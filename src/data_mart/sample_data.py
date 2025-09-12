from src.load_data.data_load import load_parquet_year_data

df = load_parquet_year_data([2020])

for i in df:
    sample_df = i.sample(n=50, random_state=42)  # random_state는 재현 가능성을 위해 설정
    sample_df.to_parquet("sampledata.parquet", index=False)
    break
    
