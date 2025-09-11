import pandas as pd
import matplotlib.pyplot as plt
import folium 
from folium.plugins import HeatMap
import branca.colormap as cm 

from src.load_data.station_route_data_load import load_route_summary_data

def visualize_trip_type_ratio(route_df):
    """
    전체 이용 건수에서 편도와 왕복이 차지하는 비율을 파이 차트로 시각화합니다.
    """
    if route_df.empty:
        print("데이터가 없어 파이 차트를 생성할 수 없습니다.")
        return

    # --- 1. 데이터 집계 ---
    usage_by_type = route_df.groupby('이용_형태')['이용_건수'].sum()
    
    # --- 2. 차트 데이터 및 스타일 설정 ---
    sizes = usage_by_type.values
    labels = [f'{index}\n({value:,.0f} 건)' for index, value in usage_by_type.items()]
    colors = ['#66b3ff', '#ffcc99'] # 파란색 계열(편도), 주황색 계열(왕복)
    explode = (0.05, 0) # 편도 부분을 약간 강조

    # --- 3. 파이 차트 생성 ---
    plt.figure(figsize=(10, 8))
    
    patches, texts, autotexts = plt.pie(
        sizes, 
        explode=explode, 
        labels=labels, 
        colors=colors,
        autopct='%1.1f%%', 
        shadow=True, 
        startangle=90,
        textprops={'fontsize': 12}
    )
    
    for autotext in autotexts:
        autotext.set_color('black')
        autotext.set_weight('bold')
    
    plt.title('전체 따릉이 이용 형태 (편도 vs 왕복) 비율', fontsize=16, pad=20)
    plt.axis('equal')
    
    print("\n이용 형태 비율 파이 차트를 생성합니다...")
    plt.show()

def visualize_final_route_map(route_df, top_n=1000):
    """
    OpenStreetMap을 배경으로 Top N 인기 경로와 핫스팟을 시각화합니다.
    """
    print("\n" + "="*50)
    print(f"🗺️ 최종 지도 시각화: OpenStreetMap + Top {top_n} 경로 & 핫스팟")
    print("="*50)

    # --- 1. 데이터 준비 ---
    one_way_trips = route_df[route_df['이용_형태'] == '편도'].copy()
    top_routes = one_way_trips.sort_values(by='이용_건수', ascending=False).head(top_n)
    required_coords = ['위도_시작', '경도_시작', '위도_종료', '경도_종료']
    map_data = top_routes.dropna(subset=required_coords).copy()
    
    if map_data.empty:
        print(f"지도에 표시할 Top {top_n} 경로 데이터가 없습니다.")
        return

    # --- 2. 지도 생성 기본 타일 사용) ---
    map_center = [37.5665, 126.9780]  # 서울 시청 좌표
    m = folium.Map(location=map_center, zoom_start=12, tiles="CartoDB positron")

    # --- 3. 데이터 시각화 레이어 그룹 ---
    flow_map_layer = folium.FeatureGroup(name=f'Top {top_n} 인기 경로', show=True).add_to(m)
    heatmap_start_layer = folium.FeatureGroup(name='출발지 핫스팟', show=False).add_to(m)
    heatmap_end_layer = folium.FeatureGroup(name='도착지 핫스팟', show=False).add_to(m)

    # --- 4. 인기 경로 플로우 맵 ---
    min_usage, max_usage = map_data['이용_건수'].min(), map_data['이용_건수'].max()
    colormap = cm.LinearColormap(['yellow', 'orange', 'red'], vmin=min_usage, vmax=max_usage)
    map_data['rank'] = range(1, len(map_data) + 1)

    print("지도 위에 인기 경로(Flow Map)를 표시합니다...")
    for idx, row in map_data.iterrows():
        start_coords = [row['위도_시작'], row['경도_시작']]
        end_coords = [row['위도_종료'], row['경도_종료']]
        weight = max(10 - (row['rank'] / top_n) * 9, 1)

        popup_html = f"<b>순위: {row['rank']}위</b><hr>" \
                     f"<b>경로:</b> {row['주소1_시작']} → {row['주소1_종료']}<br>" \
                     f"<b>이용 건수: {row['이용_건수']:,} 건</b>"
        popup = folium.Popup(popup_html, max_width=400)

        folium.PolyLine(
            locations=[start_coords, end_coords],
            color=colormap(row['이용_건수']),
            weight=weight,
            opacity=0.7,
            popup=popup
        ).add_to(flow_map_layer)

    m.add_child(colormap)

    # --- 5. 출발/도착지 히트맵 ---
    print("출발지 및 도착지 핫스팟(Heatmap)을 생성합니다...")
    start_heatmap_data = map_data[['위도_시작', '경도_시작', '이용_건수']].values.tolist()
    end_heatmap_data = map_data[['위도_종료', '경도_종료', '이용_건수']].values.tolist()
    HeatMap(start_heatmap_data, radius=15).add_to(heatmap_start_layer)
    HeatMap(end_heatmap_data, radius=15).add_to(heatmap_end_layer)
    
    # --- 6. 레이어 컨트롤 및 저장 ---
    folium.LayerControl(collapsed=False).add_to(m)
    map_filename = 'final_routes_map_osm.html'
    m.save(map_filename)
    print(f"\n✅ 최종 경로 지도 생성 완료! '{map_filename}' 파일을 열어 확인하세요.")


