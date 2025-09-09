import pandas as pd
import os

folder_path = './2020'
file_names = [f'tpss_bcycl_od_statnhm_2020{str(i).zfill(2)}.csv' for i in range(1, 13)]

standard_columns = [
    '기준_날짜', '집계_기준', '기준_시간대',
    '시작_대여소_ID', '시작_대여소명',
    '종료_대여소_ID', '종료_대여소명',
    '전체_건수', '전체_이용_분', '전체_이용_거리'
]

df_list = []

for idx, file_name in enumerate(file_names, start=1):
    file_path = os.path.join(folder_path, file_name)
    print(f"📂 [{idx}/12] 파일 처리 중: {file_name}")
    try:
        df = pd.read_csv(file_path, encoding='cp949')
        df.columns = standard_columns
        df_list.append(df)
        print(f"✅ 완료: {file_name} (행 수: {len(df)})")
    except Exception as e:
        print(f"❌ 오류 발생: {file_name} → {e}")

print("🔗 모든 파일 병합 중...")
merged_df = pd.concat(df_list, ignore_index=True)

print("💾 Parquet 파일 저장 중...")
merged_df.to_parquet('merged_2020.parquet', index=False)

print("🎉 모든 작업 완료! 저장된 파일: merged_2020.parquet")