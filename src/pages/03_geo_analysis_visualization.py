import streamlit as st
import pandas as pd
import altair as alt

from src.load_data.station_route_data_load import load_station_summary_data, load_route_summary_data

st.set_page_config(page_title="지리 정보 기반 이용 행태 분석", page_icon="🗺️", layout="wide")

# --- Altair 시각화 함수 정의 (최종 수정) ---
def create_altair_station_pie(station_df):
    """ 
    [최종 수정] Altair를 사용하여 Top 20 대여소 비중 파이 차트를 생성합니다.
    Tooltip의 데이터 타입을 명시하여 오류를 해결합니다.
    """
    if station_df.empty: return None
    
    total_usage = station_df['총_이용건수'].sum()
    top_20_usage = station_df.sort_values(by='총_이용건수', ascending=False).head(20)['총_이용건수'].sum()
    other_usage = total_usage - top_20_usage

    chart_data = pd.DataFrame({
        '구분': [f'Top 20 대여소', f'나머지 {len(station_df)-20:,}개 대여소'],
        '이용건수': [top_20_usage, other_usage]
    })

    base = alt.Chart(chart_data).transform_window(
        total='sum(이용건수)',
        frame=[None, None]
    ).transform_calculate(
        percent="datum.이용건수 / datum.total"
    )

    pie_chart = base.mark_arc(innerRadius=50, outerRadius=120).encode(
        theta=alt.Theta(field="이용건수", type="quantitative", stack=True),
        color=alt.Color(field="구분", type="nominal",
                        scale=alt.Scale(domain=chart_data['구분'].tolist(), range=['#ff9999', '#c2c2c2']),
                        legend=alt.Legend(title="대여소 그룹")),
        tooltip=[
            alt.Tooltip('구분', title='그룹'),
            alt.Tooltip('이용건수', title='이용 건수', format=',d'),
            # --- 💡 핵심 수정 ---
            alt.Tooltip('percent:Q', title='비중', format='.1%') 
        ]
    ).properties(title='Top 20 대여소 이용량 비중')
    
    text = base.mark_text(radius=85, size=14, fill='white', fontWeight='bold').encode(
        text=alt.Text('percent:Q', format='.1%'),
        theta=alt.Theta(field="이용건수", type="quantitative", stack=True)
    )
    return pie_chart + text

def create_altair_trip_type_pie(route_df):
    """ 
    [최종 수정] Altair를 사용하여 편도/왕복 비율 파이 차트를 생성합니다.
    Tooltip의 데이터 타입을 명시하여 오류를 해결합니다.
    """
    if route_df.empty: return None
    
    usage_by_type = route_df.groupby('이용_형태')['이용_건수'].sum().reset_index()

    base = alt.Chart(usage_by_type).transform_window(
        total='sum(이용_건수)',
        frame=[None, None]
    ).transform_calculate(
        percent="datum.이용_건수 / datum.total"
    )

    pie_chart = base.mark_arc(innerRadius=50, outerRadius=120).encode(
        theta=alt.Theta(field="이용_건수", type="quantitative", stack=True),
        color=alt.Color(field="이용_형태", type="nominal",
                        scale=alt.Scale(domain=['편도', '왕복'], range=['#66b3ff', '#ffcc99']),
                        legend=alt.Legend(title="이용 형태")),
        tooltip=[
            alt.Tooltip('이용_형태', title='형태'),
            alt.Tooltip('이용_건수', title='이용 건수', format=',d'),
            # --- 💡 핵심 수정 ---
            alt.Tooltip('percent:Q', title='비중', format='.1%')
        ]
    ).properties(title='전체 따릉이 이용 형태 비율')

    text = base.mark_text(radius=85, size=14, fill='black', fontWeight='bold').encode(
        text=alt.Text('percent:Q', format='.1%'),
        theta=alt.Theta(field="이용_건수", type="quantitative", stack=True)
    )
    return pie_chart + text


# --- 메인 페이지 구성 ---
st.title("🗺️ 지리 정보 기반 이용 행태 분석")
st.markdown("---")
st.info("대여소의 지리적 특성과 대여소 간의 이동 경로(Route)를 분석하여 따릉이의 공간적 이용 패턴을 파악합니다.")

tab1, tab2 = st.tabs(["[ 📍 대여소 중심 분석 ]", "[ ↔️ 경로 중심 분석 ]"])

