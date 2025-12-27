import requests
import json
from datetime import datetime, timedelta
import pandas as pd
import os
from bs4 import BeautifulSoup
import re

class PatchNoteAnalyzer:
    """
    패치노트 글자 수와 유저 반응 분석 도구
    Steam News API를 사용하여 패치노트를 수집하고 리뷰 데이터와 연관 분석
    """
    
    def __init__(self):
        self.base_url = "https://api.steampowered.com"
        self.store_url = "https://store.steampowered.com"
        
    def get_app_news(self, app_id, count=100, max_length=None):
        """
        게임의 뉴스/패치노트 가져오기
        
        Parameters:
        - app_id: Steam 게임 ID
        - count: 가져올 뉴스 개수 (최대 100)
        - max_length: 뉴스 내용 최대 길이
        """
        url = f"{self.base_url}/ISteamNews/GetNewsForApp/v0002/"
        
        params = {
            'appid': app_id,
            'count': count,
            'format': 'json'
        }
        
        if max_length:
            params['maxlength'] = max_length
            
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching news: {e}")
            return None
    
    def clean_html(self, html_text):
        """HTML 태그 제거하고 순수 텍스트만 추출"""
        if not html_text:
            return ""
        soup = BeautifulSoup(html_text, 'html.parser')
        text = soup.get_text()
        # 여러 공백을 하나로
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def is_patch_note(self, title, contents):
        """
        패치노트인지 판별 (제목이나 내용에 패치 관련 키워드 포함)
        """
        patch_keywords = [
            'patch', 'update', 'hotfix', 'fix', 'balance', 
            '패치', '업데이트', '수정', '밸런스', '버그',
            'version', 'v.', 'v1', 'v2', 'changelog'
        ]
        
        combined_text = (title + ' ' + contents).lower()
        return any(keyword in combined_text for keyword in patch_keywords)
    
    def collect_patch_notes(self, app_id, game_name):
        """
        패치노트 수집 및 분석
        """
        print(f"\n패치노트 수집 중: {game_name} (App ID: {app_id})")
        
        news_data = self.get_app_news(app_id, count=100)
        
        if not news_data or 'appnews' not in news_data:
            print(f"  ❌ 뉴스 데이터를 가져올 수 없습니다.")
            return None
        
        newsitems = news_data['appnews'].get('newsitems', [])
        
        patch_notes = []
        for item in newsitems:
            title = item.get('title', '')
            contents = item.get('contents', '')
            
            # 패치노트인지 확인
            if self.is_patch_note(title, contents):
                clean_contents = self.clean_html(contents)
                
                patch_notes.append({
                    'gid': item.get('gid', ''),
                    'title': title,
                    'url': item.get('url', ''),
                    'author': item.get('author', ''),
                    'contents': clean_contents,
                    'contents_length': len(clean_contents),
                    'date': datetime.fromtimestamp(item.get('date', 0)),
                    'feedlabel': item.get('feedlabel', ''),
                    'feed_type': item.get('feed_type', 0)
                })
        
        print(f"  ✓ 총 {len(newsitems)}개 뉴스 중 {len(patch_notes)}개 패치노트 발견")
        return patch_notes
    
    def get_review_histogram(self, app_id):
        """날짜별 리뷰 히스토그램 데이터 가져오기"""
        url = f"{self.store_url}/appreviewhistogram/{app_id}"
        
        try:
            response = requests.get(url, params={'l': 'english'})
            response.raise_for_status()
            data = response.json()
            
            if data and data.get('success') == 1:
                results = data.get('results', {})
                if isinstance(results, dict) and 'rollups' in results:
                    rollups = results['rollups']
                    histogram = []
                    for rollup in rollups:
                        if isinstance(rollup, dict):
                            date = datetime.fromtimestamp(rollup.get('date', 0))
                            histogram.append({
                                'date': date,
                                'recommendations_up': rollup.get('recommendations_up', 0),
                                'recommendations_down': rollup.get('recommendations_down', 0)
                            })
                    return histogram
            return None
        except Exception as e:
            print(f"Error fetching histogram: {e}")
            return None
    
    def analyze_patch_impact(self, patch_notes, review_histogram, window_days=7):
        """
        패치노트 발표 전후의 리뷰 변화 분석
        
        Parameters:
        - patch_notes: 패치노트 리스트
        - review_histogram: 리뷰 히스토그램 데이터
        - window_days: 패치 전후 분석 기간 (일)
        """
        if not patch_notes or not review_histogram:
            return None
        
        # 리뷰 데이터를 DataFrame으로 변환
        review_df = pd.DataFrame(review_histogram)
        review_df['date'] = pd.to_datetime(review_df['date'])
        review_df['total_reviews'] = review_df['recommendations_up'] + review_df['recommendations_down']
        review_df['positive_ratio'] = (review_df['recommendations_up'] / review_df['total_reviews'] * 100).fillna(0)
        
        analysis_results = []
        
        for patch in patch_notes:
            patch_date = pd.to_datetime(patch['date'])
            
            # 패치 전후 기간 설정
            before_start = patch_date - timedelta(days=window_days)
            before_end = patch_date - timedelta(days=1)
            after_start = patch_date
            after_end = patch_date + timedelta(days=window_days)
            
            # 패치 전 리뷰 데이터
            before_reviews = review_df[
                (review_df['date'] >= before_start) & 
                (review_df['date'] <= before_end)
            ]
            
            # 패치 후 리뷰 데이터
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
                
                # 변화율 계산
                review_count_change = ((after_avg_reviews - before_avg_reviews) / before_avg_reviews * 100) if before_avg_reviews > 0 else 0
                positive_ratio_change = after_positive_ratio - before_positive_ratio
                
                analysis_results.append({
                    'patch_date': patch_date,
                    'patch_title': patch['title'],
                    'patch_length': patch['contents_length'],
                    'before_avg_reviews': before_avg_reviews,
                    'after_avg_reviews': after_avg_reviews,
                    'review_count_change_pct': review_count_change,
                    'before_positive_ratio': before_positive_ratio,
                    'after_positive_ratio': after_positive_ratio,
                    'positive_ratio_change': positive_ratio_change,
                    'user_engagement_score': after_avg_reviews / before_avg_reviews if before_avg_reviews > 0 else 1,
                })
        
        return pd.DataFrame(analysis_results)
    
    def save_to_csv(self, patch_notes, analysis_df, game_name, app_id, output_dir='output'):
        """분석 결과를 CSV로 저장"""
        os.makedirs(output_dir, exist_ok=True)
        
        game_name_safe = game_name.replace(':', '').replace('/', '-')
        
        # 패치노트 원본 저장
        if patch_notes:
            patch_df = pd.DataFrame(patch_notes)
            patch_file = os.path.join(output_dir, f"{app_id}_{game_name_safe}_patch_notes.csv")
            patch_df.to_csv(patch_file, index=False, encoding='utf-8-sig')
            print(f"  ✓ 패치노트 저장: {patch_file}")
        
        # 분석 결과 저장
        if analysis_df is not None and len(analysis_df) > 0:
            analysis_file = os.path.join(output_dir, f"{app_id}_{game_name_safe}_patch_impact.csv")
            analysis_df.to_csv(analysis_file, index=False, encoding='utf-8-sig')
            print(f"  ✓ 패치 영향 분석 저장: {analysis_file}")
            
            return patch_file, analysis_file
        
        return None, None


