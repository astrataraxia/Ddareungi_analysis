import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# src.load_data.distance_data_load 모듈에 load_yearly_summary_data 함수가 있다고 가정합니다.
from load_data.distance_data_load import load_yearly_summary_data

# --- 페이지 기본 설정 ---
st.set_page_config(page_title="연도별 이용 시간/거리 패턴 분석", page_icon="🚴‍♀️", layout="wide")

# --- Session State 초기화 ---
if 'yearly_summary_results' not in st.session_state:
    st.session_state.yearly_summary_results = None

# --- 데이터 로딩 캐싱 함수 ---
@st.cache_data
def get_yearly_summary():
    """ yearly_detailed_summary.json 파일을 로드하고 캐싱합니다. """
    try:
        return load_yearly_summary_data()
    except FileNotFoundError:
        st.error("데이터 파일을 찾을 수 없습니다. `data/02/yearly_detailed_summary.json` 경로를 확인해주세요.")
        return pd.DataFrame()

# --- UI 구현 ---
st.title("🚴‍♀️ 연도별 이용 시간 및 거리 패턴 분석")
st.markdown("---")
st.info(
    """
    **두 개 이상의 연도**를 선택하여 따릉이 이용 패턴의 변화를 비교 분석합니다.
    - **전체 이용 패턴 변화**: 연도별 평균 이용 시간(막대)과 거리(꺾은선)의 변화 추이를 확인합니다.
    - **주중 vs 주말 패턴 비교**: 연도별로 주중과 주말의 이용 행태가 어떻게 다른지 비교합니다.
    - **시간-거리 상관관계**: 연도별 평균 데이터의 추세를 통해 시간과 거리의 연관성을 분석합니다.
    """,
    icon="💡"
)

# --- 필터 컨트롤 ---
with st.container(border=True):
    cols = st.columns([3, 1])
    
    with cols[0]:
        available_years = list(range(2020, 2026))
        selected_years = st.multiselect(
            "비교할 연도 선택 (두 개 이상)", 
            options=available_years, 
            default=[2021, 2022, 2023, 2024],
            placeholder="비교할 연도를 선택하세요"
        )
    
    with cols[1]:
        st.write("") # 버튼 수직 정렬
        if st.button("📊 연도별 패턴 분석 실행", use_container_width=True):
            if len(selected_years) < 2:
                st.error("분석을 위해 연도를 두 개 이상 선택해주세요.", icon="🚨")
                st.session_state.yearly_summary_results = None
            else:
                with st.spinner("연도별 데이터를 집계하고 분석 중입니다..."):
                    all_data = get_yearly_summary()
                    if not all_data.empty:
                        filtered_data = all_data[all_data['year'].isin(selected_years)].copy().sort_values(by='year')
                        st.session_state.yearly_summary_results = filtered_data
                    else:
                        st.session_state.yearly_summary_results = pd.DataFrame()

# --- 결과 시각화 ---
st.markdown("---")
st.subheader("📊 분석 결과")

