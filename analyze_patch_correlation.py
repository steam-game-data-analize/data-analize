import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import os

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

def analyze_patch_review_correlation(game_id, game_name, output_dir='output', viz_dir='visualizations'):
    """
    패치노트 길이와 스팀 리뷰 반응 간의 상관관계 분석
    """
    
    os.makedirs(viz_dir, exist_ok=True)
    
    game_name_safe = game_name.replace(':', '').replace('/', '-')
    patch_file = os.path.join(output_dir, f"{game_id}_{game_name_safe}_patch_notes.csv")
    histogram_file = os.path.join(output_dir, f"{game_id}_{game_name_safe}_daily_histogram.csv")
    
    if not os.path.exists(patch_file) or not os.path.exists(histogram_file):
        print(f"❌ {game_name}: 필요한 파일을 찾을 수 없습니다.")
        return None
    
    # 데이터 로드
    patch_df = pd.read_csv(patch_file)
    review_df = pd.read_csv(histogram_file)
    
    patch_df['date'] = pd.to_datetime(patch_df['date'])
    review_df['date'] = pd.to_datetime(review_df['date'])
    review_df = review_df.sort_values('date')
    
    # 리뷰 지표 계산
    review_df['total_reviews'] = review_df['recommendations_up'] + review_df['recommendations_down']
    review_df['positive_ratio'] = (review_df['recommendations_up'] / review_df['total_reviews'] * 100).fillna(0)
    
    print(f"\n{game_name} 상관관계 분석 중...")
    
    # 패치 전후 리뷰 변화 분석
    window_days = 30  # 패치 전후 30일
    analysis_results = []
    
    for idx, patch in patch_df.iterrows():
        patch_date = pd.to_datetime(patch['date'])
        
        # 패치 전 기간
        before_start = patch_date - pd.Timedelta(days=window_days)
        before_end = patch_date - pd.Timedelta(days=1)
        
        # 패치 후 기간
        after_start = patch_date
        after_end = patch_date + pd.Timedelta(days=window_days)
        
        # 해당 기간의 리뷰 데이터
        before_reviews = review_df[
            (review_df['date'] >= before_start) & 
            (review_df['date'] <= before_end)
        ]
        
        after_reviews = review_df[
            (review_df['date'] >= after_start) & 
            (review_df['date'] <= after_end)
        ]
        
        if len(before_reviews) > 0 and len(after_reviews) > 0:
            # 지표 계산
            before_avg_reviews = before_reviews['total_reviews'].mean()
            after_avg_reviews = after_reviews['total_reviews'].mean()
            before_positive_ratio = before_reviews['positive_ratio'].mean()
            after_positive_ratio = after_reviews['positive_ratio'].mean()
            
            # 변화율
            review_change_pct = ((after_avg_reviews - before_avg_reviews) / before_avg_reviews * 100) if before_avg_reviews > 0 else 0
            ratio_change = after_positive_ratio - before_positive_ratio
            
            analysis_results.append({
                'patch_date': patch_date,
                'patch_title': patch['title'],
                'patch_length': patch['contents_length'],
                'before_avg_reviews': before_avg_reviews,
                'after_avg_reviews': after_avg_reviews,
                'review_change_pct': review_change_pct,
                'before_positive_ratio': before_positive_ratio,
                'after_positive_ratio': after_positive_ratio,
                'positive_ratio_change': ratio_change,
                'engagement_score': after_avg_reviews / before_avg_reviews if before_avg_reviews > 0 else 1,
            })
    
    if not analysis_results:
        print(f"  ❌ 분석할 데이터가 충분하지 않습니다.")
        return None
    
    analysis_df = pd.DataFrame(analysis_results)
    
    # 상관계수 계산
    corr_length_reviews = analysis_df[['patch_length', 'review_change_pct']].corr().iloc[0, 1]
    corr_length_ratio = analysis_df[['patch_length', 'positive_ratio_change']].corr().iloc[0, 1]
    corr_length_engagement = analysis_df[['patch_length', 'engagement_score']].corr().iloc[0, 1]
    
    print(f"  📊 상관계수:")
    print(f"     - 패치 길이 vs 리뷰 증가율: {corr_length_reviews:.3f}")
    print(f"     - 패치 길이 vs 긍정 비율 변화: {corr_length_ratio:.3f}")
    print(f"     - 패치 길이 vs 참여도 점수: {corr_length_engagement:.3f}")
    
    # 시각화
    create_correlation_visualization(game_id, game_name, analysis_df, 
                                    corr_length_reviews, corr_length_ratio, 
                                    corr_length_engagement, viz_dir)
    
    # CSV 저장
    output_file = os.path.join(output_dir, f"{game_id}_{game_name_safe}_patch_impact.csv")
    analysis_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"  ✓ 분석 결과 저장: {output_file}")
    
    return analysis_df


