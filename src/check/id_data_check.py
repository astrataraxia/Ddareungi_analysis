import pandas as pd
import os
import glob # 파일 경로를 쉽게 다루기 위한 라이브러리

# --- 데이터 경로 설정 ---
# 실제 프로젝트 구조에 맞게 경로를 수정해주세요.
BASE_DIR = '.' # 현재 스크립트가 실행되는 위치를 기준으로 가정
DATA_DIR = os.path.join(BASE_DIR, 'data')
MASTER_FILE_PATH = os.path.join(DATA_DIR, 'bcycle_master_location.csv')
RAW_DATA_DIR = os.path.join(DATA_DIR, 'parquet', '2025') # 예시로 2023년 데이터 사용

def check_station_id_matching():
    """
    따릉이 원본 데이터와 마스터 데이터 간의 대여소 ID 매칭률을 확인합니다.
    """
    print("--- 대여소 ID 매칭률 검증 시작 ---")

    # --- 1. 대여소 마스터 데이터 로드 ---
    try:
        master_df = pd.read_csv(MASTER_FILE_PATH, encoding='cp949') # encoding 확인 필요
        master_ids = set(master_df['대여소_ID'].str.strip().dropna().unique())
        print(f"✅ 마스터 데이터 로드 성공: 총 {len(master_ids):,}개의 고유 대여소 ID")
    except FileNotFoundError:
        print(f"🚨 오류: 마스터 파일을 찾을 수 없습니다. 경로: {MASTER_FILE_PATH}")
        return
    except Exception as e:
        print(f"🚨 오류: 마스터 파일 로드 중 문제 발생: {e}")
        return

    # --- 2. 원본 데이터 샘플 로드 ---
    # 2023년 폴더의 첫 번째 parquet 파일을 샘플로 사용
    try:
        sample_file = glob.glob(os.path.join(RAW_DATA_DIR, '*.parquet'))[0]
        print(f"샘플 파일: {os.path.basename(sample_file)}")
        usage_df = pd.read_parquet(sample_file)
        print(f"✅ 원본 데이터 샘플 로드 성공: {len(usage_df):,}건")
    except IndexError:
        print(f"🚨 오류: 원본 데이터 파일을 찾을 수 없습니다. 경로: {RAW_DATA_DIR}")
        return
    except Exception as e:
        print(f"🚨 오류: 원본 샘플 파일 로드 중 문제 발생: {e}")
        return

    # --- 3. 원본 데이터의 대여소 ID 추출 ---
    # 시작 대여소 ID와 종료 대여소 ID를 모두 추출
    start_ids = usage_df['시작_대여소_ID'].dropna().unique()
    # 종료 대여소 ID 중 'X'와 같은 특이값을 제외
    end_ids = usage_df[~usage_df['종료_대여소_ID'].isin(['X', None])]['종료_대여소_ID'].dropna().unique()
    
    # 두 ID 목록을 합쳐 고유한 전체 ID 목록 생성
    usage_ids = set(start_ids) | set(end_ids)
    print(f"✅ 원본 데이터에서 {len(usage_ids):,}개의 고유 대여소 ID 추출")

    # --- 4. 매칭률 계산 및 불일치 ID 확인 ---
    # 마스터 ID와 원본 ID의 교집합 (성공적으로 매칭된 ID)
    matched_ids = master_ids.intersection(usage_ids)
    
    # 원본 데이터에는 있지만 마스터 데이터에는 없는 ID (매칭 실패)
    unmatched_ids = usage_ids - master_ids
    
    # 마스터 데이터에는 있지만 원본 데이터(샘플)에는 없는 ID (해당 기간에 미사용)
    unused_in_sample_ids = master_ids - usage_ids

    # 매칭률 계산
    if len(usage_ids) > 0:
        matching_rate = len(matched_ids) / len(usage_ids) * 100
    else:
        matching_rate = 0

    print("\n--- 검증 결과 ---")
    print(f"📊 **매칭률**: {matching_rate:.2f}% ({len(matched_ids):,} / {len(usage_ids):,})")
    print(f"  - 마스터와 일치하는 ID: {len(matched_ids):,}개")
    print(f"  - **마스터에 없는 ID (불일치)**: {len(unmatched_ids):,}개")
    print(f"  - 샘플 기간 중 미사용 ID: {len(unused_in_sample_ids):,}개")
    
    if unmatched_ids:
        print("\n--- 마스터에 없는 ID 목록 (상위 10개) ---")
        print(list(unmatched_ids)[:10])
        # 불일치 ID가 포함된 원본 데이터 확인
        unmatched_data_sample = usage_df[
            usage_df['시작_대여소_ID'].isin(unmatched_ids) | 
            usage_df['종료_대여소_ID'].isin(unmatched_ids)
        ]
        print("\n--- 불일치 ID가 포함된 원본 데이터 샘플 ---")
        print(unmatched_data_sample.head())

# 스크립트 실행
if __name__ == '__main__':
    check_station_id_matching()