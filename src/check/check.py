from src.load_data.summary_data_load import load_summary_monthly_data
from src.load_data.data_load import load_population_data

yearly_rentals = []
for year in range(2020, 2025):
    monthly_df = load_summary_monthly_data([year])
    if monthly_df is not None and not monthly_df.empty:
        total_rentals_for_year = monthly_df['total_rentals'].sum()
        yearly_rentals.append({'연도': year, '총_대여건수': total_rentals_for_year})

print(yearly_rentals)
previous_rentals = int(yearly_rentals[0]['총_대여건수'])
print(f"{yearly_rentals[0]['연도']}년: {previous_rentals:,.0f} 건 (증감률: 0.00%)")

for i in range(1, len(yearly_rentals)):
    current_rentals = int(yearly_rentals[i]['총_대여건수'])
    
    # 증감률 계산 공식: ((현재값 - 이전값) / 이전값) * 100
    if previous_rentals > 0:
        growth_rate = ((current_rentals - previous_rentals) / previous_rentals) * 100
    else:
        growth_rate = 0.0

    print(f"{yearly_rentals[i]['연도']}년: {current_rentals:,.0f} 건 (증감률: {growth_rate:+.2f}%)")
    
    # 다음 계산을 위해 현재값을 이전값 변수에 저장
    previous_rentals = current_rentals


population_raw_df = load_population_data()

if population_raw_df is None:
    print("🚨 서울시 인구 데이터가 없어 분석을 중단합니다.")

population_raw_df.columns = population_raw_df.columns.get_level_values(0)

seoul_pop_df = population_raw_df[population_raw_df['동별(2)'] == '소계'].copy()

yearly_population = []

for year in range(2020, 2026):
    year_str = str(year)
    q4_col = f'{year_str}'
    
    if year_str in seoul_pop_df.columns:
        pop_value = seoul_pop_df[year_str].iloc[0]
    elif q4_col in seoul_pop_df.columns:
        pop_value = seoul_pop_df[q4_col].iloc[0]
    else:
        continue 
    
    yearly_population.append({'연도': year-1, '총_인구수': pop_value})

print(yearly_population)