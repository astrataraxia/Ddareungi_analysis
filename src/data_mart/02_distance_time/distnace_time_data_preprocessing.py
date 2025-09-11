import pandas as pd
import numpy as np
import os
from pathlib import Path

def process_yearly_data():
    """
    연도별 데이터를 처리하여 이상치/결측치 제거 후 요약 통계 생성
    """
    years = range(2020, 2026)  # 2020-2025
    summary_results = []
    
    print("=== 연도별 데이터 처리 시작 ===")
    
    for year in years:
        file_path = f'data/02/distance_time_{year}.parquet'
        
        try:
            print(f"\n--- {year}년 데이터 처리 중 ---")
            
            # 데이터 로드
            df = pd.read_parquet(file_path)
            print(f"원본 데이터 크기: {df.shape}")
            
            # 기본 통계 확인
            print(f"이용시간 범위: {df['전체_이용_분'].min():.1f} ~ {df['전체_이용_분'].max():.1f}분")
            print(f"이용거리 범위: {df['전체_이용_거리'].min():.1f} ~ {df['전체_이용_거리'].max():.1f}m")
            
            # 1단계: 결측치 제거
            df_clean = df.dropna(subset=['전체_이용_분', '전체_이용_거리'])
            print(f"결측치 제거 후: {df_clean.shape} (제거: {df.shape[0] - df_clean.shape[0]}건)")
            
            # 2단계: 이상치 제거
            # 이용시간: 0분 초과, 720분(12시간) 이하
            # 이용거리: 0m 초과, 50km(50000m) 이하
            df_filtered = df_clean[
                (df_clean['전체_이용_분'] > 0) & 
                (df_clean['전체_이용_분'] <= 720) &
                (df_clean['전체_이용_거리'] > 0) & 
                (df_clean['전체_이용_거리'] <= 50000)
            ]
            print(f"이상치 제거 후: {df_filtered.shape} (제거: {df_clean.shape[0] - df_filtered.shape[0]}건)")
            
            # 3단계: 추가 이상치 제거 (통계적 방법 - IQR)
            # 이용시간 IQR 방법
            Q1_time = df_filtered['전체_이용_분'].quantile(0.25)
            Q3_time = df_filtered['전체_이용_분'].quantile(0.75)
            IQR_time = Q3_time - Q1_time
            time_lower = max(0, Q1_time - 1.5 * IQR_time)
            time_upper = min(720, Q3_time + 1.5 * IQR_time)
            
            # 이용거리 IQR 방법
            Q1_dist = df_filtered['전체_이용_거리'].quantile(0.25)
            Q3_dist = df_filtered['전체_이용_거리'].quantile(0.75)
            IQR_dist = Q3_dist - Q1_dist
            dist_lower = max(0, Q1_dist - 1.5 * IQR_dist)
            dist_upper = min(50000, Q3_dist + 1.5 * IQR_dist)
            
            print(f"IQR 기반 필터링 범위:")
            print(f"  - 이용시간: {time_lower:.1f} ~ {time_upper:.1f}분")
            print(f"  - 이용거리: {dist_lower:.1f} ~ {dist_upper:.1f}m")
            
            df_final = df_filtered[
                (df_filtered['전체_이용_분'] >= time_lower) & 
                (df_filtered['전체_이용_분'] <= time_upper) &
                (df_filtered['전체_이용_거리'] >= dist_lower) & 
                (df_filtered['전체_이용_거리'] <= dist_upper)
            ]
            print(f"최종 데이터: {df_final.shape} (제거: {df_filtered.shape[0] - df_final.shape[0]}건)")
            
            # 4단계: 요약 통계 계산 (JSON 직렬화 가능한 타입으로 변환)
            summary_stats = {
                'year': int(year),
                'total_records': int(len(df_final)),
                'avg_time': float(df_final['전체_이용_분'].mean()),
                'avg_distance': float(df_final['전체_이용_거리'].mean()),
                'median_time': float(df_final['전체_이용_분'].median()),
                'median_distance': float(df_final['전체_이용_거리'].median()),
                'std_time': float(df_final['전체_이용_분'].std()),
                'std_distance': float(df_final['전체_이용_거리'].std()),
                'time_range': [float(df_final['전체_이용_분'].min()), float(df_final['전체_이용_분'].max())],
                'distance_range': [float(df_final['전체_이용_거리'].min()), float(df_final['전체_이용_거리'].max())]
            }
            
            # 요일별 통계도 추가
            if '요일' in df_final.columns:
                weekday_stats = df_final.groupby('요일').agg({
                    '전체_이용_분': 'mean',
                    '전체_이용_거리': 'mean'
                }).round(2)
                # 딕셔너리 값들을 float으로 변환
                summary_stats['weekday_avg_time'] = {int(k): float(v) for k, v in weekday_stats['전체_이용_분'].to_dict().items()}
                summary_stats['weekday_avg_distance'] = {int(k): float(v) for k, v in weekday_stats['전체_이용_거리'].to_dict().items()}
            
            summary_results.append(summary_stats)
            
            print(f"평균 이용시간: {summary_stats['avg_time']:.2f}분")
            print(f"평균 이용거리: {summary_stats['avg_distance']:.2f}m")
            
            # 메모리 해제
            del df, df_clean, df_filtered, df_final
            
        except FileNotFoundError:
            print(f"{year}년 데이터 파일을 찾을 수 없습니다: {file_path}")
            continue
        except Exception as e:
            print(f"{year}년 데이터 처리 중 오류 발생: {str(e)}")
            continue
    
    return summary_results

