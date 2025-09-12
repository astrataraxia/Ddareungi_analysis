import streamlit as st
import altair as alt
import pandas as pd

import src.load_data.summary_data_load as sdl

# --- 페이지 기본 설정 ---
st.set_page_config(page_title="시간 패턴 비교 분석", page_icon="📅", layout="wide")

# --- Session State 초기화 (이름 명확화) ---
if 'monthly_results' not in st.session_state: st.session_state.monthly_results = None
if 'daily_hourly_results' not in st.session_state: st.session_state.daily_hourly_results = None
if 'monthly_hourly_results' not in st.session_state: st.session_state.monthly_hourly_results = None

# --- 데이터 분석 캐싱 함수 (이름 일관성 유지) ---
@st.cache_data
def get_monthly_data(years):
    return sdl.load_summary_monthly_data(years)

@st.cache_data
def get_daily_hourly_data(years, month, day):
    return sdl.load_summary_daily_data(years, month, day)

@st.cache_data
def get_monthly_hourly_data(years, month):
    return sdl.load_summary_hourly_for_month(years, month)

# --- UI 구현 1: 연도별 월간 이용량 ---
st.title("📈 연도별 월간 이용량 비교 분석")
st.info("비교하고 싶은 연도를 두 개 이상 선택하면, 연도별 월간 이용량 추이를 하나의 차트에서 비교할 수 있습니다.", icon="💡")

with st.container(border=True):
    cols = st.columns([3, 1])
    with cols[0]:
        selected_years_monthly = st.multiselect(
            "비교할 연도 선택", options=list(range(2020, 2026)), 
            default=[2023, 2024], key="monthly_year_select" # 고유 key 추가
        )
    with cols[1]:
        st.write("")
        if st.button("📊 월간 이용량 분석", use_container_width=True, key="monthly_run_button"): # 고유 key 및 라벨 수정
            if not selected_years_monthly:
                st.error("분석을 위해 연도를 하나 이상 선택해주세요.", icon="🚨")
                st.session_state.monthly_results = None
            else:
                with st.spinner("월별 데이터를 집계 중입니다..."):
                    st.session_state.monthly_results = get_monthly_data(years=tuple(sorted(selected_years_monthly)))

# --- 결과 시각화 1: 연도별 월간 이용량 ---
if st.session_state.monthly_results is not None:
    results_df = st.session_state.monthly_results
    st.markdown("---")
    st.subheader("📊 분석 결과")
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


st.title("🕒 시간대별 이용량 비교 분석")
st.markdown("---")

tab1, tab2 = st.tabs(["[ 🗓️ 특정일 기준 ]", "[ 🈷️ 특정월 기준 ]"])

# --- UI 구현 2: 특정일 기준 시간대별 분석 ---
with tab1:
    st.info("비교하고 싶은 여러 연도와 하나의 월, 일을 선택하여, 해당 날짜의 시간대별 이용량을 비교합니다.", icon="💡")
    with st.container(border=True):
        cols = st.columns([2, 1, 1, 1.5])
        with cols[0]:
            selected_years_daily = st.multiselect("연도 선택", options=list(range(2020, 2026)), default=[2023, 2024], key="daily_year_select")
        with cols[1]:
            selected_month_daily = st.selectbox("월 선택", options=list(range(1, 13)), format_func=lambda m: f"{m}월", key="daily_month_select")
        with cols[2]:
            selected_day_daily = st.selectbox("일 선택", options=list(range(1, 32)), key="daily_day_select")
        with cols[3]:
            st.write("")
            if st.button("📈 특정일 시간대 분석", use_container_width=True, key="daily_run_button"):
                if not selected_years_daily or not selected_month_daily or not selected_day_daily:
                    st.error("분석을 위해 연도, 월, 일을 모두 선택해야 합니다.", icon="🚨")
                    st.session_state.daily_hourly_results = None
                else:
                    with st.spinner("선택하신 날짜의 데이터를 분석 중입니다..."):
                        st.session_state.daily_hourly_results = get_daily_hourly_data(
                            years=tuple(selected_years_daily), month=selected_month_daily, day=selected_day_daily
                        )
    
    # --- 결과 시각화 2: 특정일 기준 ---
    if st.session_state.daily_hourly_results is not None:
        results_df = st.session_state.daily_hourly_results
        st.markdown("---")
        st.subheader("📊 분석 결과")
        if results_df.empty:
            st.warning("선택하신 조건에 해당하는 데이터가 없습니다.")
        else:
            sorted_years = sorted(results_df['year'].unique())
            chart_cols = st.columns(len(sorted_years)) # 컬럼을 연도 수에 맞게 동적 생성
            for i, year in enumerate(sorted_years):
                with chart_cols[i]:
                    hourly_df = results_df[results_df['year'] == year].copy()
                    all_hours = pd.DataFrame({'hour': range(24)})
                    hourly_df = pd.merge(all_hours, hourly_df, on='hour', how='left').fillna(0)
                    hourly_df['total_rentals'] = hourly_df['total_rentals'].astype(int)
                    st.write(f"#### {year}년 {selected_month_daily}월 {selected_day_daily}일")
                    total_rentals = hourly_df['total_rentals'].sum()
                    if total_rentals > 0:
                        peak_hour = int(hourly_df.loc[hourly_df['total_rentals'].idxmax()]['hour'])
                        non_zero = hourly_df[hourly_df['total_rentals'] > 0]
                        off_peak_hour = int(non_zero.loc[non_zero['total_rentals'].idxmin()]['hour'])
                    else:
                        peak_hour, off_peak_hour = "N/A", "N/A"
                    metric_cols = st.columns(3)
                    metric_cols[0].metric(label="총 이용 건수", value=f"{total_rentals:,} 건")
                    metric_cols[1].metric(label="최고 시간대", value=f"{peak_hour} 시" if peak_hour != "N/A" else "N/A")
                    metric_cols[2].metric(label="최저 시간대", value=f"{off_peak_hour} 시" if off_peak_hour != "N/A" else "N/A")
                    st.bar_chart(hourly_df, x='hour', y='total_rentals', color="#3498DB")

