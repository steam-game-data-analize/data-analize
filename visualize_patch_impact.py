import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
import numpy as np
from scipy import stats

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

def visualize_patch_notes(game_id, game_name, output_dir='output', viz_dir='visualizations'):
    """패치노트 분석 시각화"""
    
    os.makedirs(viz_dir, exist_ok=True)
    
    game_name_safe = game_name.replace(':', '').replace('/', '-')
    patch_file = os.path.join(output_dir, f"{game_id}_{game_name_safe}_patch_notes.csv")
    histogram_file = os.path.join(output_dir, f"{game_id}_{game_name_safe}_daily_histogram.csv")
    
    if not os.path.exists(patch_file):
        print(f"❌ {game_name}: 패치노트 파일을 찾을 수 없습니다.")
        return
    
    if not os.path.exists(histogram_file):
        print(f"❌ {game_name}: 히스토그램 파일을 찾을 수 없습니다.")
        return
    
    # 데이터 로드
    patch_df = pd.read_csv(patch_file)
    review_df = pd.read_csv(histogram_file)
    
    patch_df['date'] = pd.to_datetime(patch_df['date'])
    review_df['date'] = pd.to_datetime(review_df['date'])
    review_df = review_df.sort_values('date')
    
    # 리뷰 데이터 계산
    review_df['total_reviews'] = review_df['recommendations_up'] + review_df['recommendations_down']
    review_df['positive_ratio'] = (review_df['recommendations_up'] / review_df['total_reviews'] * 100).fillna(0)
    
    print(f"\n{game_name} 시각화 생성 중...")
    print(f"  패치노트: {len(patch_df)}개")
    print(f"  리뷰 데이터: {len(review_df)}개월")
    
    # 1. 패치노트 길이 분포 및 시간에 따른 변화
    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
    
    fig.suptitle(f'{game_name} - 패치노트 글자 수와 유저 반응 분석', fontsize=16, fontweight='bold', y=0.98)
    
    # 1-1. 패치노트 길이 분포
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.hist(patch_df['contents_length'], bins=30, color='#5B9BD5', alpha=0.7, edgecolor='black')
    ax1.set_title('패치노트 길이 분포', fontsize=12, fontweight='bold')
    ax1.set_xlabel('글자 수', fontsize=10)
    ax1.set_ylabel('빈도', fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    mean_length = patch_df['contents_length'].mean()
    median_length = patch_df['contents_length'].median()
    ax1.axvline(mean_length, color='red', linestyle='--', linewidth=2, label=f'평균: {mean_length:.0f}자')
    ax1.axvline(median_length, color='orange', linestyle='--', linewidth=2, label=f'중앙값: {median_length:.0f}자')
    ax1.legend()
    
    # 1-2. 시간에 따른 패치노트 길이 변화
    ax2 = fig.add_subplot(gs[0, 1])
    patch_sorted = patch_df.sort_values('date')
    ax2.scatter(patch_sorted['date'], patch_sorted['contents_length'], 
                alpha=0.6, s=50, color='#5B9BD5', edgecolor='black', linewidth=0.5)
    
    # 추세선
    x_numeric = mdates.date2num(patch_sorted['date'])
    z = np.polyfit(x_numeric, patch_sorted['contents_length'], 1)
    p = np.poly1d(z)
    ax2.plot(patch_sorted['date'], p(x_numeric), "r--", linewidth=2, label='추세선')
    
    ax2.set_title('시간에 따른 패치노트 길이 변화', fontsize=12, fontweight='bold')
    ax2.set_xlabel('날짜', fontsize=10)
    ax2.set_ylabel('글자 수', fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # 2. 패치노트와 리뷰 타임라인
    ax3 = fig.add_subplot(gs[1, :])
    
    # 리뷰 수를 배경으로
    ax3_bg = ax3.twinx()
    ax3_bg.bar(review_df['date'], review_df['total_reviews'], 
               color='#E8E8E8', alpha=0.5, width=20, label='월별 총 리뷰 수')
    ax3_bg.set_ylabel('총 리뷰 수', fontsize=10, color='gray')
    ax3_bg.tick_params(axis='y', labelcolor='gray')
    
    # 패치노트를 점으로 표시 (크기는 글자 수에 비례)
    # 날짜별로 그룹화하여 같은 날짜의 패치를 수직으로 배치
    patch_sorted = patch_df.sort_values('date')
    y_positions = []
    date_counts = {}
    
    for date in patch_sorted['date']:
        if date not in date_counts:
            date_counts[date] = 0
        else:
            date_counts[date] += 1
        
        # 같은 날짜의 패치들을 0.3 ~ 2.7 범위에 균등 분포
        y_positions.append(0.3 + (date_counts[date] % 8) * 0.3)
    
    sizes = (patch_sorted['contents_length'] / patch_sorted['contents_length'].max() * 400) + 30
    scatter = ax3.scatter(patch_sorted['date'], y_positions, 
                         s=sizes, c=patch_sorted['contents_length'], 
                         cmap='YlOrRd', alpha=0.7, edgecolor='black', linewidth=0.8,
                         zorder=5)
    
    ax3.set_title('패치노트 발표 타임라인 (크기 = 글자 수, 세로 위치 = 같은 날짜 구분)', fontsize=12, fontweight='bold', pad=15)
    ax3.set_xlabel('날짜', fontsize=10)
    ax3.set_yticks([])
    ax3.set_ylim(0, 3)
    ax3.grid(True, alpha=0.3, axis='x')
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # 컬러바
    cbar = plt.colorbar(scatter, ax=ax3, orientation='horizontal', pad=0.1, aspect=30)
    cbar.set_label('패치노트 글자 수', fontsize=9)
    
    # 3. 패치노트 길이별 평균 리뷰 반응
    # 패치노트를 길이 구간으로 분류
    patch_df['length_category'] = pd.cut(patch_df['contents_length'], 
                                         bins=[0, 500, 1000, 2000, 5000, float('inf')],
                                         labels=['매우 짧음\n(~500자)', '짧음\n(500-1000자)', 
                                                '보통\n(1000-2000자)', '김\n(2000-5000자)', 
                                                '매우 김\n(5000자+)'])
    
    ax4 = fig.add_subplot(gs[2, 0])
    category_counts = patch_df['length_category'].value_counts().sort_index()
    colors_bar = ['#FFE5E5', '#FFB3B3', '#FF8080', '#FF4D4D', '#CC0000']
    ax4.bar(range(len(category_counts)), category_counts.values, 
            color=colors_bar[:len(category_counts)], alpha=0.8, edgecolor='black')
    ax4.set_xticks(range(len(category_counts)))
    ax4.set_xticklabels(category_counts.index, fontsize=9)
    ax4.set_title('패치노트 길이별 분포', fontsize=12, fontweight='bold')
    ax4.set_ylabel('패치 개수', fontsize=10)
    ax4.grid(True, alpha=0.3, axis='y')
    
    # 각 막대 위에 개수 표시
    for i, v in enumerate(category_counts.values):
        ax4.text(i, v, str(v), ha='center', va='bottom', fontweight='bold')
    
    # 4. 주요 통계
    ax5 = fig.add_subplot(gs[2, 1])
    ax5.axis('off')
    
    stats_text = f"""
    📊 패치노트 통계
    
    • 총 패치 횟수: {len(patch_df)}개
    • 평균 글자 수: {patch_df['contents_length'].mean():.0f}자
    • 중앙값 글자 수: {patch_df['contents_length'].median():.0f}자
    • 최소 글자 수: {patch_df['contents_length'].min():.0f}자
    • 최대 글자 수: {patch_df['contents_length'].max():.0f}자
    • 표준편차: {patch_df['contents_length'].std():.0f}자
    
    📈 리뷰 통계
    
    • 분석 기간: {review_df['date'].min().strftime('%Y-%m')} ~ {review_df['date'].max().strftime('%Y-%m')}
    • 총 리뷰 수: {review_df['total_reviews'].sum():,}개
    • 평균 월별 리뷰: {review_df['total_reviews'].mean():.0f}개
    • 평균 긍정 비율: {review_df['positive_ratio'].mean():.1f}%
    """
    
    ax5.text(0.1, 0.9, stats_text, transform=ax5.transAxes, 
             fontsize=11, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    plt.tight_layout()
    
    output_file = os.path.join(viz_dir, f"{game_id}_{game_name_safe}_patch_analysis.png")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ {game_name}: {output_file}")
    plt.close()


def main():
    """메인 실행 함수"""
    
    games = [
        {'app_id': 1049590, 'name': 'Eternal Return'},
        {'app_id': 1973530, 'name': 'Limbus Company'},
        {'app_id': 730, 'name': 'Counter-Strike 2'},
        {'app_id': 440, 'name': 'Team Fortress 2'},
    ]
    
    print("=" * 80)
    print("패치노트 분석 시각화 시작")
    print("=" * 80)
    
    for game in games:
        visualize_patch_notes(game['app_id'], game['name'])
    
    print("\n" + "=" * 80)
    print("모든 시각화 완료!")
    print("출력 디렉토리: visualizations/")
    print("=" * 80)


if __name__ == "__main__":
    main()
