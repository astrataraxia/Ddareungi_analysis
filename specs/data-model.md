# Data Model for Seoul Public Bicycle "Ddareungi" Data Analysis

## 1. Ddareungi Usage Data

Represents aggregated bicycle rental trip data.

**Source**: `data/paraquet/{YEAR}/*.parquet`

**Attributes**:

# parquet
- `시작_대여소명`: Name of the starting rental station. (object)
- `종료_대여소_ID`: Unique identifier for the ending rental station. (object)
- `종료_대여소명`: Name of the ending rental station. (object)
- **Note on Missing Values**: `종료_대여소_ID` can contain 'X' for missing values, in which case `종료_대여소명` will be empty.
- `전체_건수`: Total number of rentals for the aggregated period. (int64)
- `전체_이용_분`: Total usage duration in minutes for the aggregated period. (int64)
- `전체_이용_거리`: Total usage distance in meters for the aggregated period. (float64)

# parquet
- index | column
-   0    `기준_날짜` (int64) : Date. 20200101 (YYYYmmdd)
-   1    `집계_기준` (object) : 
-   2    `기준_시간대` (int64) : Time slot for aggregation, represented as inter (e.g. 0 for 00:00, 5 for 00:05, ..., 2335 for 23:35)
-   3    `시작_대여소_ID` (object) : starting rental station. (ref: Bicycle Station Data.대여소_ID)
-   4    `시작_대여소명` (object) : Name of the starting rental station 
- **Note on Missing Values**: `시작_대여소명` has many None value,
-   5    `종료_대여소_ID` (object) : ending rental staation (참조: Bicycle Station Data.대여소_ID)
- **Note on Missing Values**: `종료_대여소_ID` can contain 'X' for None value, in which case `종료_대여소명` will be None.
-   6    `종료_대여소명` (object) : Name of the ending rental station
- **Note on Missing Values**: `종료_대여소명` has many None value,
-   7    `전체_건수` (int64) : Total number of rentals for the aggregated preiod.
-   8    `전체_이용_분` (float64) : Total usage duration in minutes (e.g. 10 -> 10 miniutes, 400 -> 400 miniutes)
-   9    `전체_이용_거리` (float64) : Total usage distance in meters


## 2. Bicycle Station Data

Represents a public bicycle rental station.

**Source**: `data/bcycle_master_location.csv`

**Attributes**:
- `대여소_ID`: Unique identifier for the station. (String)
- `주소1`: Primary address of the station. (String)
- `주소2`: Secondary address or detailed location of the station. (String)
- `위도`: Latitude coordinate of the station. (Float)
- `경도`: Longitude coordinate of the station. (Float)
-**Note on Missing vlaues**: Some kind of `위도`, `경도` value is None

## 3. Registered Population Data

Represents the registered population for different administrative districts in Seoul.

**Source**: `data/registered_population.csv`

**Attributes**:
- `동별(1)`: Classification criterion (e.g., '합계', '동별'). (String)
- `동별(2)`: Administrative district (e.g., '소계', '종로구', '중구'). (String)
- `[YYYY Q/Q]` columns: Columns representing population count for each year and quarter (e.g., `2020 1/4`, `2025 1/2`, `2024` ). (Integer)

**Note**: This file has a 2-line multi-level header. The first line indicates the year and quarter, and the second line indicates '계 (명)' for population counts.

## 4. 요약 데이터 (Summarized Data)

기존 parquet 데이터를 분석 목적에 맞게 가공하여 생성한 요약 데이터입니다.

### 4.1. 일별/시간대별 요약 (Daily/Hourly Summary)

**Source**: `data/summary/summary_daily_hourly_{YEAR}.parquet`

**생성 방식**: `data/paraquet/{YEAR}/*.parquet` 원본 데이터에서 `기준_날짜`, `기준_시간대` 정보를 추출하고, 시간대별 `전체_건수`를 합산하여 생성합니다. 이를 통해 각 시간대의 총 대여 건수를 나타냅니다.

**Attributes**:
- `year`: 년도
- `month`: 월
- `day`: 일
- `hour`: 시간
- `total_rentals`: 총 대여 건수

### 4.2. 월별 요약 (Monthly Summary)

**Source**: `data/summary/summary_monthly_{YEAR}.parquet`

**생성 방식**: `data/paraquet/{YEAR}/*.parquet` 원본 데이터에서 `기준_날짜` 정보를 이용하여 월별 `전체_건수`를 합산하여 생성합니다. 월별 총 대여 건수를 나타냅니다.

