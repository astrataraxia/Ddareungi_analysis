# 📝 프로젝트 기술 명세서 (Technical Specification)

## 1. 프로젝트 개요

본 문서는 '서울시 공공자전거 따릉이 데이터 분석 프로젝트'의 기술적인 아키텍처, 데이터 파이프라인, 주요 모듈의 기능 및 실행 방법을 상세히 기술하는 것을 목적으로 한다.

- **프로젝트 목표**: 서울시 공공자전거 '따릉이'의 대규모 이용 데이터를 분석하여 운영 효율성을 개선하고, 서비스 품질 향상을 위한 데이터 기반의 인사이트를 도출한다.
- **최종 결과물**: 사용자가 직접 데이터를 탐색하고 분석 결과를 확인할 수 있는 인터랙티브 웹 대시보드 및 종합 분석 보고서.

---

## 2. 기술 스택

본 프로젝트는 다음의 언어, 라이브러리, 및 도구를 사용하여 구축되었다.

| 구분 | 기술명 | 버전 | 주요 용도 |
|---|---|---|---|
| **언어** | Python | >=3.13 | 프로젝트 전반의 개발 언어 |
| **패키지 매니저** | uv | - | 의존성 관리 및 가상 환경 구성 |
| **데이터 처리** | pandas | >=2.3.2 | 데이터 구조화, 정제, 변환, 집계 |
| | numpy | - | 수치 연산 및 데이터 배열 처리 |
| | pyarrow | >=21.0.0 | Parquet 파일 형식 처리, 메모리 효율 증대 |
| **시각화** | streamlit | >=1.49.1 | 인터랙티브 웹 대시보드 구축 |
| | matplotlib | >=3.10.6 | 정적 그래프 및 차트 생성 |
| | seaborn | >=0.13.2 | 통계 기반의 미려한 시각화 |
| | altair | - | 선언형 통계 시각화 (Streamlit 연동) |
| | folium | >=0.20.0 | 지리 정보 시각화 (지도 생성) |
| | geopandas | >=1.1.1 | 지리 공간 데이터 처리 (향후 확장용) |
| **코드 품질** | ruff | >=0.1.0 | Linter 및 Formatter |
| **테스트** | pytest | >=8.4.2 | 단위/통합 테스트 (필요시) |

---

## 3. 프로젝트 아키텍처 및 디렉토리 구조

프로젝트는 데이터 처리 단계와 역할에 따라 명확하게 모듈화되어 있다.

```
C:/Users/astra/study/python/project/
├── data/              # 💾 데이터 저장소
│   ├── parquet/       # 표준화된 원본 데이터 (Parquet 형식)
│   ├── 01/            # 분석 마트 1: 시간 기반 분석용
│   ├── 02/            # 분석 마트 2: 거리/시간 기반 분석용
│   ├── 03/            # 분석 마트 3: 대여소/경로 기반 분석용
│   ├── bcycle_master_location.csv   # 대여소 마스터 정보
│   └── registered_population.csv    # 서울시 인구 통계
├── src/               # 🐍 소스 코드
│   ├── translate_data/  # 1. 원본 데이터 표준화/변환 스크립트
│   ├── data_mart/     # 2. 분석용 데이터 마트 생성 (ETL) 스크립트
│   ├── load_data/     # 3. 데이터 로딩 유틸리티 모듈
│   ├── analyse/       # 4. 독립적인 심층 분석 스크립트
│   ├── pages/         # 5. Streamlit 대시보드 페이지
│   └── main.py        # 🚀 Streamlit 앱 메인 실행 파일
├── maps/              # 🗺️ 생성된 지도 HTML 파일
├── report_images/     # 🖼️ 보고서용 정적 이미지 파일
├── specs/             # 📄 프로젝트 명세 문서
│   ├── spec.md        # (현재 파일)
│   └── data-model.md  # 데이터 모델 명세
├── insight.html       # 📜 최종 분석 보고서 HTML
├── pyproject.toml     # ⚙️ 프로젝트 의존성 및 설정
└── README.md          # 📖 프로젝트 개요
```

- **`src/translate_data`**: 각기 다른 형식의 원본 CSV 파일을 표준화된 컬럼 구조로 통일하고, 대용량 처리에 용이한 Parquet 형식으로 변환하는 첫 단계.
- **`src/data_mart`**: 표준화된 Parquet 데이터를 입력받아, 각 분석 목적에 맞게 미리 데이터를 집계하고 가공(ETL)하여 분석용 '데이터 마트'를 생성.
- **`src/load_data`**: 각 분석 모듈 및 대시보드 페이지에서 필요한 데이터 마트를 효율적으로 로드하는 함수를 제공.
- **`src/analyse`**: 대시보드와는 별개로, 특정 주제에 대한 심층 분석을 수행하고 정적 시각화 결과물(이미지, HTML 등)을 생성.
- **`src/pages`**: Streamlit 대시보드의 각 페이지 UI와 동적 시각화를 담당. 파일 이름 순서대로 사이드바 메뉴가 구성됨.

