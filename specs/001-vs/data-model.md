# Data Model for Seoul Public Bicycle "Ddareungi" Data Analysis

## 1. Ddareungi Usage Data

Represents aggregated bicycle rental trip data.

**Source**: `data/*.parquet`

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