def analyze_route_patterns():
    """
    경로 요약 데이터를 분석하여 편도/왕복 이용 행태와 인기 경로를 찾습니다.
    (수정된 컬럼 이름 반영)
    """
    print("--- 경로 기반 이용 행태 분석 시작 ---")

    route_df = load_route_summary_data()
    if route_df.empty:
        return

    visualize_trip_type_ratio(route_df)

    # --- 2. 전체 이용 형태 분석 (편도 vs 왕복) ---
    usage_by_type = route_df.groupby('이용_형태')['이용_건수'].sum()
    total_routes_usage = usage_by_type.sum()
    
    print("\n" + "="*50)
    print("📊 전체 이용 형태 분석 (편도 vs 왕복)")
    print("="*50)
    print(f"총 이용 건수: {total_routes_usage:,.0f} 건")
    for trip_type, count in usage_by_type.items():
        percentage = (count / total_routes_usage) * 100
        print(f" - {trip_type} 이용: {count:,.0f} 건 ({percentage:.2f}%)")
    print("\n >> 해석: 전체 따릉이 이용 중 편도와 왕복의 비율을 통해,")
    print("    시민들이 따릉이를 교통수단으로 더 많이 사용하는지,")
    print("    혹은 레저/운동 목적으로 더 많이 사용하는지에 대한 큰 그림을 파악할 수 있습니다.")


    # --- 3. 인기 왕복 경로 Top 10 (주요 레저/운동 코스) ---
    round_trips = route_df[route_df['이용_형태'] == '왕복'].copy()
    top_10_round_trips = round_trips.sort_values(by='이용_건수', ascending=False).head(10)

    top_10_round_trips['주소2_시작'] = top_10_round_trips['주소2_시작'].fillna('')
    top_10_round_trips['출발지_주소'] = top_10_round_trips['주소1_시작'] + " " + top_10_round_trips['주소2_시작']
    
    round_trip_display = top_10_round_trips[['출발지_주소', '이용_건수']].copy()
    round_trip_display.index = range(1, 11)

    print("\n" + "="*50)
    print("🏞️ 주요 관광 코스 (인기 왕복 경로 Top 10)")
    print("="*50)
    print(round_trip_display)
    print("\n >> 해석: 왕복 이용이 많은 대여소는 주로 한강공원, 서울숲, 호수공원 등")
    print("    시민들이 운동이나 여가를 즐기기 위해 방문하는 장소일 가능성이 높습니다.")
    print("    이러한 곳들은 주말이나 저녁 시간에 자전거 수요가 몰릴 것을 예상할 수 있습니다.")


    # --- 4. 인기 편도 경로 Top 10 (주요 이동 경로) ---
    one_way_trips = route_df[route_df['이용_형태'] == '편도'].copy()
    top_10_one_way = one_way_trips.sort_values(by='이용_건수', ascending=False).head(10)
    
    top_10_one_way['주소2_시작'] = top_10_one_way['주소2_시작'].fillna('')
    top_10_one_way['주소2_종료'] = top_10_one_way['주소2_종료'].fillna('')
    top_10_one_way['출발지'] = top_10_one_way['주소1_시작'] + " " + top_10_one_way['주소2_시작']
    top_10_one_way['도착지'] = top_10_one_way['주소1_종료'] + " " + top_10_one_way['주소2_종료']
    
    one_way_display = top_10_one_way[['출발지', '도착지', '이용_건수']].copy()
    one_way_display.index = range(1, 11)

    print("\n" + "="*50)
    print("주요 이동 경로 (인기 편도 경로 Top 10)")
    print("="*50)
    print(one_way_display)
    print("\n >> 해석: 편도 이용이 많은 경로는 시민들의 주요 '생활 동선'을 보여줍니다.")
    print("    주로 (주거지역 ↔ 지하철역), (지하철역 ↔ 업무지구/대학교)와 같이")
    print("    출퇴근 및 통학을 위한 '라스트 마일(Last-mile)' 교통수단으로 활용되는 패턴입니다.")

    visualize_final_route_map(route_df)


if __name__ == '__main__':
    # 한글 폰트 설정
    plt.rc('font', family='NanumGothic')
    plt.rcParams['axes.unicode_minus'] = False
    
    analyze_route_patterns()