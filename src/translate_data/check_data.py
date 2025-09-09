import pandas as pd

df = pd.read_parquet('data/merged_2025.parquet')

df.info()

print(df.head())