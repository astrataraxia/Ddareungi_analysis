import streamlit as st
import altair as alt
import pandas as pd

from src.summary_data_load import load_summary_monthly_data, load_summary_daily_data

# --- 페이지 기본 설정 ---
st.set_page_config(page_title="월간, 일별 시간대별 이용량 비교 분석", page_icon="📅", layout="wide")

# --- Session State 초기화 ---
if 'comparison_results' not in st.session_state:
    st.session_state.comparison_results = None

if 'monthly_comparison_results' not in st.session_state:
    st.session_state.monthly_comparison_results = None

# --- 데이터 분석 캐싱 함수 ---
@st.cache_data
def get_daily_rentals(years, month, day):
    return load_summary_daily_data(years, month, day)

@st.cache_data
def get_monthly_rentals(years):
    return load_summary_monthly_data(years)

# --- UI 구현 (Monthly UI) ---
st.title("📈 연도별 월간 이용량 비교 분석")
st.markdown("---")
st.info("비교하고 싶은 연도를 두 개 이상 선택하면, 연도별 월간 이용량 추이를 하나의 차트에서 비교할 수 있습니다.", icon="💡")

# --- 필터 컨트롤 ---
with st.container(border=True):
    cols = st.columns([3, 1]) # 필터와 버튼을 위한 컬럼
    
    with cols[0]:
        selected_years = st.multiselect(
            "비교할 연도 선택", 
            options=list(range(2020, 2026)), 
            default=[2023, 2024], # 기본값으로 최근 2년
            placeholder="비교할 연도를 선택하세요"
        )
    
    with cols[1]:
        st.write("") # 버튼 수직 정렬
        if st.button("📊 비교 분석 실행", use_container_width=True):
            if not selected_years:
                st.error("분석을 위해 연도를 하나 이상 선택해주세요.", icon="🚨")
                st.session_state.monthly_comparison_results = None
            else:
                with st.spinner("선택하신 연도의 월별 데이터를 집계 중입니다..."):
                    st.session_state.monthly_comparison_results = get_monthly_rentals(
                        years=tuple(sorted(selected_years))
                    )

# --- 결과 시각화 ---
st.markdown("---")
st.subheader("📊 분석 결과")

if st.session_state.monthly_comparison_results is not None:
    results_df = st.session_state.monthly_comparison_results
    
    if results_df.empty:
        st.warning("선택하신 연도에 해당하는 데이터가 없습니다.")
    else:
        # --- Altair를 사용한 다중 라인 차트 ---
        st.write("#### 연도별 월간 이용량 추이")
        
        # --- 추가: 연도별 월간 이용량 요약 메트릭 ---
        st.write("#### 연도별 요약")
        metric_cols = st.columns(3)

        # 1. 가장 많이 이용한 연도
        total_rentals_by_year = results_df.groupby('year')['total_rentals'].sum()
        year_highest_usage = int(total_rentals_by_year.idxmax()) # Ensure int
        highest_usage_value = total_rentals_by_year.max()
        with metric_cols[0]:
            st.metric(label="🥇 가장 많이 이용한 연도", value=f"{year_highest_usage}년", delta=f"{highest_usage_value:,} 건")

        # 2. 가장 많이 증가한 연도 (전년 대비)
        # 연도별 총합을 기준으로 정렬
        sorted_years_total = total_rentals_by_year.sort_index()
        # 전년 대비 증가량 계산
        yoy_increase = sorted_years_total.diff().fillna(0) # 첫 해는 증가량 0으로 처리
        
        if not yoy_increase.empty and yoy_increase.max() > 0:
            year_highest_increase = int(yoy_increase.idxmax()) # Ensure int
            highest_increase_value = yoy_increase.max()
            with metric_cols[1]:
                st.metric(label="🚀 가장 많이 증가한 연도", value=f"{year_highest_increase}년", delta=f"{int(highest_increase_value):,} 건 증가")
        else:
            with metric_cols[1]:
                st.metric(label="🚀 가장 많이 증가한 연도", value="N/A", delta="데이터 부족")

        # New section: Total rentals for each selected year
        st.write("#### 선택 연도별 총 이용 건수")
        
        # Create columns dynamically based on the number of selected years
        cols_per_row = 3
        num_years = len(total_rentals_by_year)
        num_rows = (num_years + cols_per_row - 1) // cols_per_row # Ceiling division

        for i in range(num_rows):
            current_cols = st.columns(cols_per_row)
            for j in range(cols_per_row):
                year_index = i * cols_per_row + j
                if year_index < num_years:
                    year = int(total_rentals_by_year.index[year_index]) # Ensure int
                    total_rentals = total_rentals_by_year.iloc[year_index]
                    with current_cols[j]:
                        st.metric(label=f"{year}년 총 이용 건수", value=f"{total_rentals:,} 건")

        # Altair 차트 생성
        line_chart = alt.Chart(results_df).mark_line(point=True).encode(
            x=alt.X('month:O', title='월', axis=alt.Axis(labelAngle=0)), 
            y=alt.Y('total_rentals:Q', title='총 이용 건수'), 
            color=alt.Color('year:N', title='연도'), 
            tooltip=['year', 'month', 'total_rentals'] 
        ).properties(
            height=500
        ).interactive()

        st.altair_chart(line_chart, use_container_width=True)
        
