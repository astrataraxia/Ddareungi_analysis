import pandas as pd
import numpy as np
import os
from collections import defaultdict

from src.load_data.data_load import load_parquet_year_data, load_station_data

BASE_DIR = '.'
DATA_DIR = os.path.join(BASE_DIR, 'data')
OUTPUT_DIR = os.path.join(DATA_DIR, '03')
MASTER_FILE_PATH = os.path.join(DATA_DIR, 'bcycle_master_location.csv')
YEARS_TO_PROCESS = range(2020, 2026)


def load_and_preprocess_master_data():
    """마스터 대여소 데이터 로드 및 정리"""
    try:
        master_df = load_station_data()
        master_df.dropna(subset=['대여소_ID'], inplace=True)
        master_df['대여소_ID'] = master_df['대여소_ID'].astype(str).str.strip()

        # 주소 결측치 정리
        if '주소1' not in master_df.columns:
            master_df['주소1'] = ''
        else:
            master_df['주소1'] = master_df['주소1'].fillna('').astype(str).str.strip()

        if '주소2' not in master_df.columns:
            master_df['주소2'] = ''
        else:
            master_df['주소2'] = master_df['주소2'].fillna('').astype(str).str.strip()

        print(f"✅ 마스터 데이터 로드 완료: {len(master_df):,}개 대여소 정보")
        return master_df
    except FileNotFoundError:
        print(f"🚨 치명적 오류: 마스터 파일을 찾을 수 없습니다. 경로: {MASTER_FILE_PATH}")
        return None


def process_raw_data():
    """
    스트리밍 방식으로 연도별 parquet 데이터를 집계.
    - 대여소별 총 대여/반납 건수
    - 경로별 이용 건수
    """
    required_columns = ['시작_대여소_ID', '종료_대여소_ID', '전체_건수']
    data_generator = load_parquet_year_data(
        selected_years=list(YEARS_TO_PROCESS), columns=required_columns
    )

    rentals = defaultdict(int)
    returns = defaultdict(int)
    routes = defaultdict(int)

    print("스트리밍 방식으로 원본 데이터 처리를 시작합니다...")
    chunk_count = 0
    for chunk_df in data_generator:
        chunk_count += 1
        if chunk_count % 50 == 0:
            print(f"  - {chunk_count}개 데이터 청크 처리 중...")

        chunk_df = chunk_df.loc[:, required_columns].copy()
        chunk_df.dropna(subset=['시작_대여소_ID'], inplace=True)
        chunk_df['시작_대여소_ID'] = chunk_df['시작_대여소_ID'].astype(str).str.strip()
        chunk_df = chunk_df[chunk_df['시작_대여소_ID'].str.lower() != 'center']

        # 대여소별 대여 집계
        grp_rent = chunk_df.groupby('시작_대여소_ID')['전체_건수'].sum()
        for sid, cnt in grp_rent.items():
            rentals[sid] += int(cnt)

        # 반납/경로 집계
        valid_returns = chunk_df[
            chunk_df['종료_대여소_ID'].notnull() & (chunk_df['종료_대여소_ID'] != 'X')
        ].copy()
        if not valid_returns.empty:
            valid_returns['종료_대여소_ID'] = valid_returns['종료_대여소_ID'].astype(str).str.strip()
            valid_returns = valid_returns[valid_returns['종료_대여소_ID'].str.lower() != 'center']

            grp_ret = valid_returns.groupby('종료_대여소_ID')['전체_건수'].sum()
            for eid, cnt in grp_ret.items():
                returns[eid] += int(cnt)

            grp_route = valid_returns.groupby(['시작_대여소_ID', '종료_대여소_ID'])['전체_건수'].sum()
            for (sid, eid), cnt in grp_route.items():
                routes[(sid, eid)] += int(cnt)

    print(f"\n✅ 총 {chunk_count:,}개의 청크 처리 완료. 최종 데이터 집계를 시작합니다.")

    if not rentals:
        print("🚨 처리된 데이터가 없습니다.")
        return None, None

    # 결과 DataFrame 생성
    final_rentals = pd.DataFrame(list(rentals.items()), columns=['대여소_ID', '총_대여건수'])
    final_returns = pd.DataFrame(list(returns.items()), columns=['대여소_ID', '총_반납건수'])
    final_routes = pd.DataFrame(
        [{'시작_대여소_ID': s, '종료_대여소_ID': e, '이용_건수': cnt} for (s, e), cnt in routes.items()]
    )

    final_rentals['총_대여건수'] = final_rentals['총_대여건수'].astype('int64')
    if not final_returns.empty:
        final_returns['총_반납건수'] = final_returns['총_반납건수'].astype('int64')
    if not final_routes.empty:
        final_routes['이용_건수'] = final_routes['이용_건수'].astype('int64')

    return (final_rentals, final_returns), final_routes


