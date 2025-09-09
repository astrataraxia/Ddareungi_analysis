import glob
import pandas as pd


def load_parquet_data(file_path):
    all_files = glob.glob(file_path + "/*.parquet")
    for file in all_files:
        yield pd.read_parquet(file)


def load_station_data(file_path):
    return pd.read_csv(file_path, encoding='cp949')


def load_population_data(file_path):
    return pd.read_csv(file_path, header=[0, 1])