else:
    st.info("위 필터에서 비교할 연도를 선택하고 '비교 분석 실행' 버튼을 눌러주세요.")


# --- UI 구현 (Daily UI) ---
st.title("📅 특정일 시간대별 이용량 비교 분석")
st.markdown("---")
st.info(
    """
    비교하고 싶은 **여러 연도**와 **하나의 월, 일**을 선택하세요. 
    선택한 각 연도에 대해 해당 날짜의 시간대별 이용량 추이를 개별 차트로 보여줍니다.
    """, 
    icon="💡"
)

with st.container(border=True):
    cols = st.columns([2, 1, 1, 1.5])
    
    with cols[0]:
        selected_years = st.multiselect("연도 선택 (다중 선택 가능)", options=list(range(2020, 2026)), default=[], placeholder="비교할 연도를 선택하세요")
    with cols[1]:
        selected_month = st.selectbox("월 선택 (단일 선택)", options=list(range(1, 13)), format_func=lambda m: f"{m}월", placeholder="월을 선택하세요")
    with cols[2]:
        selected_day = st.selectbox("일 선택 (단일 선택)", options=list(range(1, 32)), placeholder="일을 선택하세요")
    
    with cols[3]:
        st.write("")
        if st.button("📈 비교 분석 실행", use_container_width=True):
            if not selected_years or not selected_month or not selected_day:
                st.error("분석을 위해 연도, 월, 일을 모두 선택해야 합니다.", icon="🚨")
                st.session_state.comparison_results = None
            else:
                with st.spinner("선택하신 날짜의 연도별 데이터를 분석 중입니다..."):
                    st.session_state.comparison_results = get_daily_rentals(
                        years=tuple(selected_years),
                        month=selected_month,
                        day=selected_day
                    )

# --- 결과 시각화 ---
st.markdown("---")
st.subheader("📊 분석 결과")

if st.session_state.comparison_results is not None:
    results_df = st.session_state.comparison_results
    
    if results_df.empty:
        st.warning("선택하신 조건에 해당하는 데이터가 없습니다. 다른 날짜나 연도를 선택해보세요.")
    else:
        # DataFrame에서 연도별로 데이터 분리
        sorted_years = sorted(results_df['year'].unique())
        chart_cols = st.columns(2)
        
        for i, year in enumerate(sorted_years):
            col = chart_cols[i % 2]
            with col:
                # 해당 연도의 데이터만 필터링
                hourly_df = results_df[results_df['year'] == year].copy()
                
                # 0-23시 전체 시간대 확보 (빠진 시간대가 있을 수 있으므로)
                all_hours = pd.DataFrame({'hour': range(24)})
                hourly_df = pd.merge(all_hours, hourly_df[['hour', 'total_rentals']], on='hour', how='left')
                hourly_df['total_rentals'] = hourly_df['total_rentals'].fillna(0).astype(int)
                
                if not hourly_df['total_rentals'].empty and hourly_df['total_rentals'].sum() > 0:
                    total_rentals_sum = int(hourly_df['total_rentals'].sum())
                    peak_hour_row = hourly_df.loc[hourly_df['total_rentals'].idxmax()]
                    peak_hour = int(peak_hour_row['hour'])
                    peak_rentals = int(peak_hour_row['total_rentals'])
                    
                    non_zero_rentals = hourly_df[hourly_df['total_rentals'] > 0]
                    if not non_zero_rentals.empty:
                        off_peak_hour_row = non_zero_rentals.loc[non_zero_rentals['total_rentals'].idxmin()]
                        off_peak_hour = int(off_peak_hour_row['hour'])
                    else:
                        off_peak_hour = "N/A" 
                else: 
                    total_rentals_sum = 0
                    peak_hour = "N/A"
                    off_peak_hour = "N/A"
                
                st.write(f"#### 📈 {year}년 {selected_month}월 {selected_day}일 분석 요약")
                
                metric_cols = st.columns(3)
                with metric_cols[0]:
                    st.metric(label="✅ 총 이용 건수", value=f"{total_rentals_sum:,} 건")
                with metric_cols[1]:
                    if peak_hour != "N/A":
                        st.metric(label="🔼 최고 이용 시간대 (Peak)", value=f"{peak_hour}시")
                    else:
                        st.metric(label="🔼 최고 이용 시간대 (Peak)", value="N/A")
                with metric_cols[2]:
                    if off_peak_hour != "N/A":
                        st.metric(label="🔽 최저 이용 시간대 (Off-Peak)", value=f"{off_peak_hour}시")
                    else:
                        st.metric(label="🔽 최저 이용 시간대 (Off-Peak)", value="N/A")
                
                st.bar_chart(hourly_df, x='hour', y='total_rentals', color="#FF4B4B")

else:
    st.info("위 필터에서 조건을 선택하고 '비교 분석 실행' 버튼을 눌러주세요.")