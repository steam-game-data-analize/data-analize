# Steam Game Data Analysis

Steam 게임의 리뷰 데이터와 패치노트를 분석하여 유저 반응 패턴을 시각화하는 데이터 분석 프로젝트

## 📊 주요 기능

### 1. 리뷰 데이터 분석
- 월별 긍정/부정 리뷰 수 추이
- 긍정 리뷰 비율 변화
- 총 리뷰 수 추이
- 게임 간 비교 분석

### 2. 패치노트 분석
- 패치노트 길이 분포 및 통계
- 시간에 따른 패치노트 길이 변화
- 패치노트 발표 타임라인 (리뷰 수와 함께 시각화)
- 길이별 패치노트 분류

### 3. 상관관계 분석
- 패치노트 길이 vs 리뷰 증가율
- 패치노트 길이 vs 긍정 비율 변화
- 패치노트 길이 vs 유저 참여도
- 길이 구간별 평균 유저 반응

## 🚀 빠른 시작

### 필수 요구사항
- Python 3.8+
- uv (Python 패키지 관리자)

### 설치

```bash
# 저장소 클론
git clone https://github.com/yourusername/data-analize.git
cd data-analize

# 의존성 설치
uv pip install -r requirements.txt
```

### 실행

**전체 파이프라인 실행 (데이터 수집 → 분석 → 시각화)**

```bash
uv run generate_all_visualizations.py
```

이 명령어 하나로 다음 작업이 자동으로 실행됩니다:
1. Steam API에서 리뷰 데이터 수집
2. Steam News API에서 패치노트 수집
3. 데이터 전처리 및 분석
4. 모든 시각화 차트 생성

## 📁 프로젝트 구조

```
data-analize/
├── generate_all_visualizations.py  # 메인 실행 파일
├── util/                           # 유틸리티 모듈
│   ├── collector.py                # Steam 리뷰 데이터 수집
│   ├── patch_collector.py          # 패치노트 수집
│   ├── analyzer.py                 # 상관관계 분석
│   ├── viz_reviews.py              # 리뷰 데이터 시각화
│   └── viz_patches.py              # 패치노트 시각화
├── output/                         # CSV 데이터 출력
├── visualizations/                 # PNG 차트 출력
├── requirements.txt                # Python 의존성
├── .gitignore                      # Git 제외 설정
└── README.md                       # 프로젝트 문서
```

## 📈 생성되는 데이터

### CSV 파일 (output/)
- `{game_id}_{game_name}_reviews.csv` - 개별 리뷰 데이터
- `{game_id}_{game_name}_daily_histogram.csv` - 월별 리뷰 히스토그램
- `{game_id}_{game_name}_summary.csv` - 게임 요약 정보
- `{game_id}_{game_name}_patch_notes.csv` - 패치노트 원본
- `{game_id}_{game_name}_patch_impact.csv` - 패치 영향 분석

### 시각화 차트 (visualizations/)
각 게임당 3개의 차트 생성:
1. `{game_id}_{game_name}_analysis.png` - 리뷰 추이 분석 (3개 서브플롯)
2. `{game_id}_{game_name}_patch_analysis.png` - 패치노트 분석 (4개 서브플롯)
3. `{game_id}_{game_name}_correlation.png` - 상관관계 분석 (6개 서브플롯)

추가로 게임 간 비교 차트 1개 생성

## 🎮 분석 대상 게임

기본적으로 다음 게임들을 분석합니다:
- Eternal Return (App ID: 1049590)
- Limbus Company (App ID: 1973530)
- Counter-Strike 2 (App ID: 730)
- Team Fortress 2 (App ID: 440)

게임 목록은 `generate_all_visualizations.py`의 `games` 리스트에서 수정 가능합니다.

## 🔧 모듈 설명

### util/collector.py
Steam API를 통해 리뷰 데이터를 수집합니다.
- `get_app_reviews()` - 게임 리뷰 가져오기
- `get_review_histogram()` - 월별 리뷰 히스토그램
- `get_app_details()` - 게임 상세 정보
- `collect_game_data()` - 전체 데이터 수집
- `save_to_csv()` - CSV 저장

### util/patch_collector.py
Steam News API를 통해 패치노트를 수집하고 분석합니다.
- `get_app_news()` - 게임 뉴스/패치노트 가져오기
- `clean_html()` - HTML 태그 제거
- `is_patch_note()` - 패치노트 여부 판별
- `collect_patch_notes()` - 패치노트 수집
- `analyze_patch_impact()` - 패치 전후 리뷰 변화 분석

### util/analyzer.py
패치노트 길이와 유저 반응의 상관관계를 분석합니다.
- `analyze_patch_review_correlation()` - 상관관계 분석
- `create_correlation_visualization()` - 상관관계 시각화

### util/viz_reviews.py
리뷰 데이터를 시각화합니다.
- `visualize_game_data()` - 게임별 리뷰 추이 차트
- `create_comparison_chart()` - 게임 간 비교 차트

### util/viz_patches.py
패치노트 데이터를 시각화합니다.
- `visualize_patch_notes()` - 패치노트 분석 차트

## 📊 주요 지표

### 리뷰 분석 지표
- **월별 긍정/부정 리뷰 수**: 시간에 따른 리뷰 추이
- **긍정 리뷰 비율**: 긍정 리뷰 / 전체 리뷰 × 100
- **총 리뷰 수**: 월별 전체 리뷰 활동량

### 패치노트 분석 지표
- **패치노트 길이**: HTML 제거 후 순수 텍스트 글자 수
- **패치 빈도**: 시간당 패치 발표 횟수
- **길이 분포**: 매우 짧음(~500자) ~ 매우 김(5000자+)

### 상관관계 지표
- **리뷰 증가율**: (패치 후 평균 리뷰 - 패치 전 평균 리뷰) / 패치 전 평균 리뷰 × 100
- **긍정 비율 변화**: 패치 후 긍정 비율 - 패치 전 긍정 비율
- **참여도 점수**: 패치 후 평균 리뷰 / 패치 전 평균 리뷰
- **상관계수**: Pearson 상관계수 (-1 ~ 1)

## 🛠️ 기술 스택

- **Python 3.8+**
- **pandas** - 데이터 처리
- **matplotlib** - 데이터 시각화
- **requests** - API 호출
- **beautifulsoup4** - HTML 파싱
- **scipy** - 통계 분석

## 📝 사용 예시

### 특정 게임만 분석하기

`generate_all_visualizations.py`를 수정:

```python
games = [
    {'app_id': 1049590, 'name': 'Eternal Return'},
]
```

### 분석 기간 조정

`util/analyzer.py`의 `window_days` 파라미터 수정:

```python
# 패치 전후 30일로 변경
analysis_df = analyzer.analyze_patch_impact(patch_notes, review_histogram, window_days=30)
```

## 🤝 기여

이슈 제보 및 풀 리퀘스트를 환영합니다!

## 📄 라이선스

MIT License

## 👤 작성자

Your Name

## 🙏 감사의 말

- Steam API 제공: Valve Corporation
- 데이터 시각화 영감: matplotlib 커뮤니티