def create_station_summary(station_data, master_df):
    """대여소별 이용 현황 요약 생성 (대여소명은 제외)"""
    final_rentals, final_returns = station_data

    final_rentals['대여소_ID'] = final_rentals['대여소_ID'].astype(str).str.strip()
    if not final_returns.empty:
        final_returns['대여소_ID'] = final_returns['대여소_ID'].astype(str).str.strip()
    else:
        final_returns = pd.DataFrame(columns=['대여소_ID', '총_반납건수'])

    station_summary = pd.merge(final_rentals, final_returns, on='대여소_ID', how='outer').fillna(0)
    station_summary['총_이용건수'] = station_summary['총_대여건수'] + station_summary['총_반납건수']
    station_summary['순이동량'] = station_summary['총_대여건수'] - station_summary['총_반납건수']

    master_for_merge = master_df[['대여소_ID', '주소1', '주소2', '위도', '경도']].copy()
    master_for_merge['대여소_ID'] = master_for_merge['대여소_ID'].astype(str).str.strip()

    final_station_summary = pd.merge(station_summary, master_for_merge, on='대여소_ID', how='inner')

    final_station_summary = final_station_summary[[
        '대여소_ID', '주소1', '주소2', '위도', '경도',
        '총_대여건수', '총_반납건수', '총_이용건수', '순이동량'
    ]]

    for col in ['총_대여건수', '총_반납건수', '총_이용건수', '순이동량']:
        final_station_summary[col] = final_station_summary[col].astype('int64')

    output_path = os.path.join(OUTPUT_DIR, 'station_summary.parquet')
    final_station_summary.to_parquet(output_path, index=False)
    print(f"✅ 대여소 요약 데이터 생성 완료: {len(final_station_summary):,}개 대여소 ({output_path})")


def create_route_summary(route_data, master_df):
    """경로별 이용 현황 요약 생성 (대여소명 대신 주소 사용)"""
    if route_data is None or route_data.empty:
        print("경로 데이터가 없습니다. 생략합니다.")
        return

    route_data = route_data.copy()
    route_data['시작_대여소_ID'] = route_data['시작_대여소_ID'].astype(str).str.strip()
    route_data['종료_대여소_ID'] = route_data['종료_대여소_ID'].astype(str).str.strip()

    route_data['이용_형태'] = np.where(
        route_data['시작_대여소_ID'] == route_data['종료_대여소_ID'],
        '왕복', '편도'
    )

    master_info = master_df[['대여소_ID', '주소1', '주소2', '위도', '경도']].copy()
    master_info['대여소_ID'] = master_info['대여소_ID'].astype(str).str.strip()

    final_route_summary = pd.merge(
        route_data, master_info.add_suffix('_시작'),
        left_on='시작_대여소_ID', right_on='대여소_ID_시작', how='inner'
    )
    final_route_summary = pd.merge(
        final_route_summary, master_info.add_suffix('_종료'),
        left_on='종료_대여소_ID', right_on='대여소_ID_종료', how='inner'
    )

    final_route_summary = final_route_summary[[
        '시작_대여소_ID', '종료_대여소_ID', '이용_건수', '이용_형태',
        '주소1_시작', '주소2_시작', '위도_시작', '경도_시작',
        '주소1_종료', '주소2_종료', '위도_종료', '경도_종료'
    ]]

    output_path = os.path.join(OUTPUT_DIR, 'route_summary.parquet')
    final_route_summary.to_parquet(output_path, index=False)
    print(f"✅ 경로 요약 데이터 생성 완료: {len(final_route_summary):,}개 경로 ({output_path})")


if __name__ == '__main__':
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    master_df = load_and_preprocess_master_data()

    if master_df is not None:
        station_data, route_data = process_raw_data()

        if station_data and route_data is not None:
            create_station_summary(station_data, master_df)
            create_route_summary(route_data, master_df)
            print("\n🎉 모든 데이터 처리 파이프라인이 성공적으로 완료되었습니다.")