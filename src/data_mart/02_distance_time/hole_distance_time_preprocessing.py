import pandas as pd
import pathlib
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 경로 설정
try:
    BASE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent
except NameError:
    # 대화형 환경 (예: Jupyter)에서 실행될 경우를 대비
    BASE_DIR = pathlib.Path('.').resolve()

DATA_DIR = BASE_DIR / "data"
SOURCE_DIR = DATA_DIR / "parquet"
TARGET_DIR = DATA_DIR / "02"

# 대상 디렉터리 생성 (이미 존재하면 무시)
TARGET_DIR.mkdir(exist_ok=True)

# 불러올 컬럼 정의
COLUMNS_TO_LOAD = [
    "기준_날짜",
    "전체_이용_분",
    "전체_이용_거리",
]

def process_and_clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """데이터프레임에 정제 및 변환 로직을 적용합니다."""
    
    # 1. 주요 컬럼에 null 값이 있는 행 제거
    df_processed = df.dropna(subset=["전체_이용_분", "전체_이용_거리"]).copy()

    # 2. 이용 시간이 0 이하인 데이터 제거
    initial_rows = len(df_processed)
    df_processed = df_processed[df_processed["전체_이용_분"] > 0]
    
    rows_dropped = initial_rows - len(df_processed)
    if rows_dropped > 0:
        logging.info(f"{rows_dropped} rows with non-positive usage time removed.")

    # 3. 기준_날짜를 datetime으로 변환하고 요일 컬럼 추가 후, 기준_날짜 제거
    try:
        df_processed['기준_날짜'] = pd.to_datetime(df_processed['기준_날짜'], format='%Y%m%d', errors='coerce')
        df_processed.dropna(subset=['기준_날짜'], inplace=True)
        
        # 요일 컬럼 추가 (월요일=0, 일요일=6)
        df_processed['요일'] = df_processed['기준_날짜'].dt.dayofweek
        
        # 원본 기준_날짜 컬럼 제거
        df_processed.drop(columns=['기준_날짜'], inplace=True)

        logging.info("Added '요일' column and removed '기준_날짜' column.")
    except Exception as e:
        logging.error(f"Error during date conversion: {e}")

    return df_processed

def process_year(year: int):
    """단일 연도의 데이터를 처리합니다: 불러오기, 정제, 저장."""
    logging.info(f"Processing data for {year}...")
    year_source_dir = SOURCE_DIR / str(year)
    
    if not year_source_dir.exists():
        logging.warning(f"Source directory for year {year} not found. Skipping.")
        return

    all_files = list(year_source_dir.glob("*.parquet"))
    if not all_files:
        logging.warning(f"No parquet files found for year {year}. Skipping.")
        return
    
    try:
        df = pd.concat(
            (pd.read_parquet(f, columns=COLUMNS_TO_LOAD) for f in all_files),
            ignore_index=True
        )
        logging.info(f"Loaded {len(df)} rows for {year}.")
    except ValueError as e:
        logging.error(f"Could not read parquet files for year {year}. Error: {e}")
        return

    # 데이터 정제 및 변환
    df_processed = process_and_clean_data(df)
    logging.info(f"Processed and cleaned data for {year}, resulting in {len(df_processed)} rows.")
    
    # 정제된 데이터 저장
    output_path = TARGET_DIR / f"distance_time_{year}.parquet"
    df_processed.to_parquet(output_path, index=False)
    logging.info(f"Successfully saved processed data for {year} to {output_path}")

def main():
    """2020년부터 2025년까지 모든 연도의 데이터에 대한 ETL 프로세스를 실행합니다."""
    logging.info("Starting ETL process for time and distance data...")
    for year in range(2020, 2026):
        process_year(year)
    logging.info("ETL process finished.")

if __name__ == "__main__":
    main()
