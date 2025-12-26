import requests
import json
from datetime import datetime, timedelta
import time

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
    
    def analyze_review_data(self, app_id, sample_game_name="Sample Game"):
        """
        리뷰 데이터 분석 및 사용 가능한 지표 출력
        """
        print(f"\n{'='*80}")
        print(f"Steam API 분석: {sample_game_name} (App ID: {app_id})")
        print(f"{'='*80}\n")
        
        # 1. 기본 리뷰 데이터
        print("1. 기본 리뷰 데이터 (appreviews API)")
        print("-" * 80)
        reviews_data = self.get_app_reviews(app_id)
        
        if reviews_data and reviews_data.get('success') == 1:
            query_summary = reviews_data.get('query_summary', {})
            
            print(f"✓ 총 리뷰 수: {query_summary.get('total_reviews', 0)}")
            print(f"✓ 긍정 리뷰 수: {query_summary.get('total_positive', 0)}")
            print(f"✓ 부정 리뷰 수: {query_summary.get('total_negative', 0)}")
            print(f"✓ 리뷰 점수: {query_summary.get('review_score', 0)}")
            print(f"✓ 리뷰 점수 설명: {query_summary.get('review_score_desc', 'N/A')}")
            
            # 개별 리뷰 샘플
            reviews = reviews_data.get('reviews', [])
            if reviews:
                print(f"\n개별 리뷰 데이터 필드 (샘플):")
                sample_review = reviews[0]
                print(f"  - recommendationid: {sample_review.get('recommendationid')}")
                print(f"  - voted_up (긍정 여부): {sample_review.get('voted_up')}")
                print(f"  - votes_up (도움됨 투표): {sample_review.get('votes_up')}")
                print(f"  - votes_funny (재미있음 투표): {sample_review.get('votes_funny')}")
                print(f"  - weighted_vote_score: {sample_review.get('weighted_vote_score')}")
                print(f"  - comment_count (댓글 수): {sample_review.get('comment_count')}")
                print(f"  - timestamp_created: {sample_review.get('timestamp_created')}")
                print(f"  - timestamp_updated: {sample_review.get('timestamp_updated')}")
                print(f"  - review (리뷰 텍스트 길이): {len(sample_review.get('review', ''))}")
                
                author = sample_review.get('author', {})
                print(f"  - author.playtime_forever (총 플레이 시간): {author.get('playtime_forever')} 분")
                print(f"  - author.playtime_at_review (리뷰 작성 시 플레이 시간): {author.get('playtime_at_review')} 분")
                print(f"  - author.num_games_owned: {author.get('num_games_owned')}")
                print(f"  - author.num_reviews: {author.get('num_reviews')}")
        
        time.sleep(1)
        
        # 2. 리뷰 히스토그램 (날짜별 데이터)
        print(f"\n2. 리뷰 히스토그램 (appreviewhistogram API)")
        print("-" * 80)
        histogram_data = self.get_review_histogram(app_id)
        
        if histogram_data and histogram_data.get('success') == 1:
            print(f"✓ 날짜별 리뷰 분포 데이터 사용 가능")
            
            # 롤업 데이터 (월별 집계)
            rollups = histogram_data.get('rollups', [])
            if rollups:
                print(f"\n월별 집계 데이터:")
                for i, rollup in enumerate(rollups[:3]):  # 최근 3개월만 표시
                    date = datetime.fromtimestamp(rollup.get('date', 0))
                    print(f"  {date.strftime('%Y-%m')}: "
                          f"긍정 {rollup.get('recommendations_up', 0)}, "
                          f"부정 {rollup.get('recommendations_down', 0)}")
            
            # 일별 데이터
            results = histogram_data.get('results', [])
            if results:
                print(f"\n일별 데이터 샘플 (최근 3일):")
                for i, result in enumerate(results[:3]):
                    date = datetime.fromtimestamp(result.get('date', 0))
                    print(f"  {date.strftime('%Y-%m-%d')}: "
                          f"긍정 {result.get('recommendations_up', 0)}, "
                          f"부정 {result.get('recommendations_down', 0)}")
        
        time.sleep(1)
        
        # 3. 앱 상세 정보
        print(f"\n3. 게임 상세 정보 (appdetails API)")
        print("-" * 80)
        app_details = self.get_app_details(app_id)
        
        if app_details and str(app_id) in app_details:
            data = app_details[str(app_id)].get('data', {})
            if data:
                print(f"✓ 게임 이름: {data.get('name', 'N/A')}")
                print(f"✓ 출시일: {data.get('release_date', {}).get('date', 'N/A')}")
                print(f"✓ 개발사: {', '.join(data.get('developers', []))}")
                print(f"✓ 장르: {', '.join([g.get('description', '') for g in data.get('genres', [])])}")
                
                # 메타크리틱 점수
                metacritic = data.get('metacritic', {})
                if metacritic:
                    print(f"✓ 메타크리틱 점수: {metacritic.get('score', 'N/A')}")
        
        # 4. 추가 파라미터 테스트
        print(f"\n4. 날짜 필터링 옵션")
        print("-" * 80)
        
        # day_range 파라미터로 특정 기간의 리뷰만 가져오기
        recent_reviews = self.get_app_reviews(app_id, {'day_range': 30})
        if recent_reviews and recent_reviews.get('success') == 1:
            summary = recent_reviews.get('query_summary', {})
            print(f"✓ 최근 30일 리뷰:")
            print(f"  - 총 리뷰: {summary.get('total_reviews', 0)}")
            print(f"  - 긍정: {summary.get('total_positive', 0)}")
            print(f"  - 부정: {summary.get('total_negative', 0)}")
            print(f"  - 점수 설명: {summary.get('review_score_desc', 'N/A')}")
        
        print(f"\n{'='*80}")
        print("분석 완료")
        print(f"{'='*80}\n")