def main():
    """메인 실행 함수"""
    analyzer = PatchNoteAnalyzer()
    
    # 분석할 게임 목록
    games = [
        {'app_id': 1049590, 'name': 'Eternal Return'},
        {'app_id': 1973530, 'name': 'Limbus Company'},
        {'app_id': 730, 'name': 'Counter-Strike 2'},
        {'app_id': 440, 'name': 'Team Fortress 2'},
    ]
    
    print("=" * 80)
    print("패치노트 글자 수와 유저 반응 분석 시작")
    print("=" * 80)
    
    for game in games:
        app_id = game['app_id']
        game_name = game['name']
        
        # 1. 패치노트 수집
        patch_notes = analyzer.collect_patch_notes(app_id, game_name)
        
        if not patch_notes:
            continue
        
        # 2. 리뷰 히스토그램 수집
        print(f"  리뷰 데이터 수집 중...")
        review_histogram = analyzer.get_review_histogram(app_id)
        
        if not review_histogram:
            print(f"  ❌ 리뷰 데이터를 가져올 수 없습니다.")
            continue
        
        # 3. 패치 영향 분석
        print(f"  패치 영향 분석 중...")
        analysis_df = analyzer.analyze_patch_impact(patch_notes, review_histogram, window_days=7)
        
        # 4. CSV 저장
        analyzer.save_to_csv(patch_notes, analysis_df, game_name, app_id)
        
        # 5. 간단한 통계 출력
        if analysis_df is not None and len(analysis_df) > 0:
            print(f"\n  📊 {game_name} 분석 결과:")
            print(f"     - 분석된 패치: {len(analysis_df)}개")
            print(f"     - 평균 패치노트 길이: {analysis_df['patch_length'].mean():.0f}자")
            print(f"     - 평균 리뷰 증가율: {analysis_df['review_count_change_pct'].mean():.1f}%")
            print(f"     - 평균 긍정 비율 변화: {analysis_df['positive_ratio_change'].mean():.1f}%p")
            
            # 글자 수와 반응의 상관관계
            correlation = analysis_df[['patch_length', 'review_count_change_pct', 'positive_ratio_change']].corr()
            print(f"\n     상관관계 분석:")
            print(f"     - 패치 길이 vs 리뷰 증가율: {correlation.loc['patch_length', 'review_count_change_pct']:.3f}")
            print(f"     - 패치 길이 vs 긍정 비율 변화: {correlation.loc['patch_length', 'positive_ratio_change']:.3f}")
        
        print()
    
    print("=" * 80)
    print("분석 완료!")
    print("=" * 80)


if __name__ == "__main__":
    main()