**Attributes**:
- `year`: 년도
- `month`: 월
- `total_rentals`: 총 대여 건수

### 4.3. 이용 시간/거리 분석 데이터 (Usage Time/Distance Analysis Data)

**Source**: `data/02/distance_time_{YEAR}.parquet`

**생성 방식**: `data/parquet/{YEAR}/*.parquet` 원본 데이터에서 `기준_날짜`, `전체_이용_분`, `전체_이용_거리` 컬럼을 추출합니다. `기준_날짜`는 `요일` 정보(월요일=0, 일요일=6)를 생성하는 데 사용된 후 제거됩니다. 결측치와 이상치가 제거된 정제된 데이터입니다.

**Attributes**:
- `전체_이용_분` (float64): 총 이용 시간 (분)
- `전체_이용_거리` (float64): 총 이동 거리 (미터)
- `요일` (int64): 요일 정보 (월요일=0, 일요일=6)

---

**Source**: `data/02/yearly_summary.parquet`

**생성 방식**: `distance_time_{YEAR}.parquet` 데이터를 연도별로 그룹화하여 주요 통계(평균, 중앙값, 표준편차 등)를 계산합니다.

**Attributes**:
- `year` (int64): 연도
- `total_records` (int64): 유효 데이터 건수
- `avg_time` (float64): 평균 이용 시간 (분)
- `avg_distance` (float64): 평균 이용 거리 (미터)
- `median_time` (float64): 이용 시간의 중앙값 (분)
- `median_distance` (float64): 이용 거리의 중앙값 (미터)
- `std_time` (float64): 이용 시간의 표준편차 (분)
- `std_distance` (float64): 이용 거리의 표준편차 (미터)

---

**Source**: `data/02/yearly_detailed_summary.json`

**생성 방식**: `distance_time_{YEAR}.parquet` 데이터를 기반으로 `yearly_summary.parquet`의 통계를 포함하여, 요일별 평균 이용 시간 및 거리 등 더 상세한 정보를 JSON 형식으로 저장합니다.

**Attributes**:
- `weekday_avg_time` (dict): 요일별 평균 이용 시간
- `weekday_avg_distance` (dict): 요일별 평균 이용 거리
- (`yearly_summary.parquet`의 모든 필드 포함)

### 4.4. 대여소 및 경로 분석 데이터 (Station and Route Analysis Data)

**Source**: `data/03/station_summary.parquet`

**생성 방식**: 모든 기간의 원본 데이터를 스트리밍 방식으로 처리하여, 각 대여소별 총 대여 건수와 총 반납 건수를 집계합니다. 이 후 마스터 대여소 정보(`bcycle_master_location.csv`)와 결합하여 주소 및 좌표 정보를 추가합니다.

**Attributes**:
- `대여소_ID` (object): 대여소 고유 ID
- `주소1` (object): 대여소의 기본 주소
- `주소2` (object): 대여소의 상세 주소
- `위도` (float64): 위도 좌표
- `경도` (float64): 경도 좌표
- `총_대여건수` (int64): 해당 대여소에서 출발한 총 대여 건수
- `총_반납건수` (int64): 해당 대여소에 도착한 총 반납 건수
- `총_이용건수` (int64): 총 대여 + 총 반납 건수
- `순이동량` (int64): 총 대여 - 총 반납 건수 (양수: 유출, 음수: 유입)

---

**Source**: `data/03/route_summary.parquet`

**생성 방식**: 모든 기간의 원본 데이터를 스트리밍 방식으로 처리하여, (시작 대여소, 종료 대여소) 쌍으로 그룹화하여 경로별 총 이용 건수를 집계합니다. 이후 마스터 대여소 정보를 결합하여 각 경로의 시작점과 종료점의 주소 및 좌표 정보를 추가합니다.

**Attributes**:
- `시작_대여소_ID` (object): 출발 대여소 ID
- `종료_대여소_ID` (object): 도착 대여소 ID
- `이용_건수` (int64): 해당 경로의 총 이용 건수
- `이용_형태` (object): '편도' 또는 '왕복' (시작점과 도착점이 동일한 경우 '왕복')
- `주소1_시작` / `주소2_시작` / `위도_시작` / `경도_시작`: 출발지 정보
- `주소1_종료` / `주소2_종료` / `위도_종료` / `경도_종료`: 도착지 정보

### 4.5 서울시 인구증감에 따른 따릉이 사용자 변화

**Source** `data/01/summary_monthly_{Year}.parquet`
**Source** `data/registered_population.csv`

- 기존에 Preprocessing 하였던 자료들로 결과 도출이 가능하기에 이대로 사용한다.