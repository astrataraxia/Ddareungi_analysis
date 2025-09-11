import pandas as pd
import os
import glob
from typing import List

# 정제된 거리/시간 데이터가 저장된 디렉터리
DISTANCE_DATA_DIR = 'data/02'

def load_distance_time_data() -> pd.DataFrame:
    """
    data/02/ 폴더에 있는 정제된 distance_time parquet 파일들을 모두 불러와
    하나의 데이터프레임으로 합쳐서 반환합니다.
    """
    file_pattern = os.path.join(DISTANCE_DATA_DIR, 'distance_time_*.parquet')
    files: List[str] = glob.glob(file_pattern)
    
    if not files:
        print(f"Warning: No data files found matching pattern in {DISTANCE_DATA_DIR}")
        return pd.DataFrame()
        
    df_list = [pd.read_parquet(file) for file in files]
    
    if not df_list:
        return pd.DataFrame()

    combined_df = pd.concat(df_list, ignore_index=True)
    
    return combined_df

def load_distance_time_data_by_year(year: int) -> pd.DataFrame:
    """
    특정 연도의 distance_time 데이터를 불러옵니다.
    """
    file_path = os.path.join(DISTANCE_DATA_DIR, f'distance_time_{year}.parquet')
    
    if not os.path.exists(file_path):
        print(f"Warning: Data file for year {year} not found at {file_path}")
        return pd.DataFrame()
    
    df = pd.read_parquet(file_path)
    return df

def load_distance_time_summary_data() -> pd.DataFrame:
    file_path = os.path.join(DISTANCE_DATA_DIR, 'dis_time_summary.parquet')
    if not os.path.exists(file_path):
        print(f"Warning: Summary data file not found at {file_path}")
        return pd.DataFrame()
    df = pd.read_parquet(file_path)
    return df

def load_yearly_summary_data() -> pd.DataFrame:
    file_path = os.path.join(DISTANCE_DATA_DIR, 'yearly_detailed_summary.json')
    if not os.path.exists(file_path):
        print(f"Warning: Yearly summary data file not found at {file_path}")
        return pd.DataFrame()
    df = pd.read_json(file_path)
    return df