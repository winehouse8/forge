# 정보의 허브 관리 전략

## 개요

**정보의 허브(Information Hub)**는 특정 분야의 고품질 정보가 집중된 신뢰할 수 있는 출처입니다.

```
핵심 아이디어:
  일반 검색 → 노이즈 많음
  허브 + 검색 → 고품질 정보 직행
```

---

## 허브 유형

### 1. 학술/연구 허브

| 허브 | 분야 | 특징 |
|------|------|------|
| arxiv.org | 물리학, CS, 수학 | 프리프린트, 최신 연구 |
| pubmed.gov | 의학, 생명과학 | peer-reviewed |
| scholar.google.com | 전 분야 | 인용 추적 |
| semanticscholar.org | AI/ML 강점 | 논문 요약 |
| ieee.org | 공학 | 표준, 저널 |
| nature.com | 과학 전반 | 고영향력 저널 |
| science.org | 과학 전반 | 고영향력 저널 |

### 2. 기술/개발 허브

| 허브 | 분야 | 특징 |
|------|------|------|
| github.com | 코드, OSS | 실제 구현 |
| stackoverflow.com | 프로그래밍 | Q&A, 실용적 |
| hackernews (news.ycombinator.com) | 테크 뉴스 | 업계 트렌드 |
| dev.to | 개발자 커뮤니티 | 튜토리얼 |
| medium.com/tag/[tech] | 기술 블로그 | 다양한 관점 |

### 3. 비즈니스/스타트업 허브

| 허브 | 분야 | 특징 |
|------|------|------|
| ycombinator.com | 스타트업 | 창업자 조언 |
| a16z.com | VC/스타트업 | 트렌드 분석 |
| hbr.org | 경영 | 학술 + 실무 |
| mckinsey.com | 컨설팅 | 산업 리포트 |
| techcrunch.com | 스타트업 뉴스 | 펀딩, 출시 |

### 4. AI/ML 특화 허브

| 허브 | 분야 | 특징 |
|------|------|------|
| huggingface.co | 모델, 데이터셋 | 실제 활용 |
| paperswithcode.com | 논문 + 코드 | 벤치마크 |
| openai.com/research | GPT 계열 | 최신 연구 |
| deepmind.com/research | AI 연구 | 알고리즘 |
| distill.pub | ML 설명 | 시각화 |

---

## 허브 발견 휴리스틱

### 검색 결과에서 허브 식별

```markdown
평가 기준:

1. 전문성 (Expertise)
   - 해당 분야 전문 사이트인가?
   - 저자/기관의 신뢰성?
   +0.1 ~ +0.3

2. 일관성 (Consistency)
   - 여러 검색에서 반복 등장?
   - 다른 출처에서 인용/추천?
   +0.1 ~ +0.3

3. 깊이 (Depth)
   - 피상적 vs 심층적 콘텐츠?
   - 원본 연구/분석 포함?
   +0.1 ~ +0.3

4. 신뢰성 (Credibility)
   - 기관/조직 배경?
   - peer-review 여부?
   +0.1 ~ +0.3

최종 점수: 0.0 ~ 1.0
임계값: 0.70 이상 → 허브로 추가
```

### 자동 허브 후보 탐지

```python
def detect_hub_candidate(search_result):
    domain = extract_domain(search_result.url)

    # 이미 알려진 허브 도메인?
    if domain in KNOWN_HUB_DOMAINS:
        return True, HIGH_CONFIDENCE

    # 휴리스틱 평가
    score = 0.0

    # 도메인 패턴
    if ".edu" in domain or ".gov" in domain:
        score += 0.2
    if ".org" in domain:
        score += 0.1

    # 콘텐츠 신호
    if search_result.has_citations:
        score += 0.2
    if search_result.has_author_info:
        score += 0.1
    if search_result.content_length > 2000:
        score += 0.1

    return score >= 0.70, score
```

---

## 허브 활용 전략

### 1. site: 연산자

```
site:arxiv.org "quantum error correction"
site:ycombinator.com "fundraising strategy"
```

**장점:** 해당 사이트 내 검색으로 한정
**단점:** 해당 사이트에 없는 정보 놓침

### 2. 허브 이름 조합

```
"Y Combinator" startup advice
"Nature" quantum computing breakthrough
```

**장점:** 허브 관련 외부 언급도 포함
**단점:** 노이즈 증가 가능

