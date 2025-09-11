import matplotlib.pyplot as plt
import numpy as np
import folium 

from src.load_data.station_route_data_load import load_station_summary_data


def visualize_top_20_pie_chart(station_df):
    """
    Top 20 대여소와 나머지 대여소의 이용량 비중을 파이 차트로 시각화합니다.
    """
    if station_df.empty:
        print("데이터가 없어 파이 차트를 생성할 수 없습니다.")
        return

    # --- 1. 데이터 준비 ---
    total_usage = station_df['총_이용건수'].sum()
    top_20_usage = station_df.sort_values(by='총_이용건수', ascending=False).head(20)['총_이용건수'].sum()
    other_usage = total_usage - top_20_usage

    # --- 2. 차트 데이터 및 스타일 설정 ---
    sizes = [top_20_usage, other_usage]
    labels = [f'Top 20 대여소\n({top_20_usage:,.0f} 건)', f'나머지 {len(station_df)-20:,}개 대여소\n({other_usage:,.0f} 건)']
    colors = ['#ff9999', '#c2c2c2'] # 강조색과 무채색
    explode = (0.1, 0)  # Top 20 부분을 약간 떼어내어 강조

    # --- 3. 파이 차트 생성 ---
    plt.figure(figsize=(10, 8)) # 차트 크기 설정
    
    # autopct: 각 슬라이스에 표시될 퍼센트 형식. 소수점 첫째 자리까지 표시
    # startangle: 차트가 그려지기 시작하는 각도
    patches, texts, autotexts = plt.pie(
        sizes, 
        explode=explode, 
        labels=labels, 
        colors=colors,
        autopct='%1.1f%%', 
        shadow=True, 
        startangle=140,
        textprops={'fontsize': 12} # 라벨 폰트 크기
    )
    
    # 퍼센트 텍스트(autotexts)를 더 굵고 잘 보이게 설정
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_weight('bold')
    
    plt.title('Top 20 대여소 이용량 비중', fontsize=16, pad=20)
    plt.axis('equal')  # 파이 차트가 원형을 유지하도록 설정
    
    print("\n파이 차트를 생성합니다...")
    plt.show()


def analyze_net_flow(station_df):
    print("\n" + "="*50)
    print("🌊 자전거 쏠림 현상(순이동량) 심층 분석")
    print("="*50)

    # --- 1. 자전거 유출 Top 20 (항상 부족한 곳) ---
    # 순이동량(대여-반납)이 큰 양수(+)인 경우 -> 대여가 반납보다 훨씬 많음
    outflow_top_20 = station_df.sort_values(by='순이동량', ascending=False).head(20)
    
    # 분석에 필요한 핵심 컬럼만 선택하여 보기 좋게 만듭니다.
    outflow_display = outflow_top_20[[
        '대여소_ID', '총_대여건수', '총_반납건수', '순이동량', '주소1'
    ]].copy()
    outflow_display.index = range(1, 21)

    print("\n--- 📤 자전거 유출 Top 20 (재배치 공급 필요) ---")
    print("순이동량(대여-반납)이 높은 순서입니다.")
    print(outflow_display)
    print("\n >> 해석: 위 대여소들은 반납되는 자전거보다 대여되는 자전거가 훨씬 많아,")
    print("    자전거가 항상 부족해지는 경향이 있습니다. 주기적인 공급이 필요합니다.")

    # --- 2. 자전거 유입 Top 20 (항상 쌓이는 곳) ---
    # 순이동량(대여-반납)이 큰 음수(-)인 경우 -> 반납이 대여보다 훨씬 많음
    inflow_top_20 = station_df.sort_values(by='순이동량', ascending=True).head(20)
    
    inflow_display = inflow_top_20[[
        '대여소_ID', '총_대여건수', '총_반납건수', '순이동량', '주소1'
    ]].copy()
    inflow_display.index = range(1, 21)

    print("\n--- 📥 자전거 유입 Top 20 (재배치 수거 필요) ---")
    print("순이동량(대여-반납)이 낮은 순서입니다.")
    print(inflow_display)
    print("\n >> 해석: 위 대여소들은 대여되는 자전거보다 반납되는 자전거가 훨씬 많아,")
    print("    거치대가 부족해지는 경향이 있습니다. 주기적인 수거가 필요합니다.")