def main():
    """
    메인 실행 함수
    """
    explorer = SteamAPIExplorer()
    
    # 분석할 게임 목록
    games = [
        (1049590, "Eternal Return (이터널리턴)"),
        (1973530, "Limbus Company (림버스 컴퍼니)"),
        (730, "Counter-Strike 2 (카운터 스트라이크 2)"),
        (440, "Team Fortress 2 (팀포트리스 2)"),
    ]
    
    print("\n" + "="*80)
    print("여러 게임 분석 시작")
    print("="*80)
    print(f"총 {len(games)}개 게임 분석 예정")
    print("참고: Overwatch는 Steam에 없어 분석 불가 (Blizzard 독점)")
    print("="*80 + "\n")
    
    for app_id, game_name in games:
        explorer.analyze_review_data(app_id, game_name)
        print("\n" + "="*80)
        print(f"다음 게임으로 이동...")
        print("="*80 + "\n")
        time.sleep(2)
    
    print("\n" + "="*80)
    print("패치노트 분석을 위한 추천 지표")
    print("="*80)
    print("""
1. **시간별 사용자 반응 지표**:
   - 날짜별 긍정/부정 리뷰 비율 (appreviewhistogram API)
   - 리뷰 점수 변화 추이 (review_score_desc: 압도적으로 긍정적, 매우 긍정적 등)
   - 일별/주별/월별 리뷰 수 변화

2. **리뷰 품질 지표**:
   - 리뷰 텍스트 길이 (review 필드)
   - 도움됨 투표 수 (votes_up)
   - 가중 투표 점수 (weighted_vote_score)
   - 댓글 수 (comment_count)

3. **사용자 참여도 지표**:
   - 리뷰 작성 시 플레이 시간 (playtime_at_review)
   - 총 플레이 시간 (playtime_forever)
   - 리뷰 업데이트 여부 (timestamp_updated vs timestamp_created)

4. **패치 전후 비교 지표**:
   - 패치 전 7일 vs 패치 후 7일 긍정 비율 변화
   - 패치 전후 리뷰 수 변화 (사용자 관심도)
   - 패치 전후 평균 플레이 시간 변화

5. **패치노트 관련 지표**:
   - 패치노트 글자 수
   - 패치노트 항목 개수
   - 패치 유형 (버그 수정, 밸런스 조정, 신규 콘텐츠 등)
   - 패치 규모 (major/minor)

6. **감성 분석 지표** (리뷰 텍스트 분석 필요):
   - 긍정/부정 키워드 빈도
   - 패치노트 언급 여부
   - 특정 이슈 언급 빈도

**연구 설계 제안**:
1. 여러 게임의 주요 패치 날짜 수집
2. 각 패치의 패치노트 수집 및 글자 수 측정
3. 패치 전후 리뷰 데이터 수집 (appreviewhistogram API 사용)
4. 패치노트 글자 수와 사용자 반응 변화의 상관관계 분석
5. 게임 장르, 규모 등 통제 변수 고려
    """)


if __name__ == "__main__":
    main()