---

## 4. 데이터 파이프라인 (ETL)

데이터는 '원본 → 표준화 → 데이터 마트'의 3단계 파이프라인을 거쳐 처리된다.

### 4.1. 원본 데이터
- **따릉이 이용 내역**: 연도별/월별/일별로 나뉜 CSV 파일. 컬럼 구조가 시기별로 상이(7개 또는 10개).
- **대여소 마스터**: `bcycle_master_location.csv`. 대여소 ID, 주소, 위/경도 정보 포함.
- **인구 통계**: `registered_population.csv`. 서울시 분기별 등록 인구 정보.

### 4.2. 1단계: 데이터 표준화 및 변환 (`src/translate_data`)
- **목표**: 각기 다른 원본 CSV를 일관된 형식의 Parquet 파일로 변환.
- **주요 스크립트**:
    - `csv_day_to_year.py`, `csv_month_to_year.py`: 연도별/월별, 일별로 파편화된 CSV 파일들을 표준 컬럼(`standard_columns`)에 맞춰 병합하고 정리.
    - `csv_change_parquet.py`: 정리된 CSV 파일을 연도별/월별 Parquet 파일로 변환하여 `data/parquet/{연도}/` 폴더에 저장.

### 4.3. 2단계: 데이터 마트 생성 (`src/data_mart`)
- **목표**: 표준화된 Parquet 데이터를 분석 목적에 맞게 사전 집계하여 성능 최적화.
- **주요 스크립트 및 결과물**:
    1.  **시간 분석용 (`01_year_month_day`)**:
        - `time_analysis_preprocessing.py`: `data/parquet`의 전체 데이터를 읽어 월별/일별/시간대별 이용 건수를 집계.
        - **결과물**: `data/01/summary_monthly_{연도}.parquet`, `data/01/summary_daily_hourly_{연도}.parquet`
    2.  **거리/시간 분석용 (`02_distance_time`)**:
        - `hole_distance_time_preprocessing.py`: 전체 원본 데이터에서 이용 시간/거리/요일 정보만 추출하여 연도별 파일 생성.
        - `distnace_time_data_preprocessing.py`: 위 파일에 대해 이상치(outlier)를 제거하고, 연도별 평균/중앙값 등 요약 통계를 계산.
        - **결과물**: `data/02/yearly_summary.parquet`, `data/02/yearly_detailed_summary.json`
    3.  **대여소/경로 분석용 (`03_rental_office`)**:
        - `rental_office_data_preprocessing.py`: 전체 원본 데이터를 스트리밍 방식으로 처리하여 대여소별 총 대여/반납 건수 및 대여소 간 이동 경로별 이용 건수를 집계.
        - **결과물**: `data/03/station_summary.parquet`, `data/03/route_summary.parquet`

---

## 5. 핵심 데이터 분석 (`src/analyse`)

`src/analyse` 디렉토리는 Streamlit 대시보드와는 별개로, 특정 주제에 대한 심층 분석을 수행하고 정적 시각화 결과물(이미지, HTML 지도 등)을 생성하는 스크립트를 포함합니다. 이 분석 결과들은 최종 보고서(`insight.html`)의 핵심 근거 자료로 활용됩니다.

### 5.1. `population_analyse.py`: 인구-수요 상관관계 분석
- **목표**: 서울시 인구 증감률과 따릉이 연간 이용량 증감률 간의 거시적 연관성을 파악합니다.
- **분석 과정**:
    1. `data/01`의 월별 요약 데이터를 기반으로 연도별 총 대여 건수를 집계합니다.
    2. `data/registered_population.csv`에서 서울시 연간 총 인구수 데이터를 추출 및 전처리합니다.
    3. 두 데이터의 연도별 증감률(%)을 계산하고, 2021년 이후의 데이터를 기준으로 피어슨 상관계수를 도출합니다.
- **주요 산출물**:
    - `matplotlib`으로 생성된 연도별 증감률 비교 꺾은선 및 막대그래프 (`report_images/correlation_chart.png`).

### 5.2. `routes_analyse.py`: 경로 및 이용 행태 분석
- **목표**: 사용자의 이동 패턴을 '편도'와 '왕복'으로 구분하여 분석하고, 시민들의 주요 이동 경로를 시각화합니다.
- **분석 과정**:
    1. `data/03/route_summary.parquet` 데이터를 사용하여 전체 이용 건수 중 편도와 왕복의 비율을 계산합니다.
    2. **왕복 이용**: 이용 건수 상위 왕복 경로는 주요 '레저/관광 코스'로 간주하고 Top 10을 추출합니다.
    3. **편도 이용**: 이용 건수 상위 편도 경로는 주요 '출퇴근/통학' 등 생활 동선으로 간주하고 Top 10을 추출합니다.
