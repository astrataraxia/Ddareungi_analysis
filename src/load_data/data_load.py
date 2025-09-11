import glob
import pandas as pd
import pyarrow.parquet as pq
import os
import numbers


def load_parquet_year_data(selected_years, columns=None, chunk_size=100_000):
    if isinstance(selected_years, numbers.Number):
        selected_years = [selected_years]

    target_files = []
    for year in selected_years:
        year_folder = os.path.join('data', 'parquet', str(year))
        file_pattern = os.path.join(year_folder, '*.parquet')
        monthly_files = sorted(glob.glob(file_pattern))
        target_files.extend(monthly_files)

    # 2. 타겟팅된 파일들에 대해서만 스트리밍을 수행합니다.
    for file in target_files:
        try:
            parquet_file = pq.ParquetFile(file)
            for batch in parquet_file.iter_batches(batch_size=chunk_size, columns=columns):
                yield batch.to_pandas()
        except Exception:
            continue

def load_parquet_month_data(year, month, columns=None, chunk_size=100_000):
    year_folder = os.path.join('data', 'parquet', str(year))
    file = os.path.join(year_folder, f'bycle_{year}{month:02d}.parquet')
    return pd.read_parquet(file, columns=columns)

def load_station_data(file_path):
    return pd.read_csv(file_path, encoding='cp949')


def load_population_data(file_path):
    """
    다중 헤더를 가진 인구 데이터 CSV를 로드하고, 컬럼 이름의 공백을 정리합니다.
    """
    df = pd.read_csv(file_path, header=[0, 1])

    # 2. 컬럼 이름의 공백을 제거하는 로직
    cleaned_columns = []
    for col_level1, col_level2 in df.columns:
        # 각 레벨의 문자열 앞뒤 공백(whitespace)을 제거(strip)합니다.
        cleaned_level1 = str(col_level1).strip()
        cleaned_level2 = str(col_level2).strip()
        cleaned_columns.append((cleaned_level1, cleaned_level2))
    
    df.columns = pd.MultiIndex.from_tuples(cleaned_columns)
    
    return df