# 데이터 처리 실행
summary_data = process_yearly_data()

if summary_data:
    print("\n=== 연도별 요약 통계 ===")
    
    # DataFrame으로 변환 (기본 통계만)
    basic_stats = []
    for stats in summary_data:
        basic_stats.append({
            'year': stats['year'],
            'total_records': stats['total_records'],
            'avg_time': round(stats['avg_time'], 2),
            'avg_distance': round(stats['avg_distance'], 2),
            'median_time': round(stats['median_time'], 2),
            'median_distance': round(stats['median_distance'], 2),
            'std_time': round(stats['std_time'], 2),
            'std_distance': round(stats['std_distance'], 2)
        })
    
    summary_df = pd.DataFrame(basic_stats)
    
    # 요약 데이터 저장
    output_path = 'data/02/yearly_summary.parquet'
    summary_df.to_parquet(output_path)
    print(f"\n요약 데이터 저장 완료: {output_path}")
    
    # 상세 정보도 JSON으로 저장
    import json
    with open('data/02/yearly_detailed_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, ensure_ascii=False, indent=2)
    print("상세 요약 데이터 저장 완료: data/02/yearly_detailed_summary.json")
    
    print("\n=== 상관관계 분석 (요약 데이터 기반) ===")
    
    # 연도별 평균값들 간의 상관관계
    time_distance_corr = summary_df['avg_time'].corr(summary_df['avg_distance'])
    print(f"연도별 평균 이용시간-거리 상관관계: {time_distance_corr:.4f}")
    
    # 시각화를 위한 차트 생성
    import altair as alt
    alt.data_transformers.enable('default', max_rows=None)
    
    # 1. 연도별 평균 이용시간 추이
    time_chart = alt.Chart(summary_df).mark_line(point=True, strokeWidth=3).encode(
        x=alt.X('year:O', title='연도'),
        y=alt.Y('avg_time:Q', title='평균 이용시간 (분)'),
        color=alt.value('#1f77b4'),
        tooltip=['year:O', 'avg_time:Q']
    ).properties(
        title='연도별 평균 이용시간 추이',
        width=400,
        height=300
    )
    
    # 2. 연도별 평균 이용거리 추이
    distance_chart = alt.Chart(summary_df).mark_line(point=True, strokeWidth=3).encode(
        x=alt.X('year:O', title='연도'),
        y=alt.Y('avg_distance:Q', title='평균 이용거리 (m)'),
        color=alt.value('#ff7f0e'),
        tooltip=['year:O', 'avg_distance:Q']
    ).properties(
        title='연도별 평균 이용거리 추이',
        width=400,
        height=300
    )
    
    # 3. 이중축 차트
    base = alt.Chart(summary_df).encode(x=alt.X('year:O', title='연도'))
    
    bar_time = base.mark_bar(color='#5276A7', opacity=0.7).encode(
        y=alt.Y('avg_time:Q', axis=alt.Axis(title='평균 이용시간 (분)', titleColor='#5276A7'))
    )
    
    line_dist = base.mark_line(color='#F58518', point=True, strokeWidth=3).encode(
        y=alt.Y('avg_distance:Q', axis=alt.Axis(title='평균 이용거리 (m)', titleColor='#F58518'))
    )
    
    combined_chart = alt.layer(bar_time, line_dist).resolve_scale(
        y='independent'
    ).properties(
        title='연도별 평균 이용시간(막대) 및 이용거리(선) 추이',
        width=600,
        height=400
    )
    
    # 차트 출력
    alt.hconcat(time_chart, distance_chart).display()
    combined_chart.display()
    
else:
    print("처리할 수 있는 데이터가 없습니다.")