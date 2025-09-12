# Feature Specification: 서울시 공공자전거 "따릉이" 데이터 분석

**Feature Branch**: `Main`
**Created**: 2025-09-09
**Input**: User description: "서울시 공공자전거 따릉이 운영에 있어서 더욱 효율적이고, 세부적인 문제점을 파악하여 해결하기위한 데이터 분석 프로젝트를 할것이다.또한 서울시 인구와 따릉이 이용자간에 상관관계도 같이 파악해볼 것이고 이를 이용하기위한 자료들은 준비되어있다. 목표는 시간대별 이용패턴 분석, 이용행태분석(왕복 vs 편도), 인기대여소 및 주요 경로 파악, 이용시간과 거리의관계분석을 해볼것이다. 이것이 필요한 이유는 앞서 말했듯 따릉이 운영에 있어서 더욱 효율적이고 문제점을 찾아내어 해결하기 위한 방법이다"

---

## Analysis Goals & Methods *(mandatory)*

### 1. 시간대별 이용 패턴 분석 (Analysis of Usage Patterns by Time)
**Goal**: 따릉이 이용자들이 주로 어떤 월(Month), 요일(Day of week), 시간대(Hour)에 따릉이를 가장 많이 이용하는지 파악하여 시간대별 수요 변화를 이해합니다. (예: 출퇴근 시간, 주말 오후 등)
**Method**: 시계열 분석 및 패턴 탐색 - 월, 요일, 시간대별 따릉이 대여/반납 건수를 집계하고 시각화(꺾은선 그래프, 히트맵 등)하여 주기적인 이용 패턴 및 피크 타임을 파악합니다. 특히 출퇴근 시간, 주말 오후 등 특정 시간대의 수요 변화를 심층 분석합니다.

### 2. 이용 시간과 거리의 관계 분석 (Analysis of Relationship between Usage Time and Distance)
**Goal**: 따릉이 이용 시간과 이동 거리 간의 관계를 분석하여 단거리 이용과 장거리 이용의 특징 및 패턴을 알아봅니다.
**Method**: 시계열 분석 및 패턴 탐색 - 개별 이용 건에 대한 총 사용 시간과 움직인 거리를 활용하여, 이용 시간대별/거리별 분포를 파악하고, 짧은 거리 이용과 긴 거리 이용의 특징을 분석합니다. 산점도 등을 통해 두 변수 간의 상관관계를 시각화합니다.

### 3. 이용 시간과 거리의 관계 분석 (Analysis of Relationship between Usage Time and Distance)
**Goal** 대여소(station_summary) 중심 분석
- 인기 대여소 Top 20: 어떤 대여소가 시민들에게 가장 사랑받는지 파악했습니다.
- 자전거 쏠림 현상: 순이동량 분석을 통해 자전거가 항상 부족한 곳(유출)과 넘쳐나는 곳(유입)을 정확히 찾아냈습니다.
- 숨겨진 비효율 발견: 쏠림 비율 분석으로, 이용량은 적지만 운영 관리가 시급한 '특이 대여소'를 발굴했습니다.
- 핵심 결과물: interactive_station_map.html
**Goal** 경로(route_summary) 중심 분석
- 전체 이용 행태 파악: 편도와 왕복 비율 분석을 통해 따릉이가 '교통수단'으로서의 역할이 훨씬 크다는 것을 증명했습니다.
- 주요 레저 코스 식별: 인기 '왕복' 경로 분석으로 시민들의 주말 나들이/운동 패턴을 파악했습니다.
-핵심 생활 동선 파악: 인기 '편도' 경로 분석으로 시민들의 출퇴근/통학 '혈관'과도 같은 주요 이동 축을 찾아냈습니다.

### 4. 년도별 따릉이 수요와 서울시 인구 증가의 상관관계 분석 (Correlation Analysis of Annual Ddareungi Demand and Seoul Population Growth)
**Goal**: 2020년부터 2025년까지의 서울시 인구 증감률과 따릉이 수요 증감률을 비교하여 인구 변화가 따릉이 이용에 미치는 영향을 분석하고 잠재적 상관관계를 도출합니다.
**Method**: 데이터 마이닝 및 통계 분석 - 년도별 서울시 인구 증감률 데이터와 따릉이 총 이용 건수 또는 대여 건수 증감률 데이터를 수집하여 시계열 데이터를 구축합니다. 통계적 상관 분석(예: 피어슨 상관계수)을 통해 두 변수 간의 연관성을 정량적으로 파악하고, 회귀 분석을 통해 인구 변화가 따릉이 수요에 미치는 영향을 모델링합니다.

## User Interface / Visualization Requirements (Streamlit)

### Application Structure
The Streamlit application will have the following file structure:

*   **Main visualization Page**: `src/main.py` (Introduction/Overview)
*   **visualization Analysis Pages**: Located in `src/pages/`
    *   `01_time_analysis_visualization.py`
    *   `02_distance_time_visualization.py`
    *   `03_station_routes_visualization.py`
    *   `04_population_visualization.py`
    *   `05_conclusion.py`

### Interactivity and Filtering
For analysis charts, the application MUST provide interactive filtering capabilities:

*   **Time-based Filtering**: Users MUST be able to filter data by year, month, and specific time ranges (e.g., hour of day).
*   **Station-based Filtering**: Users MUST be able to filter data and view analysis results specific to individual rental stations.

## Key Entities *(include if feature involves data)*
- **Ddareungi Usage Data**: Represents a single trip, including rental/return time, station, distance, etc.
- **Bicycle Station**: Represents a single rental station with its location.
- **Registered Population**: Represents the registered population data for districts in Seoul.