def visualize_net_flow_on_map(station_df):
    """
    Folium을 사용하여 대여소별 순이동량을 '유출', '유입', '균형' 레이어로 나누어
    상호작용 가능한 지도 위에 시각화합니다.
    """
    print("\n" + "="*50)
    print("🗺️ 상호작용 지도 시각화: 자전거 쏠림 현상 지역 분석")
    print("="*50)
    
    # --- 1. 지도 생성 및 레이어 그룹(FeatureGroup) 준비 ---
    map_center = [37.5665, 126.9780]
    m = folium.Map(location=map_center, zoom_start=12, tiles='CartoDB positron')

    # 각 색상(그룹)을 담을 별도의 레이어를 생성
    outflow_layer = folium.FeatureGroup(name='🔴 자전거 유출 (공급 필요)', show=True)
    inflow_layer = folium.FeatureGroup(name='🔵 자전거 유입 (수거 필요)', show=True)
    # 균형 상태는 기본적으로 꺼두어, 문제 지점을 먼저 보도록 유도
    balanced_layer = folium.FeatureGroup(name='⚫ 균형 상태', show=False) 
    
    m.add_child(outflow_layer)
    m.add_child(inflow_layer)
    m.add_child(balanced_layer)
    
    # --- 2. 데이터 준비 ---
    map_data = station_df.dropna(subset=['위도', '경도']).copy()

    # --- 3. 지도에 원(CircleMarker) 추가 (조건에 따라 다른 레이어에 추가) ---
    print("지도 위에 대여소 그룹별 데이터를 표시합니다...")
    for idx, row in map_data.iterrows():
        # 원의 크기 결정 (이전과 동일)
        radius = 5 + abs(row['순이동량']) / 5000
        radius = min(radius, 20)
        
        # 팝업 HTML 구성 (이전과 동일)
        popup_html = f"""
        <b>대여소 ID:</b> {row['대여소_ID']}<br>
        <b>주소:</b> {row['주소1']}<br>
        <hr>
        <b>총 대여:</b> {row['총_대여건수']:,} 건<br>
        <b>총 반납:</b> {row['총_반납건수']:,} 건<br>
        <b>순이동량:</b> <b>{row['순이동량']:+,}</b>
        """
        popup = folium.Popup(popup_html, max_width=300)

        # --- 💡 핵심 변경: 순이동량 값에 따라 마커를 해당하는 레이어에 추가 ---
        if row['순이동량'] > 5000:
            folium.CircleMarker(
                location=[row['위도'], row['경도']], radius=radius, color='red',
                fill=True, fill_color='red', fill_opacity=0.6, popup=popup
            ).add_to(outflow_layer) # 빨간색 레이어에 추가
        elif row['순이동량'] < -5000:
            folium.CircleMarker(
                location=[row['위도'], row['경도']], radius=radius, color='blue',
                fill=True, fill_color='blue', fill_opacity=0.6, popup=popup
            ).add_to(inflow_layer) # 파란색 레이어에 추가
        else:
            folium.CircleMarker(
                location=[row['위도'], row['경도']], radius=radius, color='gray',
                fill=True, fill_color='gray', fill_opacity=0.6, popup=popup
            ).add_to(balanced_layer) # 회색 레이어에 추가

    # --- 4. 레이어 컨트롤 추가 및 파일 저장 ---
    folium.LayerControl(collapsed=False).add_to(m)
    map_filename = 'interactive_station_map.html'
    m.save(map_filename)
    print(f"\n✅ 상호작용 지도 생성 완료! '{map_filename}' 파일을 웹 브라우저로 열어 확인하세요.")
    print("   - 지도 우측 상단 컨트롤 박스에서 각 그룹(유출/유입/균형)을 켜고 끌 수 있습니다.")