### 3. 혼합 전략 (권장)

```python
def generate_enhanced_queries(original_query, hubs):
    queries = [original_query]  # 기본

    for hub in hubs[:3]:  # 상위 3개만
        # site: 연산자
        queries.append(f"site:{hub.domain} {original_query}")

        # 허브 이름 조합 (품질 높은 허브만)
        if hub.quality_score > 0.85:
            queries.append(f"{hub.name} {original_query}")

    return deduplicate(queries)
```

---

## 허브 품질 관리

### 품질 점수 계산

```python
def calculate_quality_score(hub):
    # 기본 점수 (초기 평가)
    base_score = hub.initial_score

    # 히트율 반영
    if hub.hit_count + hub.miss_count > 0:
        hit_rate = hub.hit_count / (hub.hit_count + hub.miss_count)
    else:
        hit_rate = 0.5  # 데이터 없으면 중립

    # 가중 평균
    # 초기에는 base_score 비중 높게, 데이터 쌓이면 hit_rate 비중 높게
    total_uses = hub.hit_count + hub.miss_count
    weight = min(total_uses / 10, 1.0)  # 10회 사용 후 완전 전환

    quality = (1 - weight) * base_score + weight * hit_rate

    return quality
```

### 품질 저하 대응

```python
def handle_quality_degradation(hub):
    if hub.quality_score < 0.50:
        # 옵션 1: 경고
        log_warning(f"Hub quality low: {hub.name}")

        # 옵션 2: 비활성화
        hub.status = "deprecated"

        # 옵션 3: 삭제 (극단적)
        # remove_hub(hub.id)

    elif hub.quality_score < 0.60:
        # 우선순위 낮춤
        hub.priority = "low"
```

---

## info_hubs.json 스키마

```json
{
  "version": "1.0",
  "last_updated": "2026-02-01T03:45:00Z",
  "hubs": [
    {
      "id": "hub_1",
      "domain": "arxiv.org",
      "name": "arXiv",
      "category": "academic",
      "subcategory": "preprint",
      "quality_score": 0.95,
      "initial_score": 0.90,
      "hit_count": 15,
      "miss_count": 2,
      "discovered_at": "iteration_0",
      "last_used": "iteration_12",
      "status": "active",
      "priority": "high",
      "notes": "물리학, CS, 수학 프리프린트",
      "search_patterns": [
        "site:arxiv.org",
        "arXiv"
      ]
    }
  ],
  "category_index": {
    "academic": ["hub_1", "hub_2"],
    "tech": ["hub_3", "hub_4"],
    "business": ["hub_5"]
  },
  "stats": {
    "total_hubs": 5,
    "active_hubs": 5,
    "deprecated_hubs": 0,
    "avg_quality": 0.85
  }
}
```

---

## 모범 사례

### DO

- 첫 iteration에서 허브 탐색 (HUB_SCOUT)
- 검색 결과마다 허브 후보 평가
- 허브 품질 지속 추적
- 상위 2-3개 허브만 활용 (과도한 확장 방지)

### DON'T

- 모든 검색에 모든 허브 적용 (쿼리 폭발)
- 품질 저하 허브 계속 사용
- 허브 없이 일반 검색만 의존
- 초기 허브 고정 (새 허브 발견 안 함)

---

## 예시 시나리오

### 스타트업 펀딩 연구

```markdown
HUB_SCOUT 결과:
  1. ycombinator.com (0.95)
  2. a16z.com (0.90)
  3. techcrunch.com (0.75)

검색 쿼리: "Series A fundraising strategy"

확장:
  - "Series A fundraising strategy"
  - "site:ycombinator.com Series A fundraising"
  - "Y Combinator Series A fundraising"
  - "site:a16z.com Series A fundraising"

결과: YC와 a16z의 고급 인사이트 직접 접근!
```

### AI 연구 조사

```markdown
HUB_SCOUT 결과:
  1. arxiv.org (0.95)
  2. paperswithcode.com (0.90)
  3. huggingface.co (0.85)

검색 쿼리: "transformer attention mechanism"

확장:
  - "transformer attention mechanism"
  - "site:arxiv.org transformer attention"
  - "site:paperswithcode.com attention mechanism"
  - "Hugging Face transformer attention"

결과: 최신 논문 + 코드 구현 + 실제 모델 접근!
```
