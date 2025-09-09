import pandas as pd
import os
from glob import glob

root_path = './2025'

standard_columns = [
    '기준_날짜', '집계_기준', '기준_시간대',
    '시작_대여소_ID', '시작_대여소명',
    '종료_대여소_ID', '종료_대여소명',
    '전체_건수', '전체_이용_분', '전체_이용_거리'
]

def ensure_columns(df, standard_columns):
    missing_cols = [col for col in standard_columns if col not in df.columns]
    for col in missing_cols:
        df[col] = None
    return df[standard_columns]

df_list = []

for month in range(1, 13):
    month_path = os.path.join(root_path, f'{str(month).zfill(2)}')
    csv_files = glob(os.path.join(month_path, '*.csv'))

    print(f"\n📅 [{str(month).zfill(2)}월] 처리 중... ({len(csv_files)}개 파일)")

    for idx, file_path in enumerate(sorted(csv_files), start=1):
        file_name = os.path.basename(file_path)
        print(f"  📄 [{idx}/{len(csv_files)}] {file_name} 처리 중...")
        try:
            df = pd.read_csv(file_path, encoding='cp949')
            df = ensure_columns(df, standard_columns)
            df_list.append(df)
            print(f"    ✅ 완료 (행 수: {len(df)})")
        except Exception as e:
            print(f"    ❌ 오류 발생: {file_name} → {e}")

print("\n🔗 모든 데이터 병합 중...")
merged_df = pd.concat(df_list, ignore_index=True)

print("💾 Parquet 파일 저장 중...")
merged_df.to_parquet('merged_2025.parquet', index=False)

print("🎉 모든 작업 완료! 저장된 파일: merged_2025.parquet")