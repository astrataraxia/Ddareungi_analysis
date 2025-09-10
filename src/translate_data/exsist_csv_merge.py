import pandas as pd
import glob
import os

# 병합할 CSV 파일들이 있는 디렉토리 경로
def exist_csv_merge():
    folder_path = './2022/07/'
    output_file = './merged.csv'

    # 해당 폴더 내의 모든 CSV 파일 경로 가져오기
    csv_files = glob.glob(os.path.join(folder_path, '*.csv'))

    # CSV 파일들을 읽어서 하나의 데이터프레임으로 병합
    merged_df = pd.concat([pd.read_csv(file, encoding ='cp949') for file in csv_files], ignore_index=True)

    # 병합된 데이터프레임을 새로운 CSV 파일로 저장
    merged_df.to_csv(output_file, index=False, encoding='utf-8-sig')

    print(f'총 {len(csv_files)}개의 파일이 병합되어 {output_file}로 저장되었습니다.')



standard_columns = [
    '기준_날짜', '집계_기준', '기준_시간대',
    '시작_대여소_ID', '시작_대여소명',
    '종료_대여소_ID', '종료_대여소명',
    '전체_건수', '전체_이용_분', '전체_이용_거리'
]

# CSV 파일 경로 설정
folder_path = './monthly_data_2022/merged_202207.csv'
output_file = './merged_cleaned_202207.csv'
csv_files = glob.glob(os.path.join(folder_path))

# 병합할 데이터프레임 리스트
merged_data = []

df = pd.read_csv(folder_path)

# 기존 컬럼 재정렬 및 이름 변경
new_df = pd.DataFrame()

# 매핑: 기존 컬럼 → 표준 컬럼
new_df['기준_날짜'] = df.iloc[:, 0]
new_df['집계_기준'] = ''  # 빈 값 채우기
new_df['기준_시간대'] = df.iloc[:, 1]
new_df['시작_대여소_ID'] = df.iloc[:, 2]
new_df['시작_대여소명'] = ''  # 빈 값 채우기
new_df['종료_대여소_ID'] = df.iloc[:, 3]
new_df['종료_대여소명'] = ''  # 빈 값 채우기
new_df['전체_건수'] = df.iloc[:, 4]  # 원래 값 사용
new_df['전체_이용_분'] = df.iloc[:, 5]
new_df['전체_이용_거리'] = df.iloc[:, 6]

# 컬럼 순서 맞추기
new_df = new_df[standard_columns]

# 저장
new_df.to_csv(output_file, index=False, encoding='utf-8-sig')
print(f'파일이 {output_file}로 저장되었습니다.')