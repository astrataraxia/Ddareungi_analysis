import streamlit as st
import pandas as pd
import altair as alt # altair 임포트
import os

from load_data.data_load import load_population_data
from load_data.summary_data_load import load_summary_monthly_data

# --- 페이지 기본 설정 ---
st.set_page_config(page_title="인구-따릉이 수요 상관관계 분석", page_icon="🔗", layout="wide")


@st.cache_data
def get_correlation_analysis_data():
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

    merged_df = pd.merge(rental_df, population_df, on='연도')
    merged_df.sort_values(by='연도', inplace=True)

    merged_df['대여건수_증감률'] = merged_df['총_대여건수'].pct_change() * 100
    merged_df['인구수_증감률'] = merged_df['총_인구수'].pct_change() * 100
    
    print("\n✅ 단계 3: 데이터 통합 및 증감률 계산 완료")
    final_df = merged_df[merged_df['연도'] >= 2021].copy()
    
    return final_df

def create_altair_correlation_chart(df):

    base = alt.Chart(df).encode(
        x=alt.X('연도:O', title='연도', axis=alt.Axis(labelAngle=0, ticks=False, domain=False))
    )

    bar_chart = base.mark_bar(color='skyblue', size=40, opacity=0.8).encode(
        y=alt.Y('대여건수_증감률:Q', 
                title='따릉이 대여건수 증감률 (%)',
                axis=alt.Axis(titleColor='skyblue', grid=True, format='.0f'),
                scale=alt.Scale(domain=[-10, 40])
               ),
        tooltip=[
            alt.Tooltip('연도:O', title='연도'),
            alt.Tooltip('대여건수_증감률:Q', title='대여 증감률', format='.2f')
        ]
    )
    
    line_chart = base.mark_line(color='tomato', strokeWidth=3, point=alt.OverlayMarkDef(color="tomato", size=60)).encode(
        y=alt.Y('인구수_증감률:Q',
                title='서울시 인구수 증감률 (%)',
                axis=alt.Axis(titleColor='tomato', grid=False, format='.1f'),
                scale=alt.Scale(domain=[-10, 40])
               ),
        tooltip=[
            alt.Tooltip('연도:O', title='연도'),
            alt.Tooltip('인구수_증감률:Q', title='인구 증감률', format='.2f')
        ]
    )

    combined_chart = alt.layer(bar_chart, line_chart).resolve_scale(
        y='independent'
    ).properties(
        title='연도별 따릉이 수요 및 서울시 인구 증감률 비교',
        height=500
    ).configure_title(
        fontSize=18
    )
    
    return combined_chart

def create_altair_scatter_chart(df):
    # 기본 차트 및 산점도(mark_point) 설정
    scatter_plot = alt.Chart(df).mark_point(
        size=150,       # 점 크기
        opacity=0.8,    # 투명도
        filled=True,    # 점 내부 채우기
        color='crimson' # 색상
    ).encode(
        x=alt.X('인구수_증감률:Q', title='서울시 인구수 증감률 (%)',
                scale=alt.Scale(zero=False) # x축이 0에서 시작하지 않도록 설정
               ),
        y=alt.Y('대여건수_증감률:Q', title='따릉이 대여건수 증감률 (%)'),
        tooltip=[
            alt.Tooltip('연도:O', title='연도'),
            alt.Tooltip('인구수_증감률:Q', title='인구 증감률', format='.2f'),
            alt.Tooltip('대여건수_증감률:Q', title='대여 증감률', format='.2f')
        ]
    )

    # transform_regression을 이용해 추세선 추가
    regression_line = scatter_plot.transform_regression(
        '인구수_증감률', '대여건수_증감률'
    ).mark_line(
        color='blue',
        strokeDash=[5, 5] # 점선 스타일
    )
    
    # 산점도와 추세선을 레이어로 결합
    final_chart = (scatter_plot + regression_line).properties(
        title='인구 증감률과 따릉이 대여 증감률의 상관관계',
        height=500
    ).configure_title(
        fontSize=18
    )
    
    return final_chart

# --- 메인 페이지 구성 ---
st.title("🔗 연도별 따릉이 수요와 서울시 인구 상관관계 분석")
st.markdown("---")
st.info("연도별 따릉이 총 이용 건수의 증감률과 서울시 인구 증감률을 비교하여 두 지표 간의 거시적인 연관성을 분석합니다.")

final_df = get_correlation_analysis_data()

if not final_df.empty:
    # 1. 분석 결과 요약 (이전과 동일)
    st.subheader("🔬 분석 결과 요약")
    correlation = final_df['대여건수_증감률'].corr(final_df['인구수_증감률'])
    st.metric(label=f"피어슨 상관계수 ({int(final_df['연도'].min())}년~)", value=f"{correlation:.4f}")
    # (상관계수 해석 텍스트는 이전과 동일)
    # ...

    st.markdown("---")
    
    # --- 2. 시각화 ---
    st.subheader("📈 증감률 변화 추이 시각화")

    # --- 💡 2-1. [개선] 연도별 증감률을 명확하게 표시 ---
    num_years = len(final_df)
    metric_cols = st.columns(num_years)

    for i, col in enumerate(metric_cols):
        year_data = final_df.iloc[i]
        year = int(year_data['연도'])
        rental_growth = year_data['대여건수_증감률']
        pop_growth = year_data['인구수_증감률']
        
        with col:
            # st.metric 대신 st.markdown을 사용하여 UI를 직접 구성
            st.markdown(f"<h5>{year}년</h5>", unsafe_allow_html=True)
            
            # 따릉이 증감률: 차트의 막대그래프 색상(skyblue)과 맞춤
            st.markdown(
                f"""
                <div style="font-size: 1rem; color: #b0c4de;">따릉이 증감률</div>
                <div style="font-size: 1.75rem; font-weight: 600; color: skyblue;">
                    {rental_growth:+.2f}%
                </div>
                """, unsafe_allow_html=True
            )
            
            # 인구 증감률: 차트의 꺾은선 색상(tomato)과 맞춤
            st.markdown(
                f"""
                <div style="font-size: 1rem; color: #b0c4de; margin-top: 10px;">인구 증감률</div>
                <div style="font-size: 1.75rem; font-weight: 600; color: tomato;">
                    {pop_growth:+.2f}%
                </div>
                """, unsafe_allow_html=True
            )
    
    st.write("")

    # --- 2-2. Altair 차트 시각화 ---
    correlation_chart = create_altair_correlation_chart(final_df)
    st.altair_chart(correlation_chart, use_container_width=True)

    # --- 3. 상관관계 산점도 시각화 --
    st.subheader("🔗 상관관계 직접 확인 (산점도)")
    scatter_chart = create_altair_scatter_chart(final_df)
    st.altair_chart(scatter_chart, use_container_width=True)

    # 4. 상세 데이터
    with st.expander("📄 상세 데이터 보기"):
        st.dataframe(final_df)
else:
    st.error("데이터가 부족하여 상관관계 분석을 실행할 수 없습니다.")