def analyze_net_flow_ratio(station_df):
    """
    총 이용량 대비 순이동량 비율을 분석하여 운영 비효율이 심각한 대여소를 찾습니다.
    """
    print("\n" + "="*50)
    print("🔬 운영 비효율 분석 (이용량 대비 쏠림 비율)")
    print("="*50)

    # --- 1. '쏠림_비율' 컬럼 계산 ---
    # 순이동량 / 총_이용건수. 0으로 나누는 오류를 방지하기 위해 np.divide 사용
    # 총_이용건수가 0인 경우, 결과는 0이 됨
    station_df['쏠림_비율'] = np.divide(
        station_df['순이동량'], 
        station_df['총_이용건수'], 
        out=np.zeros_like(station_df['순이동량'], dtype=float), 
        where=(station_df['총_이용건수'] != 0)
    )

    # --- 2. "빌려가기만 하는" 대여소 Top 10 (유출 비효율) ---
    # 쏠림_비율이 +1에 가까울수록 -> 반납 없이 대여만 일어남
    # 단, 총 이용건수가 너무 적으면(예: 100건 미만) 우연일 수 있으므로 최소 기준 설정
    min_usage_threshold = 100
    high_outflow_ratio = station_df[station_df['총_이용건수'] >= min_usage_threshold]
    high_outflow_ratio = high_outflow_ratio.sort_values(by='쏠림_비율', ascending=False).head(10)
    
    outflow_ratio_display = high_outflow_ratio[[
        '대여소_ID', '총_이용건수', '순이동량', '쏠림_비율', '주소1'
    ]].copy()
    outflow_ratio_display.index = range(1, 11)

    print("\n--- ⚠️ 공급 집중 관리 대상 Top 10 ('편도 대여' 특화 대여소) ---")
    print(f"(총 이용건수 {min_usage_threshold}건 이상, 쏠림 비율 높은 순)")
    print(outflow_ratio_display.to_string(formatters={'쏠림_비율': '{:.2%}'.format}))
    print("\n >> 해석: 위 대여소들은 '출발지'로서의 역할이 매우 뚜렷한 곳입니다.")
    print("    이곳의 이용자들은 명확한 목적지를 향해 편도 이용을 하는 경향이 강합니다.")
    print("    따라서 이곳은 **자전거 공급의 핵심 거점**으로, 재배치 트럭이")
    print("    정기적으로 충분한 수량의 자전거를 채워넣는 **집중 커버가 필수적**입니다.")

    # --- 3. "반납만 하는" 대여소 Top 10 (유입 비효율) ---
    # 쏠림_비율이 -1에 가까울수록 -> 대여 없이 반납만 일어남
    high_inflow_ratio = station_df[station_df['총_이용건수'] >= min_usage_threshold]
    high_inflow_ratio = high_inflow_ratio.sort_values(by='쏠림_비율', ascending=True).head(10)
    
    inflow_ratio_display = high_inflow_ratio[[
        '대여소_ID', '총_이용건수', '순이동량', '쏠림_비율', '주소1'
    ]].copy()
    inflow_ratio_display.index = range(1, 11)

    print("\n--- ⚠️ 수거 집중 관리 대상 Top 10 ('편도 반납' 특화 대여소) ---")
    print(f"(총 이용건수 {min_usage_threshold}건 이상, 쏠림 비율 낮은 순)")
    print(inflow_ratio_display.to_string(formatters={'쏠림_비율': '{:.2%}'.format}))
    print("\n >> 해석: 위 대여소들은 '최종 목적지'로서의 역할이 매우 뚜렷한 곳입니다.")
    print("    많은 이용자들이 이곳을 향해 따릉이를 이용하며, 이는 이곳이 중요한 도착지임을 의미합니다.")
    print("    따라서 이곳은 **자전거 수거의 핵심 거점**으로, 재배치 트럭이")
    print("    정기적으로 방문하여 넘치는 자전거를 회수하고 거치대 공간을 확보하는")
    print("    **선제적인 관리가 서비스 만족도를 크게 향상**시킬 수 있습니다.")

def analyze_station_rankings():
    print("--- 대여소별 이용 현황 분석 시작 ---")
    
    station_df = load_station_summary_data()
    
    if station_df.empty:
        return

    # --- 1. Top 20 대여소 ---
    top_20_stations = station_df.sort_values(by='총_이용건수', ascending=False).head(20)
    top_20_display = top_20_stations[['대여소_ID', '총_이용건수', '주소1', '주소2']].copy()
    top_20_display.index = range(1, 21)
    
    print("\n--- 🏆 인기 대여소 Top 20 ---")
    print(f"(전체 기간 동안 총 대여+반납 건수 기준)")
    top_20_display['주소2'].fillna('', inplace=True)
    print(top_20_display)

    # --- 2. Top 20 비중 분석 ---
    total_usage = station_df['총_이용건수'].sum()
    top_20_usage = top_20_stations['총_이용건수'].sum()
    top_20_percentage = (top_20_usage / total_usage) * 100
    
    print("\n--- 📊 Top 20 비중 분석 ---")
    print(f"전체 대여소 수: {len(station_df):,} 개")
    print(f"전체 이용 건수: {total_usage:,.0f} 건")
    print(f"Top 20 이용 건수: {top_20_usage:,.0f} 건")
    print(f"Top 20 대여소가 전체 이용량의 **{top_20_percentage:.2f}%**를 차지합니다.")
    
    visualize_top_20_pie_chart(station_df)

    # 순간 이동량 분석 함수
    analyze_net_flow(station_df)

    # 지도 시각화 함수
    visualize_net_flow_on_map(station_df)

    # 운영 비효율
    analyze_net_flow_ratio(station_df)


if __name__ == '__main__':
    plt.rc('font', family='NanumGothic')
    plt.rcParams['axes.unicode_minus'] = False
    analyze_station_rankings()