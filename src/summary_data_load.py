import pandas as pd
import os
from typing import List, Tuple

SUMMARY_DATA_DIR = 'data/summary'

def load_summary_monthly_data(selected_years: Tuple[int, ...]) -> pd.DataFrame:
    df_list = []
    
    for year in selected_years:
        file_path = os.path.join(SUMMARY_DATA_DIR, f'summary_monthly_{year}.parquet')
        
        if os.path.exists(file_path):
            df = pd.read_parquet(file_path)
            df_list.append(df)
        else:
            print(f"Warning: {file_path} not found. Skipping.")

    if not df_list:
        # 데이터가 없을 경우, 빈 DataFrame을 올바른 구조로 반환하여 에러 방지
        return pd.DataFrame(columns=['year', 'month', 'total_rentals'])
    
    # 모든 연도의 데이터를 하나로 합칩니다.
    return pd.concat(df_list, ignore_index=True)


def load_summary_daily_data(selected_years: Tuple[int, ...], selected_month: int, selected_day: int) -> pd.DataFrame:
    df_list = []

    for year in selected_years:
        file_path = os.path.join(SUMMARY_DATA_DIR, f'summary_daily_hourly_{year}.parquet')
        
        if os.path.exists(file_path):
            df = pd.read_parquet(file_path)
            
            filtered_df = df[
                (df['month'] == selected_month) &
                (df['day'] == selected_day)
            ]
            
            if not filtered_df.empty:
                df_list.append(filtered_df)
        else:
            print(f"Warning: {file_path} not found. Skipping.")

    if not df_list:
        return pd.DataFrame(columns=['year', 'month', 'day', 'hour', 'total_rentals'])

    return pd.concat(df_list, ignore_index=True)