- **주요 산출물**:
    - 이용 형태(편도/왕복) 비율을 나타내는 파이 차트 (`report_images/pie_chart_trip_types.png`).
    - `folium`을 활용하여 Top 1000 편도 경로의 흐름과 출발/도착지 핫스팟을 시각화한 HTML 지도 (`maps/final_routes_map_osm.html`).

### 5.3. `station_analyse.py`: 대여소 중심 분석
- **목표**: 대여소별 이용 현황을 분석하여 핵심 대여소를 식별하고, '자전거 쏠림 현상'(재고 불균형)을 정량적으로 분석합니다.
- **분석 과정**:
    1. `data/03/station_summary.parquet` 데이터를 기반으로 총 이용 건수 기준 Top 20 인기 대여소를 선정하고, 전체 이용량 대비 비중을 계산합니다.
    2. 대여소별 '순이동량' (총 대여 건수 - 총 반납 건수)을 계산하여 자전거 유출(공급 필요) 및 유입(수거 필요)이 가장 심한 Top 20 대여소를 식별합니다.
    3. '쏠림 비율' (순이동량 / 총 이용건수)을 계산하여, 이용량 대비 운영 비효율이 가장 심각한 대여소를 분석합니다.
- **주요 산출물**:
    - Top 20 대여소의 이용량 비중 파이 차트 (`report_images/pie_chart_top20Pstations.png`).
    - `folium`을 활용하여 대여소별 순이동량을 유출(🔴)/유입(🔵)으로 구분하여 시각화한 인터랙티브 HTML 지도 (`maps/interactive_station_map.html`).

### 5.4. `distance_time_analyse.py`: 이용 시간 및 거리 분석
- **목표**: 연도별 평균적인 이용 시간과 거리의 변화 추이를 분석하여 따릉이 이용 행태의 거시적 변화를 파악합니다.
- **분석 과정**:
    1. `data/02/yearly_detailed_summary.json` 데이터를 사용하여 연도별 평균 이용 시간 및 거리를 계산합니다.
    2. 요일 데이터를 기반으로 주중과 주말의 평균 이용 시간 및 거리를 비교 분석합니다.
- **주요 산출물**:
    - `matplotlib`으로 생성된 연도별/주중-주말별 이용 시간 및 거리 비교 그래프.

---

## 6. 대시보드 애플리케이션

Streamlit을 기반으로 구축되었으며, 사용자가 직접 필터를 조작하여 분석 결과를 탐색할 수 있다.

### 6.1. 실행 방법
프로젝트 루트 디렉토리에서 다음 명령어를 실행한다.
```bash
streamlit run src/main.py
```

### 6.2. 페이지 구성 (`src/main.py`, `src/pages/`)
- **`main.py` (메인 페이지)**: 프로젝트 소개, 목표, 사용 데이터셋에 대한 개요를 제공.
- **`01_time_analysis_visualization.py`**:
    - 연도별 월간 이용량 추이 비교.
    - 특정 날짜 또는 특정 월의 시간대별 이용 패턴 비교.
- **`02_distance_time_visualization.py`**:
    - 연도별 평균 이용 시간 및 거리 변화 추이 분석.
    - 주중 vs 주말 이용 패턴 비교.
    - 시간-거리 간의 상관관계 분석.
- **`03_geo_analysis_visualization.py`**:
    - 인기 대여소 Top 20 및 이용량 비중 시각화.
    - 자전거 쏠림 현상(순이동량) 분석 및 지도 시각화.
    - 편도/왕복 이용 비율 및 인기 경로 분석, 지도 시각화.
- **`04_population_analysis_visualization.py`**:
    - 연도별 따릉이 이용 증감률과 서울시 인구 증감률을 비교 분석.
- **`05_conclusion.py`**:
    - 모든 분석 결과를 종합한 최종 보고서(`insight.html`)를 대시보드 내에 임베드하여 표시.

---

## 7. 주요 산출물

- **인터랙티브 대시보드**: `streamlit run src/main.py`로 실행.
- **정적 지도**: `maps/` 폴더 내 HTML 파일.
    - `interactive_station_map.html`: 대여소별 순이동량 지도.
    - `final_routes_map_osm.html`: 주요 이동 경로 및 핫스팟 지도.
- **종합 분석 보고서**: `insight.html`.
- **분석용 데이터 마트**: `data/01`, `data/02`, `data/03` 폴더 내 Parquet/JSON 파일.

