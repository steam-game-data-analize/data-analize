import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path
import os

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

def visualize_game_data(game_id, game_name, output_dir='output', viz_dir='visualizations'):
    """
    게임의 히스토그램 데이터를 시각화
    """
    os.makedirs(viz_dir, exist_ok=True)
    
    game_name_safe = game_name.replace('/', '_').replace('\\', '_').replace(':', '_')
    histogram_file = os.path.join(output_dir, f"{game_id}_{game_name_safe}_daily_histogram.csv")
    
    if not os.path.exists(histogram_file):
        print(f"❌ {game_name}: 히스토그램 파일을 찾을 수 없습니다.")
        return
    
    df = pd.read_csv(histogram_file)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    # 3개 서브플롯: 리뷰 수, 비율, 거래량
    fig = plt.figure(figsize=(16, 11))
    gs = fig.add_gridspec(3, 1, height_ratios=[2.5, 1.5, 1], hspace=0.3)
    
    fig.suptitle(f'{game_name} - Steam 리뷰 분석', fontsize=16, fontweight='bold', y=0.98)
    
    df['total_reviews'] = df['recommendations_up'] + df['recommendations_down']
    df['positive_ratio'] = (df['recommendations_up'] / df['total_reviews'] * 100).fillna(0)
    df['negative_ratio'] = (df['recommendations_down'] / df['total_reviews'] * 100).fillna(0)
    
    bar_width = 20
    
    # 1. 비율 차트 (상단)
    ax1 = fig.add_subplot(gs[0])
    ax1.bar(df['date'], df['positive_ratio'], width=bar_width, 
            label='긍정 비율', color='#5B9BD5', alpha=0.85, edgecolor='none')
    ax1.bar(df['date'], -df['negative_ratio'], width=bar_width, 
            label='부정 비율', color='#ED7D31', alpha=0.85, edgecolor='none')
    
    ax1.axhline(y=0, color='black', linewidth=1.5, zorder=3)
    ax1.set_title('월별 긍정 리뷰 비율 추이', fontsize=12, fontweight='bold', pad=15)
    ax1.set_ylabel('비율 (%)', fontsize=10)
    ax1.legend(loc='upper left', framealpha=0.9)
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.set_ylim(-100, 100)
    
    ax1_labels = ax1.get_yticks()
    ax1.set_yticklabels([f'{abs(int(y))}' for y in ax1_labels])
    ax1.set_xticklabels([])
    
    # 2. 리뷰 수 차트 (중간)
    ax2 = fig.add_subplot(gs[1], sharex=ax1)
    ax2.bar(df['date'], df['recommendations_up'], width=bar_width, 
            label='긍정 리뷰', color='#5B9BD5', alpha=0.85, edgecolor='none')
    ax2.bar(df['date'], -df['recommendations_down'], width=bar_width, 
            label='부정 리뷰', color='#ED7D31', alpha=0.85, edgecolor='none')
    
    ax2.axhline(y=0, color='black', linewidth=1.5, zorder=3)
    ax2.set_title('월별 긍정/부정 리뷰 수 추이 (새로운 스타일)', fontsize=12, fontweight='bold', pad=15)
    ax2.set_ylabel('리뷰 수', fontsize=10)
    ax2.legend(loc='upper left', framealpha=0.9, fontsize=9)
    ax2.grid(True, alpha=0.3, axis='y')
    
    y_max = max(df['recommendations_up'].max(), df['recommendations_down'].max())
    ax2.set_ylim(-y_max * 1.1, y_max * 1.1)
    
    ax2_labels = ax2.get_yticks()
    ax2.set_yticklabels([f'{abs(int(y)):,}' for y in ax2_labels])
    ax2.set_xticklabels([])
    
    # 3. 거래량 스타일 차트: 총 리뷰 수
    ax3 = fig.add_subplot(gs[2], sharex=ax1)
    ax3.bar(df['date'], df['total_reviews'], color='#9b59b6', alpha=0.6, width=20, edgecolor='none')
    ax3.set_title('월별 총 리뷰 수', fontsize=10, fontweight='bold', pad=10)
    ax3.set_ylabel('총 리뷰 수', fontsize=9)
    ax3.set_xlabel('날짜', fontsize=10)
    ax3.grid(True, alpha=0.3, axis='y')
    
    # X축 날짜 포맷 개선
    data_range = (df['date'].max() - df['date'].min()).days
    if data_range > 1825:  # 5년 이상
        ax3.xaxis.set_major_locator(mdates.YearLocator())
        ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    elif data_range > 730:  # 2년 이상
        ax3.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
        ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    else:
        ax3.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    
    plt.setp(ax3.xaxis.get_majorticklabels(), rotation=60, ha='right', fontsize=9)
    ax3.tick_params(axis='y', labelsize=8)
    
    plt.tight_layout()
    
    output_file = os.path.join(viz_dir, f"{game_id}_{game_name_safe}_analysis.png")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ {game_name}: {output_file}")
    plt.close()
    
    # 통계 요약
    print(f"\n  📊 {game_name} 통계 요약:")
    print(f"     - 데이터 기간: {df['date'].min().strftime('%Y-%m')} ~ {df['date'].max().strftime('%Y-%m')}")
    print(f"     - 총 긍정 리뷰: {df['recommendations_up'].sum():,}개")
    print(f"     - 총 부정 리뷰: {df['recommendations_down'].sum():,}개")
    print(f"     - 전체 긍정 비율: {(df['recommendations_up'].sum() / (df['recommendations_up'].sum() + df['recommendations_down'].sum()) * 100):.1f}%")
    print(f"     - 최고 리뷰 수 월: {df.loc[df['total_reviews'].idxmax(), 'date'].strftime('%Y-%m')} ({df['total_reviews'].max():,}개)")
    print(f"     - 최저 긍정 비율 월: {df.loc[df['positive_ratio'].idxmin(), 'date'].strftime('%Y-%m')} ({df['positive_ratio'].min():.1f}%)")
    print()


