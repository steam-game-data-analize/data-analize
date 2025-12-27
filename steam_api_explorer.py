import requests
import json
from datetime import datetime, timedelta
import time
import csv
import pandas as pd
import os

class SteamAPIExplorer:
    """
    Steam API 탐색 도구 - 리뷰 데이터 및 지표 수집
    """
    
    def __init__(self):
        self.base_url = "https://store.steampowered.com"
        
    def get_app_reviews(self, app_id, params=None):
        """
        특정 게임의 리뷰 데이터 가져오기
        
        Parameters:
        - app_id: Steam 게임 ID
        - params: 추가 파라미터 (filter, day_range, cursor 등)
        """
        url = f"{self.base_url}/appreviews/{app_id}"
        
        default_params = {
            'json': 1,
            'language': 'all',
            'review_type': 'all',
            'purchase_type': 'all',
        }
        
        if params:
            default_params.update(params)
            
        try:
            response = requests.get(url, params=default_params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching reviews: {e}")
            return None
    
    def get_review_histogram(self, app_id):
        """
        날짜별 리뷰 히스토그램 데이터 가져오기
        이 API는 시간에 따른 긍정/부정 리뷰 수를 제공
        """
        url = f"{self.base_url}/appreviewhistogram/{app_id}"
        
        try:
            response = requests.get(url, params={'l': 'english'})
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching histogram: {e}")
            return None
    
    def get_app_details(self, app_id):
        """
        게임의 상세 정보 가져오기 (전체 리뷰 점수 포함)
        """
        url = f"{self.base_url}/api/appdetails"
        
        try:
            response = requests.get(url, params={'appids': app_id})
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching app details: {e}")
            return None
    
    def collect_game_data(self, app_id, game_name):
        """
        게임 데이터를 수집하여 구조화된 형태로 반환
        """
        print(f"데이터 수집 중: {game_name} (App ID: {app_id})")
        
        game_data = {
            'app_id': app_id,
            'game_name': game_name,
            'reviews': [],
            'histogram_daily': [],
            'histogram_monthly': [],
            'game_info': {},
            'summary': {}
        }
        
        reviews_data = self.get_app_reviews(app_id)
        if reviews_data and reviews_data.get('success') == 1:
            query_summary = reviews_data.get('query_summary', {})
            game_data['summary'] = {
                'total_reviews': query_summary.get('total_reviews', 0),
                'total_positive': query_summary.get('total_positive', 0),
                'total_negative': query_summary.get('total_negative', 0),
                'review_score': query_summary.get('review_score', 0),
                'review_score_desc': query_summary.get('review_score_desc', 'N/A')
            }
            
            reviews = reviews_data.get('reviews', [])
            for review in reviews:
                author = review.get('author', {})
                game_data['reviews'].append({
                    'recommendationid': review.get('recommendationid'),
                    'voted_up': review.get('voted_up'),
                    'votes_up': review.get('votes_up'),
                    'votes_funny': review.get('votes_funny'),
                    'weighted_vote_score': review.get('weighted_vote_score'),
                    'comment_count': review.get('comment_count'),
                    'timestamp_created': review.get('timestamp_created'),
                    'timestamp_updated': review.get('timestamp_updated'),
                    'review_length': len(review.get('review', '')),
                    'playtime_forever': author.get('playtime_forever'),
                    'playtime_at_review': author.get('playtime_at_review'),
                    'num_games_owned': author.get('num_games_owned'),
                    'num_reviews': author.get('num_reviews')
                })
        
        time.sleep(1)
        
        histogram_data = self.get_review_histogram(app_id)
        if histogram_data and histogram_data.get('success') == 1:
            results = histogram_data.get('results', {})
            if isinstance(results, dict) and 'rollups' in results:
                rollups = results['rollups']
                for rollup in rollups:
                    if isinstance(rollup, dict):
                        date = datetime.fromtimestamp(rollup.get('date', 0))
                        game_data['histogram_daily'].append({
                            'date': date.strftime('%Y-%m-%d'),
                            'recommendations_up': rollup.get('recommendations_up', 0),
                            'recommendations_down': rollup.get('recommendations_down', 0)
                        })
        
        time.sleep(1)
        
        app_details = self.get_app_details(app_id)
        if app_details and str(app_id) in app_details:
            data = app_details[str(app_id)].get('data', {})
            if data:
                game_data['game_info'] = {
                    'name': data.get('name', 'N/A'),
                    'release_date': data.get('release_date', {}).get('date', 'N/A'),
                    'developers': ', '.join(data.get('developers', [])),
                    'genres': ', '.join([g.get('description', '') for g in data.get('genres', [])]),
                    'metacritic_score': data.get('metacritic', {}).get('score', 'N/A')
                }
        
        recent_reviews = self.get_app_reviews(app_id, {'day_range': 30})
        if recent_reviews and recent_reviews.get('success') == 1:
            summary = recent_reviews.get('query_summary', {})
            game_data['summary']['recent_30days'] = {
                'total_reviews': summary.get('total_reviews', 0),
                'total_positive': summary.get('total_positive', 0),
                'total_negative': summary.get('total_negative', 0),
                'review_score_desc': summary.get('review_score_desc', 'N/A')
            }
        
        print(f"✓ {game_name} 데이터 수집 완료")
        return game_data
    
    def save_to_csv(self, game_data, output_dir='output'):
        """
        수집된 게임 데이터를 CSV 파일로 저장
        """
        os.makedirs(output_dir, exist_ok=True)
        
        game_name_safe = game_data['game_name'].replace('/', '_').replace('\\', '_').replace(':', '_')
        app_id = game_data['app_id']
        
        if game_data['reviews']:
            reviews_df = pd.DataFrame(game_data['reviews'])
            reviews_file = os.path.join(output_dir, f"{app_id}_{game_name_safe}_reviews.csv")
            reviews_df.to_csv(reviews_file, index=False, encoding='utf-8-sig')
            print(f"  ✓ 리뷰 데이터 저장: {reviews_file}")
        
        if game_data['histogram_daily']:
            daily_df = pd.DataFrame(game_data['histogram_daily'])
            daily_file = os.path.join(output_dir, f"{app_id}_{game_name_safe}_daily_histogram.csv")
            daily_df.to_csv(daily_file, index=False, encoding='utf-8-sig')
            print(f"  ✓ 일별 히스토그램 저장: {daily_file}")
        
        summary_data = [{
            'app_id': game_data['app_id'],
            'game_name': game_data['game_name'],
            'total_reviews': game_data['summary'].get('total_reviews', 0),
            'total_positive': game_data['summary'].get('total_positive', 0),
            'total_negative': game_data['summary'].get('total_negative', 0),
            'review_score': game_data['summary'].get('review_score', 0),
            'review_score_desc': game_data['summary'].get('review_score_desc', 'N/A'),
            'game_name_full': game_data['game_info'].get('name', 'N/A'),
            'release_date': game_data['game_info'].get('release_date', 'N/A'),
            'developers': game_data['game_info'].get('developers', 'N/A'),
            'genres': game_data['game_info'].get('genres', 'N/A'),
            'metacritic_score': game_data['game_info'].get('metacritic_score', 'N/A')
        }]
        
        if 'recent_30days' in game_data['summary']:
            recent = game_data['summary']['recent_30days']
            summary_data[0].update({
                'recent_30days_total': recent.get('total_reviews', 0),
                'recent_30days_positive': recent.get('total_positive', 0),
                'recent_30days_negative': recent.get('total_negative', 0),
                'recent_30days_score_desc': recent.get('review_score_desc', 'N/A')
            })
        
        summary_df = pd.DataFrame(summary_data)
        summary_file = os.path.join(output_dir, f"{app_id}_{game_name_safe}_summary.csv")
        summary_df.to_csv(summary_file, index=False, encoding='utf-8-sig')
        print(f"  ✓ 요약 정보 저장: {summary_file}")


def main():
    """
    메인 실행 함수
    """
    explorer = SteamAPIExplorer()
    
    games = [
        (1049590, "Eternal Return"),
        (1973530, "Limbus Company"),
        (730, "Counter-Strike 2"),
        (440, "Team Fortress 2"),
    ]
    
    print("\n" + "="*80)
    print(f"Steam 게임 데이터 수집 시작 - 총 {len(games)}개 게임")
    print("="*80 + "\n")
    
    for app_id, game_name in games:
        game_data = explorer.collect_game_data(app_id, game_name)
        explorer.save_to_csv(game_data)
        print()
        time.sleep(2)
    
    print("="*80)
    print("모든 게임 데이터 수집 및 CSV 저장 완료")
    print("출력 디렉토리: output/")
    print("="*80)


if __name__ == "__main__":
    main()
