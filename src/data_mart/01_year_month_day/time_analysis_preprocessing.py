import pandas as pd
import os
import glob
import time
import pyarrow.parquet as pq 

# --- 설정 (Configuration) ---

# 1. 입력: 월별 Parquet 파일이 있는 기본 경로
BASE_INPUT_DIR = 'data/parquet'

# 2. 출력: 최종 요약 파일을 저장할 경로
OUTPUT_DATA_DIR = 'data/summary'

# 3. 처리할 연도 범위
YEARS_TO_PROCESS = range(2020, 2026)

# 4. 집계에 필요한 최소한의 컬럼
REQUIRED_COLUMNS = ['기준_날짜', '기준_시간대', '전체_건수']


def create_yearly_summaries_from_monthly_files(year):
    """
    지정된 연도의 모든 월별 Parquet 파일을 직접 읽어, 두 종류의 사전 집계된
    요약 파일(Data Mart)을 생성합니다.
    """
    
    # --- 1. 입력 파일 탐색 ---
    year_input_folder = os.path.join(BASE_INPUT_DIR, str(year))
    file_pattern = os.path.join(year_input_folder, f'bycle_{year}*.parquet')
    monthly_files = sorted(glob.glob(file_pattern))

    if not monthly_files:
        print(f"    ⏩ 원본 파일 없음: {year_input_folder} 폴더에 파일이 없습니다. 건너뜁니다.")
        return

    print(f"    - Step 1: 총 {len(monthly_files)}개의 월별 파일을 읽어 집계 시작...")
    
    daily_hourly_dict = {}
    monthly_dict = {}
    total_chunks_processed = 0

    # --- 2. 모든 월별 파일을 순회하며 청크 단위로 집계 ---
    for file_path in monthly_files:
        try:
            parquet_file = pq.ParquetFile(file_path)
            batch_iterator = parquet_file.iter_batches(batch_size=500_000, columns=REQUIRED_COLUMNS)

            for batch in batch_iterator:

                chunk = batch.to_pandas()

                chunk['기준_날짜'] = pd.to_datetime(chunk['기준_날짜'], format='%Y%m%d')
                chunk['year'] = chunk['기준_날짜'].dt.year
                chunk['month'] = chunk['기준_날짜'].dt.month
                chunk['day'] = chunk['기준_날짜'].dt.day
                chunk['hour'] = chunk['기준_시간대'] // 100

                # 집계 1: 일별/시간별
                daily_chunk_summary = chunk.groupby(['year', 'month', 'day', 'hour'])['전체_건수'].sum()
                for (y, m, d, h), count in daily_chunk_summary.items():
                    key = (y, m, d, h)
                    daily_hourly_dict[key] = daily_hourly_dict.get(key, 0) + count

                # 집계 2: 월별
                monthly_chunk_summary = chunk.groupby(['year', 'month'])['전체_건수'].sum()
                for (y, m), count in monthly_chunk_summary.items():
                    key = (y, m)
                    monthly_dict[key] = monthly_dict.get(key, 0) + count
                    
                total_chunks_processed += 1
                print(f"\r      총 {total_chunks_processed}개의 청크 처리 완료... ({os.path.basename(file_path)})", end="")

        except Exception as e:
            file_name = os.path.basename(file_path)
            print(f"\n    ❌ 오류: {file_name} 파일을 읽는 중 문제 발생 - {e}. 이 파일은 건너뜁니다.")
            continue

    print("\n    - Step 2: 최종 집계 결과 변환 및 저장...")
    
    # --- 결과 1: 일별/시간별 요약 파일 저장 ---
    if daily_hourly_dict:
        daily_data = []
        for (y, m, d, h), count in daily_hourly_dict.items():
            daily_data.append({'year': y, 'month': m, 'day': d, 'hour': h, 'total_rentals': count})
        daily_df = pd.DataFrame(daily_data)
        
        for col in ['year', 'month', 'day', 'hour']:
            daily_df[col] = pd.to_numeric(daily_df[col], downcast='integer')
        daily_df['total_rentals'] = pd.to_numeric(daily_df['total_rentals'], downcast='unsigned')

        output_daily_file = os.path.join(OUTPUT_DATA_DIR, f'summary_daily_hourly_{year}.parquet')
        daily_df.to_parquet(output_daily_file, index=False)
        print(f"    ✅ 일별/시간별 요약 저장 완료: {os.path.basename(output_daily_file)}")
    else:
        print("    ⚠️ 일별/시간별 요약 데이터 없음.")

    # --- 결과 2: 월별 요약 파일 저장 ---
    if monthly_dict:
        monthly_data = []
        for (y, m), count in monthly_dict.items():
            monthly_data.append({'year': y, 'month': m, 'total_rentals': count})
        monthly_df = pd.DataFrame(monthly_data)
        
        for col in ['year', 'month']:
            monthly_df[col] = pd.to_numeric(monthly_df[col], downcast='integer')
        monthly_df['total_rentals'] = pd.to_numeric(monthly_df['total_rentals'], downcast='unsigned')

        output_monthly_file = os.path.join(OUTPUT_DATA_DIR, f'summary_monthly_{year}.parquet')
        monthly_df.to_parquet(output_monthly_file, index=False)
        print(f"    ✅ 월별 요약 저장 완료: {os.path.basename(output_monthly_file)}")
    else:
        print("    ⚠️ 월별 요약 데이터 없음.")


def main():
    start_time = time.time()
    print("--- 🚀 최종 사전 집계 데이터 마트 2종 생성 시작 (월별 파일 직접 처리) ---\n")
    
    os.makedirs(OUTPUT_DATA_DIR, exist_ok=True)
    
    for year in YEARS_TO_PROCESS:
        print(f"--- 🏭 {year}년 데이터 집계 시작 ---")
        create_yearly_summaries_from_monthly_files(year)
        print("-" * 40)

    end_time = time.time()
    print(f"\n🎉 모든 작업 완료! 총 소요 시간: {end_time - start_time:.2f}초")
    print(f"집계된 최종 요약 파일들은 '{OUTPUT_DATA_DIR}' 폴더에 저장되었습니다.")

if __name__ == "__main__":
    main()