import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from src.load_data.summary_data_load import load_summary_monthly_data
from src.load_data.data_load import load_population_data



def analyze_correlation_with_population():
    """
    연도별 따릉이 수요와 서울시 인구의 상관관계를 분석하고 시각화합니다.
    """
    print("--- 따릉이 수요-인구 상관관계 분석 시작 ---")

    # --- 1단계: 따릉이 연간 이용 데이터 집계 ---
    yearly_rentals = []
    for year in range(2020, 2025):
        monthly_df = load_summary_monthly_data([year])
        if monthly_df is not None and not monthly_df.empty:
            total_rentals_for_year = monthly_df['total_rentals'].sum()
            yearly_rentals.append({'연도': year, '총_대여건수': total_rentals_for_year})
    
    if not yearly_rentals:
        print("🚨 따릉이 월별 요약 데이터가 없어 분석을 중단합니다.")
        return
        
    rental_df = pd.DataFrame(yearly_rentals)
    print("\n✅ 단계 1: 따릉이 연간 이용량 집계 완료")
    print(rental_df)

    # --- 2단계: 서울시 연간 인구 데이터 전처리 ---
    population_raw_df = load_population_data()
    if population_raw_df is None: return

    population_raw_df.columns = population_raw_df.columns.get_level_values(0)
    seoul_pop_df = population_raw_df[population_raw_df['동별(2)'] == '소계'].copy()
    
    yearly_population = []
    for year in range(2020, 2026):
        year_str = str(year)
        if year_str in seoul_pop_df.columns:
            pop_value = seoul_pop_df[year_str].iloc[0]
            yearly_population.append({'연도': year-1, '총_인구수': pop_value})
        else:
            continue
            

    population_df = pd.DataFrame(yearly_population)
    print("\n✅ 단계 2: 서울시 연간 인구 데이터 전처리 완료")
    print(population_df)

    # --- 3단계: 데이터 통합 및 증감률 계산 ---
    merged_df = pd.merge(rental_df, population_df, on='연도')
    merged_df.sort_values(by='연도', inplace=True)

    merged_df['대여건수_증감률'] = merged_df['총_대여건수'].pct_change() * 100
    merged_df['인구수_증감률'] = merged_df['총_인구수'].pct_change() * 100
    
    print("\n✅ 단계 3: 데이터 통합 및 증감률 계산 완료 (전처리 전)")
    print(merged_df[['연도', '대여건수_증감률', '인구수_증감률']])
    
    # --- 💡 4. 증감률 데이터 최종 정리 (2021년부터 시작) ---
    final_df = merged_df[merged_df['연도'] >= 2021].copy()

    print("\n✅ 단계 4: 최종 분석용 데이터 (2021년~)")
    print(final_df[['연도', '대여건수_증감률', '인구수_증감률']])

    # --- 5단계: 상관관계 분석 및 시각화 ---
    correlation = final_df['대여건수_증감률'].corr(final_df['인구수_증감률'])
    
    print("\n" + "="*50)
    print("🔬 최종 분석 결과")
    print("="*50)
    print(f"📈 피어슨 상관계수 (2021년~): {correlation:.4f}")

    fig, ax1 = plt.subplots(figsize=(12, 7))

    years = final_df['연도']

    # --- 좌측 Y축: 대여건수 증감률 (막대) ---
    color_bar = 'skyblue'
    ax1.bar(years, final_df['대여건수_증감률'], color=color_bar, label='따릉이 대여건수 증감률 (%)', width=0.6, alpha=0.8)
    ax1.set_xlabel('연도', fontsize=12)
    ax1.set_ylabel('대여건수 증감률 (%)', color=color_bar, fontsize=12)
    ax1.tick_params(axis='y', labelcolor=color_bar)

    ax1.set_ylim(-10, 40)
    ax1.axhline(0, color=color_bar, linestyle='--', linewidth=1, alpha=0.5)


    # --- 우측 Y축: 인구수 증감률 (꺾은선) ---
    ax2 = ax1.twinx()
    color_line = 'tomato'
    ax2.plot(years, final_df['인구수_증감률'], color=color_line, marker='o', linestyle='-', label='서울시 인구수 증감률 (%)', linewidth=2.5)
    ax2.set_ylabel('인구수 증감률 (%)', color=color_line, fontsize=12)
    ax2.tick_params(axis='y', labelcolor=color_line)

    ax2.set_ylim(-10, 40) 
    ax2.axhline(0, color=color_line, linestyle='--', linewidth=1, alpha=0.5)

    # --- 최종 차트 정리 ---
    plt.title('연도별 따릉이 수요 및 서울시 인구 증감률 비교', fontsize=16)
    fig.legend(loc="upper right", bbox_to_anchor=(0.9, 0.9), bbox_transform=ax1.transAxes)
    ax1.set_xticks(years)
    # Y축 그리드를 추가하여 가독성 향상
    ax1.grid(True, axis='y', linestyle=':', alpha=0.6)

    # --- 6단계 (추가): 산점도를 이용한 직접적인 상관관계 시각화 ---
    fig2, ax2 = plt.subplots(figsize=(10, 8))

    # 산점도 그리기
    ax2.scatter(final_df['인구수_증감률'], final_df['대여건수_증감률'], 
                s=150, c='crimson', alpha=0.7, edgecolors='black', label='연도별 데이터')

    # 각 점에 연도 표시
    for i, txt in enumerate(final_df['연도']):
        ax2.annotate(txt, (final_df['인구수_증감률'].iloc[i]+0.01, final_df['대여건수_증감률'].iloc[i]))

    # 추세선(회귀선) 그리기
    z = np.polyfit(final_df['인구수_증감률'], final_df['대여건수_증감률'], 1)
    p = np.poly1d(z)
    ax2.plot(final_df['인구수_증감률'], p(final_df['인구수_증감률']), "b--", alpha=0.8, label='추세선')

    ax2.set_title('서울시 인구 증감률과 따릉이 대여 증감률의 상관관계', fontsize=16)
    ax2.set_xlabel('인구수 증감률 (%)', fontsize=12)
    ax2.set_ylabel('따릉이 대여건수 증감률 (%)', fontsize=12)
    ax2.grid(True, linestyle='--', alpha=0.6)
    ax2.legend()

    plt.show()
    


if __name__ == '__main__':
    plt.rc('font', family='NanumGothic')
    plt.rcParams['axes.unicode_minus'] = False
    analyze_correlation_with_population()
