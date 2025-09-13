import streamlit as st
import altair as alt
import pandas as pd
import numpy as np
import load_data.summary_data_load as sdl

# --- 설정 ---
st.set_page_config(page_title="시간 패턴 비교 분석", page_icon="📅", layout="wide")

# --- 전역 옵션: 정규화 토글 ---
APPLY_NORMALIZATION = True       # True면 불러오는 모든 데이터에서 카운트를 divisor로 나눕니다.
NORMALIZATION_DIVISOR = 2        # 나눌 값 (이번 케이스는 2)
# 특정 컬럼만 정규화하고 싶으면 리스트로 지정, None이면 자동탐지 (total/ count / rental / return 포함)
NORMALIZE_COLUMNS = None

# --- Session State 초기화 ---
def init_session_state():
    session_keys = [
        'monthly_results', 'daily_hourly_results',
        'monthly_hourly_results', 'yearly_hourly_results'
    ]
    for key in session_keys:
        if key not in st.session_state:
            st.session_state[key] = None

init_session_state()

# --- 유틸리티: 카운트 정규화 함수 ---
def normalize_count_columns(df, divisor=NORMALIZATION_DIVISOR, columns=NORMALIZE_COLUMNS):
    """
    DataFrame의 카운트 계열 컬럼을 안전하게 숫자형으로 변환한 뒤 divisor로 나눕니다.
    - columns가 None이면 자동 탐지 (컬럼명에 total/count/rental/return 포함)
    - 나눗셈 결과가 정수에 매우 근접하면 int로 캐스팅합니다.
    """
    if df is None:
        return df
    # 빈 데이터프레임이면 바로 반환
    if hasattr(df, "empty") and df.empty:
        return df

    df = df.copy()

    # 자동 컬럼 탐지
    if columns is None:
        candidate_cols = [c for c in df.columns if any(k in c.lower() for k in ['total','count','rental','return'])]
    else:
        candidate_cols = [c for c in columns if c in df.columns]

    if not candidate_cols:
        return df

    for c in candidate_cols:
        # 안전하게 숫자형 변환
        num = pd.to_numeric(df[c], errors='coerce').fillna(0)
        divided = num / divisor

        # 정수에 가까운 값이면 int로 변환 (오차 허용)
        if np.all(np.isclose(divided, divided.round(), atol=1e-8)):
            df[c] = divided.round().astype(int)
        else:
            # 소수점이 필요한 경우 소수로 유지 (소수 둘째자리로 반올림)
            df[c] = divided.round(2)

    return df

# --- 데이터 분석 캐싱 함수 (로드 시 정규화 적용) ---
@st.cache_data
def get_monthly_data(years):
    df = sdl.load_summary_monthly_data(years)
    return normalize_count_columns(df) if APPLY_NORMALIZATION else df

@st.cache_data
def get_daily_hourly_data(years, month, day):
    df = sdl.load_summary_daily_data(years, month, day)
    return normalize_count_columns(df) if APPLY_NORMALIZATION else df

@st.cache_data
def get_monthly_hourly_data(years, month):
    df = sdl.load_summary_hourly_for_month(years, month)
    return normalize_count_columns(df) if APPLY_NORMALIZATION else df

@st.cache_data
def get_yearly_hourly_data(years):
    df = sdl.load_summary_hourly_for_year(years)
    return normalize_count_columns(df) if APPLY_NORMALIZATION else df

# --- 기존 유틸리티 함수들 (원본 유지) ---
def calculate_peak_hours(df, value_col):
    """최고/최저 시간대 계산"""
    if df.empty or df[value_col].sum() == 0:
        return "N/A", "N/A"

    # 안전하게 숫자형 확인
    df[value_col] = pd.to_numeric(df[value_col], errors='coerce').fillna(0)

    peak_hour = int(df.loc[df[value_col].idxmax()]['hour'])
    non_zero = df[df[value_col] > 0]
    off_peak_hour = int(non_zero.loc[non_zero[value_col].idxmin()]['hour']) if not non_zero.empty else "N/A"

    return peak_hour, off_peak_hour

def create_year_selector(label, key_prefix, default_years=[2023, 2024]):
    """연도 선택기 생성"""
    return st.multiselect(
        label,
        options=list(range(2020, 2026)),
        default=default_years,
        key=f"{key_prefix}_year_select"
    )

def display_metrics_grid(data_dict, cols_per_row=3):
    """메트릭을 그리드 형태로 표시"""
    items = list(data_dict.items())
    num_items = len(items)
    num_rows = (num_items + cols_per_row - 1) // cols_per_row

    for i in range(num_rows):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            item_index = i * cols_per_row + j
            if item_index < num_items:
                label, value = items[item_index]
                with cols[j]:
                    st.metric(label=label, value=value)