# --- UI 구현 3: 특정월 기준 시간대별 분석 ---
with tab2:
    st.info("비교하고 싶은 여러 연도와 하나의 월을 선택하여, 해당 월의 **평균 시간대별 이용 패턴**을 비교합니다.", icon="💡")
    with st.container(border=True):
        cols = st.columns([2, 1, 1.5])
        with cols[0]:
            selected_years_monthly_h = st.multiselect("연도 선택 ", options=list(range(2020, 2026)), default=[2023, 2024], key="monthly_hourly_year_select")
        with cols[1]:
            selected_month_monthly_h = st.selectbox("월 선택 ", options=list(range(1, 13)), format_func=lambda m: f"{m}월", key="monthly_hourly_month_select")
        with cols[2]:
            st.write("")
            if st.button("📈 특정월 시간대 패턴 분석", use_container_width=True, key="monthly_hourly_run_button"):
                if not selected_years_monthly_h or not selected_month_monthly_h:
                    st.error("분석을 위해 연도와 월을 모두 선택해야 합니다.", icon="🚨")
                    st.session_state.monthly_hourly_results = None
                else:
                    with st.spinner(f"{selected_month_monthly_h}월의 시간대별 평균 데이터를 분석 중입니다..."):
                        st.session_state.monthly_hourly_results = get_monthly_hourly_data(
                            years=tuple(selected_years_monthly_h), month=selected_month_monthly_h
                        )

    # --- 결과 시각화 3: 특정월 기준 ---
    if st.session_state.monthly_hourly_results is not None:
        results_df = st.session_state.monthly_hourly_results
        st.markdown("---")
        st.subheader("📊 분석 결과")
        if results_df.empty:
            st.warning("선택하신 조건에 해당하는 데이터가 없습니다.")
        else:
            sorted_years = sorted(results_df['year'].unique())
            chart_cols = st.columns(len(sorted_years))
            for i, year in enumerate(sorted_years):
                with chart_cols[i]:
                    hourly_df = results_df[results_df['year'] == year].copy()
                    st.write(f"#### {year}년 {selected_month_monthly_h}월 평균")
                    
                    # --- 💡 메트릭 추가 ---
                    if not hourly_df['avg_total_rentals'].empty and hourly_df['avg_total_rentals'].sum() > 0:
                        peak_hour = int(hourly_df.loc[hourly_df['avg_total_rentals'].idxmax()]['hour'])
                        non_zero = hourly_df[hourly_df['avg_total_rentals'] > 0]
                        off_peak_hour = int(non_zero.loc[non_zero['avg_total_rentals'].idxmin()]['hour'])
                    else:
                        peak_hour, off_peak_hour = "N/A", "N/A"
                    metric_cols = st.columns(2)
                    metric_cols[0].metric(label="최고 시간대 (평균)", value=f"{peak_hour} 시" if peak_hour != "N/A" else "N/A")
                    metric_cols[1].metric(label="최저 시간대 (평균)", value=f"{off_peak_hour} 시" if off_peak_hour != "N/A" else "N/A")

                    st.bar_chart(hourly_df, x='hour', y='avg_total_rentals', color="#F1C40F")