import pandas as pd
import os

SOURCE_YEAR = 2021
SOURCE_FOLDER = f'./{SOURCE_YEAR}'

OUTPUT_FOLDER = f'./preprocessed_{SOURCE_YEAR}'
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# --- 표준 컬럼 정의 ---
standard_columns = [
    '기준_날짜', '집계_기준', '기준_시간대',
    '시작_대여소_ID', '시작_대여소명',
    '종료_대여소_ID', '종료_대여소명',
    '전체_건수', '전체_이용_분', '전체_이용_거리'
]

# 컬럼이 7개일 경우의 컬럼 순서
seven_columns = [
    '기준_날짜', '기준_시간대',
    '시작_대여소_ID', 
    '종료_대여소_ID', 
    '전체_건수', '전체_이용_분', '전체_이용_거리'
]

file_names_template = f'tpss_bcycl_od_statnhm_{SOURCE_YEAR}'
monthly_files = [f'{file_names_template}{str(month).zfill(2)}.csv' for month in range(1, 13)]

print(f"--- 💾 {SOURCE_YEAR}년 월별 데이터 개별 변환 시작 ---")
print(f"결과 저장 폴더: {OUTPUT_FOLDER}\n")

for idx, file_name in enumerate(monthly_files, start=1):
    source_file_path = os.path.join(SOURCE_FOLDER, file_name)
    
    print(f"📂 [{idx}/12] 파일 처리 시작: {file_name}")

    if not os.path.exists(source_file_path):
        print(f"  ⏩ 파일 없음. 건너뜁니다.")
        continue

    try:
        # 먼저 파일의 컬럼 개수부터 확인
        with open(source_file_path, 'r', encoding='cp949') as f:
            header_line = f.readline()
            num_columns = len(header_line.split(','))

        if num_columns == 10:
            # 컬럼이 10개인 경우, 데이터를 읽고 컬럼 이름만 재할당
            df = pd.read_csv(source_file_path, encoding='cp949')
            # --- 핵심 수정 부분 ---
            # reindex 대신, 컬럼 이름만 직접 변경하여 데이터를 보존합니다.
            df.columns = standard_columns
            
        elif num_columns == 7:
            # 컬럼이 7개인 경우, 이전의 안전한 reindex 방식을 사용
            df = pd.read_csv(source_file_path, encoding='cp949', header=None, names=seven_columns)
            df = df.reindex(columns=standard_columns) # 빠진 컬럼을 NaN으로 채움
            
        else:
            print(f"  ⚠️ 경고: 컬럼 개수가 10개 또는 7개가 아닙니다 (개수: {num_columns}). 건너뜁니다.")
            continue

        output_file_name = f'preprocessed_{file_name}'
        output_file_path = os.path.join(OUTPUT_FOLDER, output_file_name)
        
        df.to_csv(output_file_path, index=False, encoding='utf-8-sig')
        
        print(f"  ✅ 완료. 저장된 파일: {output_file_name} (행: {len(df)}, 열: {len(df.columns)})")

    except Exception as e:
        print(f"  ❌ 오류 발생: {file_name} → {e}")

print("\n🎉 모든 작업 완료!")