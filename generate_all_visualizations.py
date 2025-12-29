"""
데이터 수집부터 시각화까지 전체 파이프라인을 실행하는 통합 스크립트
"""

import sys
import os

# 기능별 모듈 임포트
from util.collector import SteamAPIExplorer
from util.patch_collector import PatchNoteAnalyzer
from util.viz_reviews import visualize_game_data, create_comparison_chart
from util.viz_patches import visualize_patch_notes
from util.analyzer import analyze_patch_review_correlation

def main():
    """데이터 수집 → 전처리 → 시각화 전체 파이프라인 실행"""
    
    games = [
        {'app_id': 1049590, 'name': 'Eternal Return'},
        {'app_id': 1973530, 'name': 'Limbus Company'},
        {'app_id': 730, 'name': 'Counter-Strike 2'},
        {'app_id': 440, 'name': 'Team Fortress 2'},
    ]
    
    print("=" * 80)
    print("전체 데이터 분석 파이프라인 시작")
    print("=" * 80)
    
    # 0. 데이터 수집
    print("\n[0/4] Steam API 데이터 수집 중...")
    print("-" * 80)
    
    # 0-1. 리뷰 및 히스토그램 데이터 수집
    print("\n리뷰 데이터 수집 중...")
    explorer = SteamAPIExplorer()
    for game in games:
        try:
            print(f"\n{game['name']} 데이터 수집 중...")
            game_data = explorer.collect_game_data(game['app_id'], game['name'])
            explorer.save_to_csv(game_data)
        except Exception as e:
            print(f"  ❌ {game['name']} 리뷰 데이터 수집 실패: {e}")
    
    # 0-2. 패치노트 데이터 수집
    print("\n패치노트 데이터 수집 중...")
    patch_analyzer = PatchNoteAnalyzer()
    for game in games:
        try:
            app_id = game['app_id']
            game_name = game['name']
            
            # 패치노트 수집
            patch_notes = patch_analyzer.collect_patch_notes(app_id, game_name)
            if not patch_notes:
                continue
            
            # 리뷰 히스토그램 수집
            review_histogram = patch_analyzer.get_review_histogram(app_id)
            if not review_histogram:
                print(f"  ❌ {game_name}: 리뷰 데이터를 가져올 수 없습니다.")
                continue
            
            # 패치 영향 분석
            analysis_df = patch_analyzer.analyze_patch_impact(patch_notes, review_histogram, window_days=7)
            
            # CSV 저장
            patch_analyzer.save_to_csv(patch_notes, analysis_df, game_name, app_id)
            
        except Exception as e:
            print(f"  ❌ {game['name']} 패치노트 수집 실패: {e}")
    
    print("\n✅ 데이터 수집 완료!")
    
    # 1. 기본 리뷰 데이터 시각화
    print("\n[1/3] 리뷰 데이터 시각화 생성 중...")
    print("-" * 80)
    for game in games:
        try:
            visualize_game_data(game['app_id'], game['name'])
        except Exception as e:
            print(f"  ❌ {game['name']} 리뷰 시각화 실패: {e}")
    
    # 비교 차트
    try:
        create_comparison_chart(games)
    except Exception as e:
        print(f"  ❌ 비교 차트 생성 실패: {e}")
    
    # 2. 패치노트 분석 시각화
    print("\n[2/3] 패치노트 분석 시각화 생성 중...")
    print("-" * 80)
    for game in games:
        try:
            visualize_patch_notes(game['app_id'], game['name'])
        except Exception as e:
            print(f"  ❌ {game['name']} 패치노트 시각화 실패: {e}")
    
    # 3. 상관관계 분석 시각화
    print("\n[3/3] 상관관계 분석 시각화 생성 중...")
    print("-" * 80)
    for game in games:
        try:
            analyze_patch_review_correlation(game['app_id'], game['name'])
        except Exception as e:
            print(f"  ❌ {game['name']} 상관관계 분석 실패: {e}")
    
    print("\n" + "=" * 80)
    print("모든 시각화 생성 완료!")
    print("=" * 80)
    print("\n생성된 파일:")
    print("  📁 visualizations/ - 모든 차트 이미지")
    print("  📁 output/ - 분석 데이터 CSV")
    print("\n생성된 차트 종류:")
    print("  1. 리뷰 추이 분석 (월별 긍정/부정 리뷰, 비율, 총 리뷰 수)")
    print("  2. 게임 간 비교 차트")
    print("  3. 패치노트 길이 분석 (분포, 시간 변화, 타임라인)")
    print("  4. 패치노트-리뷰 상관관계 분석 (6개 지표)")
    print("=" * 80)


if __name__ == "__main__":
    main()
