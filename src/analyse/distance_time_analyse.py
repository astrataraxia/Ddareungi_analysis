import numpy as np
import matplotlib.pyplot as plt

from src.load_data.distance_data_load import load_yearly_summary_data


plt.rc('font', family='NanumGothic') # For Windows
plt.rcParams['axes.unicode_minus'] = False # 마이너스 폰트 깨짐 방지

# --- 데이터 로드 ---
df = load_yearly_summary_data()


# --- 2 연도별 평균 이용 시간 및 거리 변화 ---
print("\n--- 연도별 평균 이용 시간 및 거리 변화 시각화 ---")

fig, ax1 = plt.subplots(figsize=(12, 7))

# X축 설정
years = df['year']

# 좌측 Y축 (평균 이용 시간)
color_time = 'darkorange'
ax1.set_xlabel('연도', fontsize=12)
ax1.set_ylabel('평균 이용 시간 (분)', color=color_time, fontsize=12)
ax1.bar(years, df['avg_time'], color=color_time, label='평균 이용 시간(분)', width=0.6, alpha=0.7)
ax1.tick_params(axis='y', labelcolor=color_time)

# 우측 Y축 (평균 이용 거리)
ax2 = ax1.twinx()
color_dist = 'green'
ax2.set_ylabel('평균 이용 거리 (m)', color=color_dist, fontsize=12)
ax2.plot(years, df['avg_distance'], color=color_dist, marker='s', linestyle='--', label='평균 이용 거리(m)')
ax2.tick_params(axis='y', labelcolor=color_dist)

# 제목 및 범례
plt.title('연도별 평균 따릉이 이용 시간 및 거리 변화', fontsize=16)
fig.legend(loc="upper right", bbox_to_anchor=(1,1), bbox_transform=ax1.transAxes)
fig.tight_layout()
plt.show()


# --- 3. (신규) 연도별 주중 vs 주말 이용 패턴 비교 ---
print("\n--- 연도별 주중 vs 주말 이용 패턴 시각화 ---")

# 주중(0-4), 주말(5-6) 데이터 계산
# weekday_avg_time과 weekday_avg_distance 컬럼의 딕셔너리 키를 정수로 변환하여 사용
df['workday_avg_time'] = df['weekday_avg_time'].apply(lambda x: np.mean([v for k, v in x.items() if int(k) < 5]))
df['weekend_avg_time'] = df['weekday_avg_time'].apply(lambda x: np.mean([v for k, v in x.items() if int(k) >= 5]))
df['workday_avg_dist'] = df['weekday_avg_distance'].apply(lambda x: np.mean([v for k, v in x.items() if int(k) < 5]))
df['weekend_avg_dist'] = df['weekday_avg_distance'].apply(lambda x: np.mean([v for k, v in x.items() if int(k) >= 5]))

fig, axes = plt.subplots(1, 2, figsize=(18, 7))
fig.suptitle('연도별 주중 vs 주말 따릉이 이용 패턴 비교', fontsize=16)

bar_width = 0.35
index = np.arange(len(years))

# 평균 이용 시간 비교 (주중 vs 주말)
axes[0].bar(index - bar_width/2, df['workday_avg_time'], bar_width, label='주중 평균', color='cornflowerblue')
axes[0].bar(index + bar_width/2, df['weekend_avg_time'], bar_width, label='주말 평균', color='salmon')
axes[0].set_title('평균 이용 시간 (분)', fontsize=14)
axes[0].set_xlabel('연도', fontsize=12)
axes[0].set_ylabel('시간 (분)', fontsize=12)
axes[0].set_xticks(index)
axes[0].set_xticklabels(years)
axes[0].legend()
axes[0].grid(axis='y', linestyle='--', alpha=0.6)

# 평균 이용 거리 비교 (주중 vs 주말)
axes[1].bar(index - bar_width/2, df['workday_avg_dist'], bar_width, label='주중 평균', color='cornflowerblue')
axes[1].bar(index + bar_width/2, df['weekend_avg_dist'], bar_width, label='주말 평균', color='salmon')
axes[1].set_title('평균 이용 거리 (m)', fontsize=14)
axes[1].set_xlabel('연도', fontsize=12)
axes[1].set_ylabel('거리 (m)', fontsize=12)
axes[1].set_xticks(index)
axes[1].set_xticklabels(years)
axes[1].legend()
axes[1].grid(axis='y', linestyle='--', alpha=0.6)

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()