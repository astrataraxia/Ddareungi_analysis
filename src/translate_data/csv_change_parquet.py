import pandas as pd
import os
import glob

def convert_csvs_to_parquet_individually():
    folder_path = './data/2025/'
    output_folder = './data/parquet/'
    os.makedirs(output_folder, exist_ok=True)

    # CSV 파일 목록 정렬
    csv_files = sorted(glob.glob(os.path.join(folder_path, '*.csv')))

    # 월별 이름 생성: 202001 ~ 202012
    for i, file in enumerate(csv_files, start=1):
        month_str = f'2025{str(i).zfill(2)}'  # 01~12
        output_file = os.path.join(output_folder, f'bycle_{month_str}.parquet')

        try:
            df = pd.read_csv(file, encoding='utf-8')
            df.to_parquet(output_file, index=False)
            print(f'✅ 저장 완료: {output_file}')
        except Exception as e:
            print(f'❌ 오류 발생: {file} → {e}')

    print(f'\n🎉 총 {len(csv_files)}개의 CSV 파일이 Parquet로 변환되었습니다.')

convert_csvs_to_parquet_individually()
