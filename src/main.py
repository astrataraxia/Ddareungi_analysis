import streamlit as st

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.load_data.data_load import load_parquet_year_data,load_station_data, load_population_data

# --- 페이지 설정 ---
# layout="wide"로 변경하여 넓은 화면을 모두 사용합니다.
st.set_page_config(
    page_title="따릉이 데이터 분석 프로젝트",
    page_icon="🚲",
    layout="wide", # 'centered' -> 'wide'
    initial_sidebar_state="expanded"
)

# --- 데이터 로딩 함수 (기존과 동일) ---
@st.cache_data
def get_parquet_sample_data():
    """Parquet 파일 제너레이터에서 첫 번째 청크의 상위 5개 행만 샘플로 반환합니다."""
    try:
        first_chunk = next(load_parquet_year_data(2020))
        return first_chunk.head()
    except Exception as e:
        st.error(f"Parquet 데이터 로딩 중 오류 발생: {e}")
        return None

@st.cache_data
def get_station_data():
    try:
        return load_station_data()
    except FileNotFoundError:
        return None

@st.cache_data
def get_population_data():
    try:
        return load_population_data()
    except FileNotFoundError:
        return None

# --- 메인 페이지 구현 ---
def main_page():
    # --- 1. 프로젝트 소개 ---
    st.title("🚲 서울시 공공자전거 '따릉이' 데이터 분석")
    st.markdown("---")
    st.markdown("""
    안녕하세요! 이 프로젝트는 서울시 공공자전거 '따릉이'의 방대한 이용 데이터를 분석하여,
    운영 효율성을 개선하고 시민들이 겪는 불편함을 해결하기 위한 인사이트를 도출하는 것을 목표로 합니다.
    """)
    st.info("👈 **왼쪽 사이드바에서 원하는 분석 메뉴를 선택하여 결과를 확인하실 수 있습니다.**", icon="💡")
    st.markdown("---")

    # --- 2. 프로젝트 목표 ---
    # st.expander를 사용하여 내용을 기본적으로 숨겨두고, 클릭하면 펼쳐지도록 합니다.
    with st.expander("🎯 프로젝트 목표 자세히 보기", expanded=True):
        st.markdown("""
        이 분석을 통해 다음과 같은 질문에 대한 답을 찾고자 합니다.
        - **01 시간대별 수요 예측:** 사용자들이 주로 언제 따릉이를 이용할까요? (월/요일/시간대)
        - **02 이용 시간과 거리의 관계:** 이용 시간과 이동 거리간의 관계는 어떻게 될까요?
        - **03 이용 행태 분석:** 시민들은 어떤 곳에서 자전거를 많이 빌리고 반납의 형태(편도,왕복) 어떻게 될까요?
        - **04 인구 데이터와 연관성 분석:** 서울시 인구 변화가 따릉이 수요에 미치는 영향이 있을까요?
        - **05 데이터 분석을 통한 인사이트 도출:** 데이터 분석을 통해 따릉이 서비스 개선에 활용할 수 있는 인사이트는 무엇일까요?
        """)
    st.write("") # 섹션 간 여백
    st.markdown("---") # 구분선 추가
    st.write("")


    # --- 2. 사용 데이터 소개 ---
    st.header("💾 사용 데이터 소개")
    st.markdown("본 분석에는 다음과 같은 세 가지 주요 데이터를 사용하며, 각 항목을 클릭하여 자세한 내용을 확인하실 수 있습니다.")
    st.write("")

    # st.expander를 사용하여 각 데이터 섹션을 접고 펼 수 있는 목록 형태로 만듭니다.
    # 첫 번째 항목은 expanded=True로 설정하여 기본적으로 펼쳐져 있도록 합니다.
    with st.expander("📊 1. 따릉이 이용 내역"):
        st.markdown("2020년부터 2025년까지의 시간대/대여소별 대여 및 반납 기록 데이터입니다. 데이터의 크기가 매우 커 메모리 효율적인 방식으로 처리해야 합니다.")
        st.info(
            """
            **주요 컬럼 설명:**
            - `기준_날짜`, `기준_시간대`: 이용 시간 분석의 핵심 기준이 됩니다.
            - `시작_대여소_ID`, `종료_대여소_ID`: 이용 경로 및 행태 분석에 사용됩니다.
            - `전체_건수`: 각 시간대의 총 이용량을 나타내어 수요를 파악하는 데 사용됩니다.
            """, icon="✅"
        )
        usage_df_sample = get_parquet_sample_data()
        if usage_df_sample is not None:
            st.dataframe(usage_df_sample, width='stretch')
        else:
            st.warning("이용 내역 데이터를 로드할 수 없습니다.")

    with st.expander("📈 2. 자전거 대여소 정보"):
        st.markdown("서울시 전역에 위치한 모든 따릉이 대여소의 마스터 정보입니다. 따릉이 이용 내역 데이터와 결합하여 지리적 분석을 수행하는 데 사용됩니다.")
        st.info(
            """
            **주요 컬럼 설명:**
            - `대여소_ID`: 각 대여소를 구분하는 고유한 키(Key) 값입니다.
            - `위도`, `경도`: 지도 시각화를 위한 핵심적인 위치 좌표 정보입니다.
            """, icon="✅"
        )
        station_df = get_station_data()
        if station_df is not None:
            st.dataframe(station_df.head(), width='stretch')
        else:
            st.warning("대여소 데이터를 로드할 수 없습니다.")

    with st.expander("📉 3. 서울시 인구 데이터"):
        st.markdown("서울시 행정구역별, 분기별 등록 인구 데이터입니다. 따릉이 전체 수요와 인구 변화의 연관성을 파악하는 데 활용됩니다.")
        st.info(
            """
            **주요 컬럼 설명:**
            - `동별(1)`, `동별(2)`: 행정구역을 나타냅니다.
            - `'YYYY Q/Q'` 형태의 컬럼: 각 연도/분기별 인구수를 나타내는 다중 헤더 구조를 가집니다.
            """, icon="✅"
        )
        population_df = get_population_data()
        if population_df is not None:
            st.dataframe(population_df.head(), width='stretch')
        else:
            st.warning("인구 데이터를 로드할 수 없습니다.")


# --- 앱 실행 ---
if __name__ == "__main__":
    main_page()