def create_hourly_chart_column(year, hourly_df, date_info, value_col='total_rentals', chart_color="#3498DB"):
    """시간대별 차트 컬럼 생성 (데이터는 이미 정규화되어 있다고 가정)"""
    st.write(f"#### {date_info}")

    # 안전하게 숫자형으로 변환
    if value_col in hourly_df.columns:
        hourly_df[value_col] = pd.to_numeric(hourly_df[value_col], errors='coerce').fillna(0)

    # 시간 범위 보장 (0~23)
    if 'hour' in hourly_df.columns:
        all_hours = pd.DataFrame({'hour': range(24)})
        hourly_df = pd.merge(all_hours, hourly_df, on='hour', how='left').fillna(0)
        hourly_df[value_col] = pd.to_numeric(hourly_df[value_col], errors='coerce').fillna(0)

    # 메트릭 계산 및 표시
    peak_hour, off_peak_hour = calculate_peak_hours(hourly_df, value_col)

    if value_col == 'total_rentals' or 'total' in value_col.lower():
        total_rentals = int(hourly_df[value_col].sum())
        metrics = {
            "총 이용 건수": f"{total_rentals:,} 건",
            "최고 시간대": f"{peak_hour} 시" if peak_hour != "N/A" else "N/A",
            "최저 시간대": f"{off_peak_hour} 시" if off_peak_hour != "N/A" else "N/A"
        }
    else:
        metrics = {
            "최고 시간대 (평균)": f"{peak_hour} 시" if peak_hour != "N/A" else "N/A",
            "최저 시간대 (평균)": f"{off_peak_hour} 시" if off_peak_hour != "N/A" else "N/A"
        }

    display_metrics_grid(metrics, cols_per_row=len(metrics))

    # 차트 표시 (원래처럼 st.bar_chart 사용)
    # 만약 Altair로 통일하고 싶으면 여기를 교체하세요.
    st.bar_chart(hourly_df, x='hour', y=value_col, color=chart_color)

# --- 메인 UI: 연도별 월간 이용량 ---
st.title("📈 연도별 월간 이용량 비교 분석")
st.info("비교하고 싶은 연도를 두 개 이상 선택하면, 연도별 월간 이용량 추이를 하나의 차트에서 비교할 수 있습니다.", icon="💡")

with st.container():
    cols = st.columns([3, 1])
    with cols[0]:
        selected_years_monthly = create_year_selector("비교할 연도 선택", "monthly")
    with cols[1]:
        st.write("")
        if st.button("📊 월간 이용량 분석", use_container_width=True, key="monthly_run_button"):
            if not selected_years_monthly:
                st.error("분석을 위해 연도를 하나 이상 선택해주세요.", icon="🚨")
                st.session_state.monthly_results = None
            else:
                with st.spinner("월별 데이터를 집계 중입니다..."):
                    st.session_state.monthly_results = get_monthly_data(years=tuple(sorted(selected_years_monthly)))

# --- 월간 이용량 결과 시각화 ---
if st.session_state.monthly_results is not None:
    results_df = st.session_state.monthly_results
    st.markdown("---")
    st.subheader("📊 분석 결과")

    if results_df.empty:
        st.warning("선택하신 연도에 해당하는 데이터가 없습니다.")
    else:
        st.write("#### 연도별 월간 이용량 추이")

        # 연도별 요약 메트릭
        st.write("#### 연도별 요약")
        total_rentals_by_year = results_df.groupby('year')['total_rentals'].sum()
        year_highest_usage = int(total_rentals_by_year.idxmax())
        highest_usage_value = int(total_rentals_by_year.max())

        metric_cols = st.columns(3)
        with metric_cols[0]:
            st.metric(
                label="🥇 가장 많이 이용한 연도",
                value=f"{year_highest_usage}년",
                delta=f"{highest_usage_value:,} 건"
            )

        # 연도별 총 이용 건수
        st.write("#### 선택 연도별 총 이용 건수")
        year_metrics = {
            f"{int(year)}년 총 이용 건수": f"{int(total):,} 건"
            for year, total in total_rentals_by_year.items()
        }
        display_metrics_grid(year_metrics)

        # Altair 차트
        line_chart = alt.Chart(results_df).mark_line(point=True).encode(
            x=alt.X('month:O', title='월', axis=alt.Axis(labelAngle=0)),
            y=alt.Y('total_rentals:Q', title='총 이용 건수'),
            color=alt.Color('year:N', title='연도'),
            tooltip=['year', 'month', 'total_rentals']
        ).properties(height=500).interactive()

        st.altair_chart(line_chart, use_container_width=True)
else:
    st.info("위 필터에서 비교할 연도를 선택하고 '월간 이용량 분석' 버튼을 눌러주세요.")

