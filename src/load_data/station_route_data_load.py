import pandas as pd
import os

def load_station_summary_data():
    file_path = os.path.join('data', '03', 'station_summary.parquet')
    
    if not os.path.exists(file_path):
        print(f"Warning: 대여소 요약 데이터 파일을 찾을 수 없습니다: {file_path}")
        print("ETL 스크립트(build_summary_data.py)를 먼저 실행해주세요.")
        return pd.DataFrame()
        
    try:
        df = pd.read_parquet(file_path)
        print(f"✅ 대여소 요약 데이터 로드 성공: {len(df):,}개 대여소")
        return df
    except Exception as e:
        print(f"Error: 대여소 요약 데이터 로드 중 오류 발생: {e}")
        return pd.DataFrame()


def load_route_summary_data():
    file_path = os.path.join('data', '03', 'route_summary.parquet')
    
    if not os.path.exists(file_path):
        print(f"Warning: 경로 요약 데이터 파일을 찾을 수 없습니다: {file_path}")
        print("ETL 스크립트(build_summary_data.py)를 먼저 실행해주세요.")
        return pd.DataFrame()
        
    try:
        df = pd.read_parquet(file_path)
        print(f"✅ 경로 요약 데이터 로드 성공: {len(df):,}개 경로")
        return df
    except Exception as e:
        print(f"Error: 경로 요약 데이터 로드 중 오류 발생: {e}")
        return pd.DataFrame()