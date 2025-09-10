import pandas as pd
import os
import glob
import time

# --- 설정 (Configuration) ---
YEAR_TO_PROCESS = 2022
SOURCE_BASE_FOLDER = f'./{YEAR_TO_PROCESS}'
OUTPUT_FOLDER = f'./monthly_data_{YEAR_TO_PROCESS}'

standard_columns = [
    '기준_날짜', '집계_기준', '기준_시간대',
    '시작_대여소_ID', '시작_대여소명',
    '종료_대여소_ID', '종료_대여소명',
    '전체_건수', '전체_이용_분', '전체_이용_거리'
]

def process_and_merge_monthly_files():
    """
    월별 하위 폴더의 일별 파일을 월별로 병합합니다.
    7개/10개 컬럼 파일을 모두 처리하며 모든 데이터를 보존합니다.
    """
    start_time = time.time()
    print(f"--- 📅 {YEAR_TO_PROCESS}년 일별 데이터 → 월별 데이터 병합 시작 ---")
    
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    print(f"결과 저장 폴더: {OUTPUT_FOLDER}\n")

    for month in range(1, 13):
        month_str = str(month).zfill(2)
        print(f"--- 📄 {month_str}월 데이터 처리 중 ---")

        monthly_source_folder = os.path.join(SOURCE_BASE_FOLDER, month_str)
        file_pattern = os.path.join(monthly_source_folder, '*.csv')
        daily_files = sorted(glob.glob(file_pattern))

        if not daily_files:
            print(f"  ⏩ {monthly_source_folder} 폴더에 파일이 없습니다. 건너뜁니다.")
            continue

        monthly_df_list = []
        print(f"  총 {len(daily_files)}개의 일별 파일을 찾았습니다.")

        for file_path in daily_files:
            file_name = os.path.basename(file_path)
            try:
                # 먼저 컬럼 개수만 확인
                with open(file_path, 'r', encoding='cp949') as f:
                    num_columns = len(f.readline().split(','))

                # --- 핵심 로직: 컬럼 개수에 따라 다르게 처리 ---
                if num_columns == 10:
                    # 10개 컬럼: 헤더와 함께 데이터를 읽고, 컬럼 이름만 표준으로 교체
                    df = pd.read_csv(file_path, encoding='cp949')
                    df.columns = standard_columns # 데이터 보존, 이름만 변경
                
                elif num_columns == 7:
                    # 7개 컬럼: 헤더와 함께 데이터를 읽고, 빠진 컬럼을 추가 후 재정렬
                    df = pd.read_csv(file_path, encoding='cp949')
                    
                    # 1. 빠진 3개의 컬럼을 'None'으로 채워서 새로 생성
                    df['집계_기준'] = None
                    df['시작_대여소명'] = None
                    df['종료_대여소명'] = None
                    
                    # 2. standard_columns 순서에 맞게 모든 컬럼을 재정렬
                    #    이 과정에서 데이터는 그대로 유지됩니다.
                    df = df.reindex(columns=standard_columns)
                    
                else:
                    print(f"    - ⚠️ 경고: {file_name}의 컬럼 수가 7 또는 10이 아닙니다. 건너뜁니다.")
                    continue
                
                monthly_df_list.append(df)

            except Exception as e:
                print(f"    - ❌ 오류: {file_name} 처리 중 문제 발생 → {e}")
        
        print(f"  {len(monthly_df_list)}개 파일 처리 완료.")

        if not monthly_df_list:
            print(f"  ⏩ 처리할 유효한 파일이 없어 {month_str}월 파일 생성을 건너뜁니다.")
            continue
            
        print(f"  🔗 {month_str}월 데이터 병합 중...")
        monthly_df = pd.concat(monthly_df_list, ignore_index=True)

        output_filename = f'merged_{YEAR_TO_PROCESS}{month_str}.csv'
        output_filepath = os.path.join(OUTPUT_FOLDER, output_filename)
        
        monthly_df.to_csv(output_filepath, index=False, encoding='utf-8-sig')
        print(f"  ✅ 저장 완료: {output_filename} (총 {len(monthly_df)} 행, {len(monthly_df.columns)} 열)")
        print("-" * 30)

    end_time = time.time()
    print(f"\n🎉 모든 작업 완료! 총 소요 시간: {end_time - start_time:.2f}초")

if __name__ == "__main__":
    process_and_merge_monthly_files()