# --- 시간대별 이용량 분석 ---
st.title("🕒 시간대별 이용량 비교 분석")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["[ 🗓️ 특정일 기준 ]", "[ 🈷️ 특정월 기준 ]", "[ 🎉 특정년 기준]"])

# --- Tab 1: 특정일 기준 ---
with tab1:
    st.info("비교하고 싶은 여러 연도와 하나의 월, 일을 선택하여, 해당 날짜의 시간대별 이용량을 비교합니다.", icon="💡")

    with st.container():
        cols = st.columns([2, 1, 1, 1.5])
        with cols[0]:
            selected_years_daily = create_year_selector("연도 선택", "daily")
        with cols[1]:
            selected_month_daily = st.selectbox(
                "월 선택",
                options=list(range(1, 13)),
                format_func=lambda m: f"{m}월",
                key="daily_month_select"
            )
        with cols[2]:
            selected_day_daily = st.selectbox(
                "일 선택",
                options=list(range(1, 32)),
                key="daily_day_select"
            )
        with cols[3]:
            st.write("")
            if st.button("📈 특정일 시간대 분석", use_container_width=True, key="daily_run_button"):
                if not selected_years_daily:
                    st.error("분석을 위해 연도를 선택해주세요.", icon="🚨")
                    st.session_state.daily_hourly_results = None
                else:
                    with st.spinner("선택하신 날짜의 데이터를 분석 중입니다..."):
                        st.session_state.daily_hourly_results = get_daily_hourly_data(
                            years=tuple(selected_years_daily),
                            month=selected_month_daily,
                            day=selected_day_daily
                        )

    # 특정일 결과 시각화
    if st.session_state.daily_hourly_results is not None:
        results_df = st.session_state.daily_hourly_results
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
                    date_info = f"{year}년 {selected_month_daily}월 {selected_day_daily}일"
                    create_hourly_chart_column(year, hourly_df, date_info, 'total_rentals', "#3498DB")

# --- Tab 2: 특정월 기준 ---
with tab2:
    st.info("비교하고 싶은 여러 연도와 하나의 월을 선택하여, 해당 월의 **평균 시간대별 이용 패턴**을 비교합니다.", icon="💡")

    with st.container():
        cols = st.columns([2, 1, 1.5])
        with cols[0]:
            selected_years_monthly_h = create_year_selector("연도 선택", "monthly_hourly")
        with cols[1]:
            selected_month_monthly_h = st.selectbox(
                "월 선택",
                options=list(range(1, 13)),
                format_func=lambda m: f"{m}월",
                key="monthly_hourly_month_select"
            )
        with cols[2]:
            st.write("")
            if st.button("📈 특정월 시간대 패턴 분석", use_container_width=True, key="monthly_hourly_run_button"):
                if not selected_years_monthly_h:
                    st.error("분석을 위해 연도를 선택해주세요.", icon="🚨")
                    st.session_state.monthly_hourly_results = None
                else:
                    with st.spinner(f"{selected_month_monthly_h}월의 시간대별 평균 데이터를 분석 중입니다..."):
                        st.session_state.monthly_hourly_results = get_monthly_hourly_data(
                            years=tuple(selected_years_monthly_h),
                            month=selected_month_monthly_h
                        )

    # 특정월 결과 시각화
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
                    date_info = f"{year}년 {selected_month_monthly_h}월 평균"
                    create_hourly_chart_column(year, hourly_df, date_info, 'avg_total_rentals', "#F1C40F")

# --- Tab 3: 특정년 기준 ---
with tab3:
    st.info("비교하고 싶은 여러 연도를 선택하여, 해당 년도의 **평균 시간대별 이용량**을 비교합니다.", icon="💡")

    with st.container():
        cols = st.columns([3, 1])
        with cols[0]:
            selected_years_hour = create_year_selector("연도 선택", "yearly_hourly")
        with cols[1]:
            st.write("")
            if st.button("📈 연도별 시간대 패턴 분석", use_container_width=True, key="yearly_hourly_run_button"):
                if not selected_years_hour:
                    st.error("분석을 위해 연도를 선택해주세요.", icon="🚨")
                    st.session_state.yearly_hourly_results = None
                else:
                    with st.spinner("선택하신 연도의 시간대별 평균 데이터를 분석 중입니다..."):
                        st.session_state.yearly_hourly_results = get_yearly_hourly_data(years=tuple(selected_years_hour))

    # 특정년 결과 시각화
    if st.session_state.yearly_hourly_results is not None:
        results_df = st.session_state.yearly_hourly_results
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
                    date_info = f"{year}년 평균"
                    create_hourly_chart_column(year, hourly_df, date_info, 'avg_total_rentals', "#2ECC71")
    else:
        st.info("위 필터에서 연도를 선택하고 '연도별 시간대 패턴 분석' 버튼을 눌러주세요.")