def create_correlation_visualization(game_id, game_name, analysis_df, 
                                     corr_reviews, corr_ratio, corr_engagement, viz_dir):
    """패치 길이와 유저 반응 상관관계 시각화"""
    
    game_name_safe = game_name.replace(':', '').replace('/', '-')
    
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(2, 3, hspace=0.35, wspace=0.3)
    
    fig.suptitle(f'{game_name} - 패치노트 길이와 유저 반응 상관관계 분석', 
                 fontsize=16, fontweight='bold', y=0.98)
    
    # 1. 패치 길이 vs 리뷰 증가율
    ax1 = fig.add_subplot(gs[0, 0])
    scatter1 = ax1.scatter(analysis_df['patch_length'], analysis_df['review_change_pct'],
                          alpha=0.6, s=80, c=analysis_df['positive_ratio_change'],
                          cmap='RdYlGn', edgecolor='black', linewidth=0.5)
    
    # 추세선
    z1 = np.polyfit(analysis_df['patch_length'], analysis_df['review_change_pct'], 1)
    p1 = np.poly1d(z1)
    x_line = np.linspace(analysis_df['patch_length'].min(), analysis_df['patch_length'].max(), 100)
    ax1.plot(x_line, p1(x_line), "r--", linewidth=2, alpha=0.8, label='추세선')
    
    ax1.axhline(y=0, color='gray', linestyle='-', linewidth=1, alpha=0.5)
    ax1.set_xlabel('패치노트 글자 수', fontsize=10)
    ax1.set_ylabel('리뷰 증가율 (%)', fontsize=10)
    ax1.set_title(f'패치 길이 vs 리뷰 증가율\n상관계수: {corr_reviews:.3f}', 
                  fontsize=11, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    plt.colorbar(scatter1, ax=ax1, label='긍정 비율 변화 (%p)')
    
    # 2. 패치 길이 vs 긍정 비율 변화
    ax2 = fig.add_subplot(gs[0, 1])
    scatter2 = ax2.scatter(analysis_df['patch_length'], analysis_df['positive_ratio_change'],
                          alpha=0.6, s=80, c=analysis_df['review_change_pct'],
                          cmap='coolwarm', edgecolor='black', linewidth=0.5)
    
    # 추세선
    z2 = np.polyfit(analysis_df['patch_length'], analysis_df['positive_ratio_change'], 1)
    p2 = np.poly1d(z2)
    ax2.plot(x_line, p2(x_line), "r--", linewidth=2, alpha=0.8, label='추세선')
    
    ax2.axhline(y=0, color='gray', linestyle='-', linewidth=1, alpha=0.5)
    ax2.set_xlabel('패치노트 글자 수', fontsize=10)
    ax2.set_ylabel('긍정 비율 변화 (%p)', fontsize=10)
    ax2.set_title(f'패치 길이 vs 긍정 비율 변화\n상관계수: {corr_ratio:.3f}', 
                  fontsize=11, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    plt.colorbar(scatter2, ax=ax2, label='리뷰 증가율 (%)')
    
    # 3. 패치 길이 vs 참여도 점수
    ax3 = fig.add_subplot(gs[0, 2])
    scatter3 = ax3.scatter(analysis_df['patch_length'], analysis_df['engagement_score'],
                          alpha=0.6, s=80, c=analysis_df['positive_ratio_change'],
                          cmap='RdYlGn', edgecolor='black', linewidth=0.5)
    
    # 추세선
    z3 = np.polyfit(analysis_df['patch_length'], analysis_df['engagement_score'], 1)
    p3 = np.poly1d(z3)
    ax3.plot(x_line, p3(x_line), "r--", linewidth=2, alpha=0.8, label='추세선')
    
    ax3.axhline(y=1, color='gray', linestyle='-', linewidth=1, alpha=0.5, label='변화 없음')
    ax3.set_xlabel('패치노트 글자 수', fontsize=10)
    ax3.set_ylabel('참여도 점수 (배수)', fontsize=10)
    ax3.set_title(f'패치 길이 vs 유저 참여도\n상관계수: {corr_engagement:.3f}', 
                  fontsize=11, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    plt.colorbar(scatter3, ax=ax3, label='긍정 비율 변화 (%p)')
    
    # 4. 길이 구간별 평균 반응
    analysis_df['length_category'] = pd.cut(analysis_df['patch_length'], 
                                            bins=[0, 500, 1000, 2000, 5000, float('inf')],
                                            labels=['~500자', '500-1K', '1K-2K', '2K-5K', '5K+'])
    
    ax4 = fig.add_subplot(gs[1, 0])
    category_stats = analysis_df.groupby('length_category', observed=True).agg({
        'review_change_pct': 'mean',
        'patch_length': 'count'
    }).reset_index()
    
    bars = ax4.bar(range(len(category_stats)), category_stats['review_change_pct'],
                   color=['#FFE5E5', '#FFB3B3', '#FF8080', '#FF4D4D', '#CC0000'][:len(category_stats)],
                   alpha=0.8, edgecolor='black')
    ax4.axhline(y=0, color='gray', linestyle='-', linewidth=1)
    ax4.set_xticks(range(len(category_stats)))
    ax4.set_xticklabels(category_stats['length_category'], fontsize=9)
    ax4.set_ylabel('평균 리뷰 증가율 (%)', fontsize=10)
    ax4.set_title('길이 구간별 평균 리뷰 증가율', fontsize=11, fontweight='bold')
    ax4.grid(True, alpha=0.3, axis='y')
    
    # 막대 위에 값 표시
    for i, (bar, val, count) in enumerate(zip(bars, category_stats['review_change_pct'], 
                                               category_stats['patch_length'])):
        ax4.text(i, val, f'{val:.1f}%\n(n={count})', 
                ha='center', va='bottom' if val > 0 else 'top', fontsize=8, fontweight='bold')
    
    # 5. 길이 구간별 긍정 비율 변화
    ax5 = fig.add_subplot(gs[1, 1])
    category_stats2 = analysis_df.groupby('length_category', observed=True).agg({
        'positive_ratio_change': 'mean',
        'patch_length': 'count'
    }).reset_index()
    
    bars2 = ax5.bar(range(len(category_stats2)), category_stats2['positive_ratio_change'],
                    color=['#E8F5E9', '#A5D6A7', '#66BB6A', '#43A047', '#2E7D32'][:len(category_stats2)],
                    alpha=0.8, edgecolor='black')
    ax5.axhline(y=0, color='gray', linestyle='-', linewidth=1)
    ax5.set_xticks(range(len(category_stats2)))
    ax5.set_xticklabels(category_stats2['length_category'], fontsize=9)
    ax5.set_ylabel('평균 긍정 비율 변화 (%p)', fontsize=10)
    ax5.set_title('길이 구간별 평균 긍정 비율 변화', fontsize=11, fontweight='bold')
    ax5.grid(True, alpha=0.3, axis='y')
    
    # 막대 위에 값 표시
    for i, (bar, val, count) in enumerate(zip(bars2, category_stats2['positive_ratio_change'], 
                                               category_stats2['patch_length'])):
        ax5.text(i, val, f'{val:+.1f}%p\n(n={count})', 
                ha='center', va='bottom' if val > 0 else 'top', fontsize=8, fontweight='bold')
    
    # 6. 주요 인사이트
    ax6 = fig.add_subplot(gs[1, 2])
    ax6.axis('off')
    
    # 상관관계 해석
    def interpret_correlation(corr):
        if abs(corr) < 0.3:
            return "약한 상관관계"
        elif abs(corr) < 0.7:
            return "중간 상관관계"
        else:
            return "강한 상관관계"
    
    best_length = category_stats.loc[category_stats['review_change_pct'].idxmax(), 'length_category']
    best_ratio_length = category_stats2.loc[category_stats2['positive_ratio_change'].idxmax(), 'length_category']
    
    insights_text = f"""
    📊 주요 인사이트
    
    1. 리뷰 증가율 상관관계
       • 상관계수: {corr_reviews:.3f}
       • 해석: {interpret_correlation(corr_reviews)}
       • {'긴 패치노트일수록 리뷰 증가' if corr_reviews > 0 else '짧은 패치노트가 더 효과적'}
    
    2. 긍정 비율 상관관계
       • 상관계수: {corr_ratio:.3f}
       • 해석: {interpret_correlation(corr_ratio)}
       • {'긴 패치노트일수록 긍정 반응' if corr_ratio > 0 else '짧은 패치노트가 더 긍정적'}
    
    3. 최적 패치노트 길이
       • 리뷰 증가: {best_length}
       • 긍정 반응: {best_ratio_length}
    
    4. 분석 데이터
       • 분석된 패치: {len(analysis_df)}개
       • 평균 리뷰 증가율: {analysis_df['review_change_pct'].mean():.1f}%
       • 평균 긍정 비율 변화: {analysis_df['positive_ratio_change'].mean():.1f}%p
    """
    
    ax6.text(0.05, 0.95, insights_text, transform=ax6.transAxes, 
             fontsize=10, verticalalignment='top', family='monospace',
             bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    plt.tight_layout()
    
    output_file = os.path.join(viz_dir, f"{game_id}_{game_name_safe}_correlation.png")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"  ✓ 상관관계 차트 저장: {output_file}")
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
    print("패치노트 길이와 유저 반응 상관관계 분석")
    print("=" * 80)
    
    all_results = {}
    
    for game in games:
        result = analyze_patch_review_correlation(game['app_id'], game['name'])
        if result is not None:
            all_results[game['name']] = result
    
    print("\n" + "=" * 80)
    print("분석 완료!")
    print("=" * 80)
    
    return all_results


if __name__ == "__main__":
    main()