with tab1:
    st.header("대여소별 이용 현황 분석")
    
    @st.cache_data
    def get_station_data():
        df = load_station_summary_data()
        # 💡 2. 전체 주소 컬럼 미리 생성
        if not df.empty:
            df['전체주소'] = df['주소1'] + " " + df['주소2'].fillna('')
        return df
    station_df = get_station_data()

    if not station_df.empty:
        col1, col2 = st.columns([1, 1.5])
        with col1:
            st.subheader("📊 Top 20 대여소 이용량 비중")
            pie_fig = create_altair_station_pie(station_df)
            if pie_fig: st.altair_chart(pie_fig, use_container_width=True)
        with col2:
            st.subheader("🏆 인기 대여소 Top 20")
            top_20 = station_df.sort_values(by='총_이용건수', ascending=False).head(20).reset_index(drop=True)
            # 💡 3. 순위 인덱스 설정
            top_20.index = top_20.index + 1
            st.dataframe(top_20[['전체주소', '총_이용건수', '순이동량']], height=450)

        st.markdown("---")
        st.subheader("🌊 자전거 쏠림 현상 Top 20")
        col3, col4 = st.columns(2)
        with col3:
            st.write("📤 **자전거 유출 Top 20 (공급 필요)**")
            outflow = station_df.sort_values(by='순이동량', ascending=False).head(20).reset_index(drop=True)
            outflow.index = outflow.index + 1
            st.dataframe(outflow[['전체주소', '순이동량']])
        with col4:
            st.write("📥 **자전거 유입 Top 20 (수거 필요)**")
            inflow = station_df.sort_values(by='순이동량', ascending=True).head(20).reset_index(drop=True)
            inflow.index = inflow.index + 1
            st.dataframe(inflow[['전체주소', '순이동량']])

        st.markdown("---")
        st.subheader("🗺️ 자전거 쏠림 현상 지도")
        st.info("지도 우측 상단의 컨트롤 박스를 통해 유출(🔴)/유입(🔵)/균형(⚫) 그룹을 선택하여 볼 수 있습니다.")
        try:
            with open('interactive_station_map.html', 'r', encoding='utf-8') as f:
                map_html = f.read()
            # 💡 5. 지도 세로 길이 조정
            st.components.v1.html(map_html, height=800, scrolling=True)
        except FileNotFoundError:
            st.error("지도 파일(interactive_station_map.html)을 찾을 수 없습니다.")
    else:
        st.warning("대여소 요약 데이터가 없습니다.")

with tab2:
    st.header("주요 이동 경로(Route) 분석")
    
    @st.cache_data
    def get_route_data():
        df = load_route_summary_data()
        # 💡 2. 전체 주소 컬럼 미리 생성
        if not df.empty:
            df['출발지'] = df['주소1_시작'] + " " + df['주소2_시작'].fillna('')
            df['도착지'] = df['주소1_종료'] + " " + df['주소2_종료'].fillna('')
        return df
    route_df = get_route_data()

    if not route_df.empty:
        col1, col2 = st.columns([1, 1.5])
        with col1:
            st.subheader("📊 전체 이용 형태 비율")
            trip_pie_fig = create_altair_trip_type_pie(route_df)
            if trip_pie_fig: st.altair_chart(trip_pie_fig, use_container_width=True)
        with col2:
            st.subheader("🏞️ 인기 왕복 경로 Top 10")
            round_trips = route_df[route_df['이용_형태'] == '왕복'].sort_values(by='이용_건수', ascending=False).head(10).reset_index(drop=True)
            round_trips.index = round_trips.index + 1
            st.dataframe(round_trips[['출발지', '이용_건수']], height=450)
            
        st.markdown("---")
        # 💡 4. 한자 제거
        st.subheader("🚉 주요 이동 경로 (인기 편도 Top 10)")
        one_way_trips = route_df[route_df['이용_형태'] == '편도'].sort_values(by='이용_건수', ascending=False).head(10).reset_index(drop=True)
        one_way_trips.index = one_way_trips.index + 1
        st.dataframe(one_way_trips[['출발지', '도착지', '이용_건수']])

        st.markdown("---")
        st.subheader("🗺️ 서울시 주요 이동 경로 및 핫스팟")
        st.info("지도 우측 상단의 컨트롤 박스를 통해 데이터 레이어(경로/핫스팟)를 선택할 수 있습니다.")
        try:
            with open('final_routes_map_osm.html', 'r', encoding='utf-8') as f:
                map_html = f.read()
            # 💡 5. 지도 세로 길이 조정
            st.components.v1.html(map_html, height=800, scrolling=True)
        except FileNotFoundError:
            st.error("지도 파일(final_routes_map_osm.html)을 찾을 수 없습니다.")
    else:
        st.warning("경로 요약 데이터가 없습니다.")