def create_comparison_chart(output_dir='output', viz_dir='visualizations'):
    """
    모든 게임의 긍정 비율을 비교하는 차트 생성
    """
    games = [
        (1049590, "Eternal Return"),
        (1973530, "Limbus Company"),
        (730, "Counter-Strike 2"),
        (440, "Team Fortress 2"),
    ]
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12']
    
    for (game_id, game_name), color in zip(games, colors):
        game_name_safe = game_name.replace('/', '_').replace('\\', '_').replace(':', '_')
        histogram_file = os.path.join(output_dir, f"{game_id}_{game_name_safe}_daily_histogram.csv")
        
        if os.path.exists(histogram_file):
            df = pd.read_csv(histogram_file)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            df['total_reviews'] = df['recommendations_up'] + df['recommendations_down']
            df['positive_ratio'] = (df['recommendations_up'] / df['total_reviews'] * 100).fillna(0)
            
            ax.plot(df['date'], df['positive_ratio'], label=game_name, linewidth=2, color=color)
    
    ax.axhline(y=50, color='gray', linestyle='--', alpha=0.5, label='50% 기준선')
    ax.set_title('게임별 긍정 리뷰 비율 비교', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('날짜', fontsize=10)
    ax.set_ylabel('긍정 비율 (%)', fontsize=10)
    ax.set_ylim(0, 100)
    ax.legend(loc='best', framealpha=0.9)
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.YearLocator())
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    
    output_file = os.path.join(viz_dir, "all_games_comparison.png")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ 게임 비교 차트: {output_file}")
    plt.close()


def main():
    games = [
        (1049590, "Eternal Return"),
        (1973530, "Limbus Company"),
        (730, "Counter-Strike 2"),
        (440, "Team Fortress 2"),
    ]
    
    print("\n" + "="*80)
    print("Steam 게임 데이터 시각화 시작")
    print("="*80 + "\n")
    
    for game_id, game_name in games:
        visualize_game_data(game_id, game_name)
    
    print("="*80)
    print("게임 비교 차트 생성")
    print("="*80 + "\n")
    create_comparison_chart()
    
    print("\n" + "="*80)
    print("모든 시각화 완료!")
    print("출력 디렉토리: visualizations/")
    print("="*80)


if __name__ == "__main__":
    main()