if st.session_state.yearly_summary_results is not None:
    results_df = st.session_state.yearly_summary_results
    
    if results_df.empty:
        st.warning("선택하신 연도에 해당하는 데이터가 없습니다.")
    else:
        # --- 1. 선택 연도별 핵심 지표 ---
        st.markdown("#### 🎯 선택 연도별 핵심 지표")
        
        # 동적으로 컬럼 생성
        num_years = len(results_df)
        cols_per_row = 4 # 한 줄에 4개 연도까지 표시
        num_rows = (num_years + cols_per_row - 1) // cols_per_row

        for i in range(num_rows):
            cols = st.columns(cols_per_row)
            for j in range(cols_per_row):
                year_index = i * cols_per_row + j
                if year_index < num_years:
                    year_data = results_df.iloc[year_index]
                    year = int(year_data['year'])
                    avg_time = year_data['avg_time']
                    avg_dist = year_data['avg_distance']
                    
                    with cols[j]:
                        st.metric(
                            label=f"**{year}년** 평균 이용 시간",
                            value=f"{avg_time:.1f} 분",
                            delta=f"평균 거리: {avg_dist:,.0f} m"
                        )
        
        st.markdown("---")

        # --- 2. 시간과 거리의 상관관계 분석 ---
        st.markdown("#### 🕰️ 연도별 평균 시간-거리 상관관계 분석")

        with st.expander("ℹ️ 분석 방법 및 해석 보기"):
            st.write("""
                이 분석은 각 연도의 **평균 이용 시간**과 **평균 이용 거리** 데이터를 하나의 점으로 보고, 이 점들의 분포를 통해 두 지표 간의 연관성을 파악합니다.
                
                - **상관계수 (Pearson Correlation)**: -1부터 1 사이의 값으로, 두 변수가 얼마나 직선 관계에 가까운지를 나타냅니다.
                    - **1에 가까울수록**: 평균 이용 시간이 긴 연도는 평균 이용 거리도 긴 강한 양의 관계
                    - **-1에 가까울수록**: 평균 이용 시간이 긴 연도는 평균 이용 거리가 짧은 강한 음의 관계
                    - **0에 가까울수록**: 두 지표 간의 뚜렷한 선형 관계가 없음
                
                **주의**: 이는 연도별 '평균값의 추세'에 대한 분석이며, 개별 따릉이 이용 건의 상관관계와는 다릅니다.
            """)
        
        correlation = results_df['avg_time'].corr(results_df['avg_distance'])

        corr_cols = st.columns([1, 3])
        with corr_cols[0]:
            st.metric(label="상관계수 (Pearson)", value=f"{correlation:.4f}")
            if abs(correlation) >= 0.9:
                st.success("매우 강한 상관관계가 있습니다.")
            elif abs(correlation) >= 0.7:
                st.info("강한 상관관계가 있습니다.")
            elif abs(correlation) >= 0.4:
                st.info("어느 정도 상관관계가 있습니다.")
            else:
                st.warning("상관관계가 거의 없습니다.")

        with corr_cols[1]:
            scatter_chart = alt.Chart(results_df).mark_point(size=100, filled=True).encode(
                x=alt.X('avg_time:Q', title='평균 이용 시간 (분)', scale=alt.Scale(zero=False)),
                y=alt.Y('avg_distance:Q', title='평균 이용 거리 (m)', scale=alt.Scale(zero=False)),
                color=alt.Color('year:O', title='연도'),
                tooltip=[
                    alt.Tooltip('year:O', title='연도'),
                    alt.Tooltip('avg_time:Q', title='평균 시간(분)', format='.1f'),
                    alt.Tooltip('avg_distance:Q', title='평균 거리(m)', format=',.0f')
                ]
            ).properties(
                title='연도별 평균 시간-거리 분포'
            )

            # 회귀선 추가
            regression_line = scatter_chart.transform_regression('avg_time', 'avg_distance').mark_line(color='grey', strokeDash=[5,5])

            st.altair_chart(scatter_chart + regression_line, use_container_width=True)

        st.markdown("---")

        # --- 3. 전체 이용 패턴 변화 (Altair) ---
        st.markdown("#### 📈 전체 이용 패턴 변화")
        
        # ... (이전 코드와 동일) ...
        base = alt.Chart(results_df).encode(x=alt.X('year:O', title='연도', axis=alt.Axis(labelAngle=0)))
        bar_chart = base.mark_bar(color='darkorange', opacity=0.7).encode(
            y=alt.Y('avg_time:Q', title='평균 이용 시간 (분)', axis=alt.Axis(titleColor='darkorange')),
            tooltip=[alt.Tooltip('year:O', title='연도'), alt.Tooltip('avg_time:Q', title='평균 시간(분)', format='.1f')]
        )
        line_chart = base.mark_line(color='green', strokeWidth=2.5, point=True).encode(
            y=alt.Y('avg_distance:Q', title='평균 이용 거리 (m)', axis=alt.Axis(titleColor='green')),
            tooltip=[alt.Tooltip('year:O', title='연도'), alt.Tooltip('avg_distance:Q', title='평균 거리(m)', format='.0f')]
        )
        combined_chart = alt.layer(bar_chart, line_chart).resolve_scale(y='independent').properties(
            title='연도별 평균 이용 시간 및 거리 변화', height=400
        ).interactive()
        st.altair_chart(combined_chart, use_container_width=True)
        
        st.markdown("---")

        # --- 4. 주중 vs 주말 이용 패턴 비교 (Altair) ---
        st.markdown("#### 📅 주중 vs 주말 이용 패턴 비교")
        # ... (이전 코드와 동일, 데이터 전처리 및 차트 생성) ...
        results_df['workday_avg_time'] = results_df['weekday_avg_time'].apply(lambda x: np.mean([v for k, v in x.items() if int(k) < 5]))
        results_df['weekend_avg_time'] = results_df['weekday_avg_time'].apply(lambda x: np.mean([v for k, v in x.items() if int(k) >= 5]))
        results_df['workday_avg_dist'] = results_df['weekday_avg_distance'].apply(lambda x: np.mean([v for k, v in x.items() if int(k) < 5]))
        results_df['weekend_avg_dist'] = results_df['weekday_avg_distance'].apply(lambda x: np.mean([v for k, v in x.items() if int(k) >= 5]))
        
        time_melted = results_df.melt(id_vars=['year'], value_vars=['workday_avg_time', 'weekend_avg_time'], var_name='구분', value_name='평균 이용 시간')
        time_melted['구분'] = time_melted['구분'].map({'workday_avg_time': '주중', 'weekend_avg_time': '주말'})
        
        dist_melted = results_df.melt(id_vars=['year'], value_vars=['workday_avg_dist', 'weekend_avg_dist'], var_name='구분', value_name='평균 이용 거리')
        dist_melted['구분'] = dist_melted['구분'].map({'workday_avg_dist': '주중', 'weekend_avg_dist': '주말'})

        chart_cols = st.columns(2)
        with chart_cols[0]:
            time_bar_chart = alt.Chart(time_melted).mark_bar().encode(
                x=alt.X('year:O', title='연도', axis=alt.Axis(labelAngle=0)),
                y=alt.Y('평균 이용 시간:Q', title='평균 이용 시간 (분)'),
                color=alt.Color('구분:N', title='구분', scale=alt.Scale(domain=['주중', '주말'], range=['cornflowerblue', 'salmon'])),
                xOffset='구분:N',
                tooltip=[alt.Tooltip('year:O', title='연도'), alt.Tooltip('구분:N', title='구분'), alt.Tooltip('평균 이용 시간:Q', title='시간(분)', format='.1f')]
            ).properties(title='주중 vs 주말: 평균 이용 시간 비교', height=400).interactive()
            st.altair_chart(time_bar_chart, use_container_width=True)

        with chart_cols[1]:
            dist_bar_chart = alt.Chart(dist_melted).mark_bar().encode(
                x=alt.X('year:O', title='연도', axis=alt.Axis(labelAngle=0)),
                y=alt.Y('평균 이용 거리:Q', title='평균 이용 거리 (m)'),
                color=alt.Color('구분:N', title='구분', scale=alt.Scale(domain=['주중', '주말'], range=['cornflowerblue', 'salmon'])),
                xOffset='구분:N',
                tooltip=[alt.Tooltip('year:O', title='연도'), alt.Tooltip('구분:N', title='구분'), alt.Tooltip('평균 이용 거리:Q', title='거리(m)', format='.0f')]
            ).properties(title='주중 vs 주말: 평균 이용 거리 비교', height=400).interactive()
            st.altair_chart(dist_bar_chart, use_container_width=True)

else:
    st.info("위 필터에서 비교할 연도를 선택하고 '연도별 패턴 분석 실행' 버튼을 눌러주세요.")