# Research Skill 계획서 v2

> **기반 연구**: Deep Research Survey (arXiv:2508.12752), Anthropic Context Engineering, LATS, Reflexion 등 최신 연구 종합

---

## 1. 핵심 아키텍처 개선

### 1.1 4단계 Deep Research 파이프라인 (Survey 기반)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        DEEP RESEARCH PIPELINE                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────┐    ┌───────────┐ │
│  │ PLANNING │ → │   QUESTION   │ → │     WEB      │ → │  REPORT   │ │
│  │          │    │  DEVELOPING  │    │ EXPLORATION  │    │GENERATION │ │
│  └──────────┘    └──────────────┘    └──────────────┘    └───────────┘ │
│       │                │                    │                  │        │
│       ↓                ↓                    ↓                  ↓        │
│  - 연구질문 분해    - 서브쿼리 생성      - API/브라우저     - 구조 제어   │
│  - 실행계획 수립    - 다양성 & 특수성   - 반복 검색        - 사실 무결성 │
│  - World Model     - RL 최적화          - 신뢰도 평가      - 인용 관리   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.2 v1 대비 주요 개선점

| 영역 | v1 | v2 |
|------|----|----|
| **플래닝** | 단순 서브태스크 분해 | World Model 기반 시뮬레이션 + 적응형 계획 |
| **쿼리 생성** | 정적 검색어 | RL 최적화 + Multi-dimensional Reward |
| **검색** | 단일 검색 도구 | Hybrid (API + Browser Agent) + 신뢰도 평가 |
| **메모리** | 파일 기반 단순 저장 | Temporal Knowledge Graph + Compaction |
| **추론** | CoT 단일 경로 | Self-Consistency + Tree of Thoughts |
| **평가** | 수동 확인 | 자동 Factuality Verification |

---

## 2. 사고 프레임워크 (Reasoning Engines)

### 2.1 추론 방식 선택 전략

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      REASONING MODE SELECTOR                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   질문 복잡도 평가                                                        │
│         │                                                                │
│         ├─── 단순 (사실 확인) ──→ Chain-of-Thought (CoT)                │
│         │                                                                │
│         ├─── 중간 (비교/분석) ──→ Self-Consistency (다중 경로)          │
│         │                                                                │
│         ├─── 복잡 (다단계 추론) ──→ Tree of Thoughts (ToT)              │
│         │                                                                │
│         └─── 매우 복잡 (탐색적) ──→ LATS (Monte Carlo Tree Search)      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Self-Consistency 구현

```python
# 개념적 구현
def self_consistency_reasoning(query, num_paths=5):
    """
    동일 쿼리에 대해 여러 추론 경로를 생성하고
    가장 일관된 답변을 선택
    """
    reasoning_paths = []
    answers = []

    for i in range(num_paths):
        path, answer = generate_reasoning_path(query, temperature=0.7)
        reasoning_paths.append(path)
        answers.append(answer)

    # 다수결 또는 의미적 유사도 기반 선택
    final_answer = select_most_consistent(answers)
    confidence = calculate_agreement_score(answers)

    return {
        "answer": final_answer,
        "confidence": confidence,
        "paths": reasoning_paths,
        "agreement_ratio": count_majority(answers) / num_paths
    }
```

### 2.3 Tree of Thoughts (ToT) 구현

```
                    [연구 질문]
                         │
         ┌───────────────┼───────────────┐
         ↓               ↓               ↓
    [가설 A]        [가설 B]        [가설 C]
    평가: 0.7       평가: 0.85      평가: 0.5
         │               │               │
         │          ✓ 선택              ✗ 가지치기
         │               │
         │      ┌────────┼────────┐
         │      ↓        ↓        ↓
         │   [B-1]    [B-2]    [B-3]
         │   0.9      0.75     0.6
         │      │
         │   ✓ 최선 경로
         │      │
         └──────┴───→ [최종 결론]
```

### 2.4 Reflexion (자기 반성) 루프

```json
{
  "reflexion_memory": [
    {
      "iteration": 3,
      "action": "검색: 'transformer attention complexity'",
      "outcome": "failure",
      "reflection": "검색어가 너무 광범위함. 'self-attention O(n^2) quadratic' 로 구체화 필요",
      "lesson_learned": "복잡도 관련 검색 시 Big-O 표기법 포함"
    },
    {
      "iteration": 4,
      "action": "검색: 'self-attention O(n^2) quadratic complexity'",
      "outcome": "success",
      "reflection": "구체적인 기술 용어 포함 시 관련성 높은 결과 획득",
      "lesson_learned": "기술 개념 검색 시 수학적 표기 포함"
    }
  ]
}
```

---

## 3. 메모리 아키텍처

### 3.1 3-Tier 메모리 시스템

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         MEMORY ARCHITECTURE                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ TIER 1: Working Memory (현재 컨텍스트 윈도우)                    │   │
│  │ - 현재 반복의 즉각적 상태                                        │   │
│  │ - 최근 5개 검색 결과                                             │   │
│  │ - 현재 추론 체인                                                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              │                                          │
│                              ↓ Compaction (80% 임계값)                  │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ TIER 2: Episodic Memory (세션 메모리)                            │   │
│  │ - 현재 리서치 세션의 모든 반복 요약                              │   │
│  │ - Reflexion 기록                                                 │   │
│  │ - 검색 히스토리 및 결과                                          │   │
│  │ 저장: state.json, iteration_logs/                                │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              │                                          │
│                              ↓ 세션 종료 시                             │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ TIER 3: Semantic Memory (장기 지식)                              │   │
│  │ - Temporal Knowledge Graph (Graphiti 스타일)                     │   │
│  │ - 검증된 사실 및 관계                                            │   │
│  │ - 논문/소스 인덱스                                               │   │
│  │ 저장: knowledge_graph.json, paper_index.json                     │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Context Compaction 전략

```markdown
## Compaction 규칙

### 언제 Compaction 실행?
- 토큰 사용량이 컨텍스트 윈도우의 80% 도달 시
- 반복 5회마다 자동 실행

### 무엇을 보존?
1. **필수 보존**
   - 원본 연구 질문
   - 현재 가설 및 확신도
   - 아직 해결되지 않은 하위 질문
   - 최근 3개 반복의 핵심 발견

2. **요약으로 압축**
   - 이전 반복들의 상세 로그 → 핵심 포인트만
   - 검색 결과 전문 → 관련 발췌문만
   - 추론 체인 → 결론만

3. **제거 가능**
   - 중복 검색 결과
   - 실패한 검색 시도의 상세 내용
   - 이미 통합된 중간 결과
```

### 3.3 Knowledge Graph 구조

```json
{
  "knowledge_graph": {
    "nodes": [
      {
        "id": "concept_001",
        "type": "concept",
        "label": "Self-Attention Mechanism",
        "properties": {
          "definition": "쿼리, 키, 값을 사용한 가중 평균 메커니즘",
          "first_seen": "iteration_2",
          "confidence": 0.95,
          "sources": ["arxiv:1706.03762"]
        }
      },
      {
        "id": "fact_001",
        "type": "fact",
        "label": "Self-attention의 시간복잡도는 O(n²)",
        "properties": {
          "verified": true,
          "sources": ["arxiv:1706.03762", "arxiv:2009.14794"],
          "contradicted_by": []
        }
      }
    ],
    "edges": [
      {
        "source": "concept_001",
        "target": "fact_001",
        "relation": "HAS_PROPERTY",
        "confidence": 0.95
      }
    ],
    "temporal_markers": {
      "last_updated": "2024-01-15T10:30:00Z",
      "version": 5
    }
  }
}
```

---

## 4. 검색 전략 (Web Exploration)

### 4.1 Hybrid 검색 아키텍처

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      HYBRID SEARCH ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │                    SEARCH ORCHESTRATOR                          │    │
│  │  - 쿼리 분석 및 라우팅                                          │    │
│  │  - 소스 선택 전략                                               │    │
│  │  - 결과 병합 및 중복 제거                                        │    │
│  └────────────────────────────────────────────────────────────────┘    │
│                              │                                          │
│          ┌──────────────────┼──────────────────┐                       │
│          ↓                  ↓                  ↓                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │ API Search   │  │ Academic     │  │ Browser      │                  │
│  │              │  │ Search       │  │ Agent        │                  │
│  │ - WebSearch  │  │ - arXiv      │  │ - Playwright │                  │
│  │ - Exa        │  │ - Semantic   │  │ - 동적 콘텐츠│                  │
│  │              │  │   Scholar    │  │ - 인터랙티브 │                  │
│  └──────────────┘  └──────────────┘  └──────────────┘                  │
│          │                  │                  │                        │
│          └──────────────────┼──────────────────┘                       │
│                              ↓                                          │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │                   CREDIBILITY SCORER                            │    │
│  │  - 소스 신뢰도 평가 (도메인, 저자, 인용수)                       │    │
│  │  - 최신성 점수                                                   │    │
│  │  - 교차 검증 (여러 소스에서 확인)                                │    │
│  └────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Query Decomposition 전략

```
원본 질문: "Transformer의 attention mechanism이 왜 효과적인가?"

┌─────────────────────────────────────────────────────────────────────────┐
│                     QUERY DECOMPOSITION TREE                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  [Level 0: 원본 질문]                                                   │
│           │                                                              │
│           ├── [L1: 사실적 질문]                                         │
│           │   ├── "Self-attention mechanism 작동 원리"                  │
│           │   ├── "Attention 수식 (Q, K, V)"                            │
│           │   └── "Transformer vs RNN 아키텍처 차이"                    │
│           │                                                              │
│           ├── [L1: 비교/분석 질문]                                      │
│           │   ├── "Self-attention vs RNN의 장거리 의존성 처리"          │
│           │   ├── "Attention의 계산 복잡도 분석"                        │
│           │   └── "병렬화 가능성 비교"                                  │
│           │                                                              │
│           └── [L1: 인과/설명 질문]                                      │
│               ├── "왜 O(1) path length가 중요한가?"                     │
│               ├── "Attention이 gradient flow를 어떻게 개선하는가?"      │
│               └── "Attention의 해석 가능성이 왜 유용한가?"              │
│                                                                          │
│  분해 타입: PARALLEL (서브질문들이 독립적으로 답변 가능)                │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4.3 소스 신뢰도 평가 시스템

```json
{
  "credibility_scoring": {
    "domain_scores": {
      "arxiv.org": 0.95,
      "nature.com": 0.98,
      "ieee.org": 0.95,
      "acm.org": 0.95,
      "github.com": 0.7,
      "medium.com": 0.5,
      "wikipedia.org": 0.75,
      "unknown": 0.3
    },

    "freshness_decay": {
      "formula": "score = base_score * exp(-lambda * days_since_publish)",
      "lambda": 0.001,
      "note": "최신 정보일수록 높은 점수, 1000일 이상 된 정보는 50% 감소"
    },

    "cross_validation": {
      "single_source": 0.6,
      "two_sources_agree": 0.8,
      "three_plus_sources_agree": 0.95,
      "sources_contradict": "flag_for_review"
    },

    "citation_boost": {
      "formula": "boost = min(1.2, 1 + log10(citations) * 0.05)",
      "note": "인용수 많을수록 최대 20% 부스트"
    }
  }
}
```

---

## 5. Question Developing (쿼리 생성 최적화)

### 5.1 RL 기반 쿼리 최적화

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    RL-OPTIMIZED QUERY GENERATION                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Reward Function (Multi-dimensional):                                    │
│                                                                          │
│  R(query) = w1 * R_format      // 형식 정확성                           │
│           + w2 * R_relevance   // 검색 결과 관련성                       │
│           + w3 * R_diversity   // 기존 쿼리와의 다양성                   │
│           + w4 * R_efficiency  // 최소 검색 횟수로 정보 획득             │
│           - w5 * P_redundancy  // 중복 검색 페널티                       │
│                                                                          │
│  가중치 예시:                                                            │
│  w1=0.1, w2=0.4, w3=0.2, w4=0.2, w5=0.1                                 │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.2 쿼리 다양성 전략

```markdown
## 단일 서브골에서 다양한 쿼리 생성

서브골: "Self-attention의 계산 복잡도 이해"

### 생성된 쿼리들:
1. **정확한 기술 용어**: "self-attention time complexity O(n^2) analysis"
2. **비교 관점**: "self-attention vs linear attention computational cost"
3. **학술 검색**: "site:arxiv.org efficient attention mechanisms survey"
4. **실용적 관점**: "transformer inference optimization memory reduction"
5. **역사적 맥락**: "attention mechanism evolution from RNN to transformer"

### 다양성 검증:
- 단어 겹침(Jaccard): 평균 < 30%
- 의미적 유사도: 코사인 < 0.7
- 타겟 정보 커버리지: > 80%
```

---

## 6. Report Generation (보고서 생성)

### 6.1 구조 제어 시스템

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    REPORT STRUCTURE CONTROLLER                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ 1. OUTLINE PLANNING (개요 계획)                                  │   │
│  │    - 섹션 구조 결정                                              │   │
│  │    - 각 섹션별 목표 단어 수                                      │   │
│  │    - 필요 증거 매핑                                              │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              │                                          │
│                              ↓                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ 2. EVIDENCE INTEGRATION (증거 통합)                              │   │
│  │    - 검색 결과 → 섹션 매핑                                       │   │
│  │    - 중복 제거 및 일관성 확인                                     │   │
│  │    - 인용 준비                                                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              │                                          │
│                              ↓                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ 3. SECTION-WISE GENERATION (섹션별 생성)                         │   │
│  │    - 개요에 따라 순차 생성                                        │   │
│  │    - 이전 섹션과의 일관성 유지                                    │   │
│  │    - 인라인 인용 삽입                                            │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              │                                          │
│                              ↓                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ 4. FACTUALITY VERIFICATION (사실성 검증)                         │   │
│  │    - 각 주장의 소스 확인                                         │   │
│  │    - 모순 탐지                                                   │   │
│  │    - 확신도 태깅                                                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 6.2 인용 및 사실성 관리

```json
{
  "citation_system": {
    "inline_format": "[{author_short} {year}]",
    "example": "[Vaswani et al. 2017]",

    "citation_requirements": {
      "factual_claims": "required",
      "opinions": "optional",
      "well_known_facts": "optional",
      "statistics": "required"
    },

    "verification_levels": {
      "verified": "다수의 신뢰 소스에서 확인됨",
      "likely": "단일 신뢰 소스에서 확인됨",
      "uncertain": "소스가 부족하거나 신뢰도 낮음",
      "contradicted": "소스 간 모순 존재"
    }
  },

  "fact_checking": {
    "process": [
      "1. 주장 추출 (atomic claims)",
      "2. 각 주장에 대한 소스 매칭",
      "3. 교차 검증 (2개 이상 소스)",
      "4. 모순 탐지 및 플래깅"
    ],
    "output_format": {
      "claim": "Self-attention은 O(n²) 복잡도를 가진다",
      "sources": ["arxiv:1706.03762", "arxiv:2009.14794"],
      "verification_status": "verified",
      "confidence": 0.98
    }
  }
}
```

---

## 7. 가설 관리 시스템

### 7.1 가설 생명주기

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      HYPOTHESIS LIFECYCLE                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  [생성] → [평가] → [검증/반증 시도] → [업데이트] → [확정/폐기]          │
│                                                                          │
│  상태 전이:                                                              │
│                                                                          │
│  INITIAL ──(증거 발견)──→ SUPPORTED ──(더 많은 증거)──→ CONFIRMED       │
│     │                          │                              │         │
│     │                          │                              ↓         │
│     │                    (모순 증거)                    [ARCHIVED]       │
│     │                          │                                        │
│     │                          ↓                                        │
│     └──(강한 반증)──→ CONTRADICTED ──(해결 불가)──→ REJECTED            │
│                              │                                          │
│                              └──(부분 수정)──→ REVISED → [재평가]        │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 7.2 확신도 계산 공식

```python
def calculate_confidence(hypothesis):
    """
    가설의 확신도를 다차원적으로 계산
    """
    # 지지 증거 점수
    support_score = sum(
        evidence.credibility * evidence.relevance
        for evidence in hypothesis.supporting_evidence
    )

    # 반증 증거 점수
    contradict_score = sum(
        evidence.credibility * evidence.relevance
        for evidence in hypothesis.contradicting_evidence
    )

    # 소스 다양성 보너스
    source_diversity = len(set(e.source_domain for e in hypothesis.all_evidence))
    diversity_bonus = min(0.1, source_diversity * 0.02)

    # 최종 확신도 (0~1)
    raw_confidence = (support_score - contradict_score) / (support_score + contradict_score + 1)

    # 정규화 및 보너스 적용
    confidence = max(0, min(1, (raw_confidence + 1) / 2 + diversity_bonus))

    return {
        "confidence": confidence,
        "support_count": len(hypothesis.supporting_evidence),
        "contradict_count": len(hypothesis.contradicting_evidence),
        "source_diversity": source_diversity,
        "recommendation": get_recommendation(confidence)
    }

def get_recommendation(confidence):
    if confidence >= 0.9:
        return "ACCEPT: 강한 증거로 지지됨"
    elif confidence >= 0.7:
        return "LIKELY: 추가 검증 권장"
    elif confidence >= 0.5:
        return "UNCERTAIN: 더 많은 증거 필요"
    elif confidence >= 0.3:
        return "DOUBTFUL: 반증 증거 존재"
    else:
        return "REJECT: 강하게 반증됨"
```

---

## 8. 반복 흐름 (Iteration Flow)

### 8.1 단일 반복 상세 흐름

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      SINGLE ITERATION FLOW                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  [1. LOAD & REFLECT]                                                     │
│  ├── state.json 로드                                                    │
│  ├── 이전 반복 결과 분석                                                │
│  ├── Reflexion 메모리 확인                                              │
│  └── 현재 지식 갭 식별                                                  │
│                              │                                          │
│                              ↓                                          │
│  [2. PLAN]                                                               │
│  ├── 추론 모드 선택 (CoT/ToT/LATS)                                      │
│  ├── 이번 반복의 목표 설정                                              │
│  ├── 쿼리 생성 (3-5개)                                                  │
│  └── 검색 전략 결정                                                     │
│                              │                                          │
│                              ↓                                          │
│  [3. EXECUTE]                                                            │
│  ├── 병렬 검색 실행                                                     │
│  │   ├── WebSearch × 3                                                  │
│  │   ├── Academic Search × 2 (필요시)                                   │
│  │   └── WebFetch × N (유망 URL)                                        │
│  ├── 결과 수집 및 신뢰도 평가                                           │
│  └── PDF 다운로드 및 분석 (학술 논문)                                   │
│                              │                                          │
│                              ↓                                          │
│  [4. SYNTHESIZE]                                                         │
│  ├── 새 정보를 기존 지식과 통합                                         │
│  ├── Knowledge Graph 업데이트                                           │
│  ├── 가설 평가 및 업데이트                                              │
│  ├── 모순점 식별 및 기록                                                │
│  └── Self-Consistency 검증 (필요시)                                     │
│                              │                                          │
│                              ↓                                          │
│  [5. SAVE & REPORT]                                                      │
│  ├── state.json 업데이트                                                │
│  ├── iteration_log 작성                                                 │
│  ├── findings.md 업데이트                                               │
│  ├── Context Compaction (필요시)                                        │
│  └── 진행 상황 출력                                                     │
│                              │                                          │
│                              ↓                                          │
│  [6. CONTINUE DECISION]                                                  │
│  ├── max_iterations 체크                                                │
│  ├── 사용자 중단 신호 체크                                              │
│  └── 다음 반복 계획 준비                                                │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 8.2 state.json v2 구조

```json
{
  "version": "2.0",
  "session_id": "research_20240115_001",

  "question": {
    "original": "Transformer의 attention mechanism이 왜 효과적인가?",
    "decomposed": [
      {"id": "q1", "text": "Self-attention 작동 원리", "status": "answered"},
      {"id": "q2", "text": "장거리 의존성 처리 방식", "status": "in_progress"},
      {"id": "q3", "text": "계산 효율성 분석", "status": "pending"}
    ]
  },

  "iteration": {
    "current": 5,
    "max": 100,
    "last_compaction": 3
  },

  "status": "running",

  "hypotheses": [
    {
      "id": "h1",
      "statement": "Self-attention은 O(1) path length로 장거리 의존성을 효과적으로 학습한다",
      "status": "supported",
      "confidence": 0.85,
      "supporting_evidence": ["e001", "e003", "e005"],
      "contradicting_evidence": [],
      "created_at_iteration": 2,
      "last_updated_iteration": 5
    }
  ],

  "knowledge_graph_summary": {
    "total_nodes": 24,
    "total_edges": 31,
    "confirmed_facts": 12,
    "uncertain_claims": 8,
    "contradictions": 1
  },

  "search_history": {
    "total_searches": 23,
    "successful": 20,
    "by_source": {
      "web": 15,
      "academic": 8
    }
  },

  "reasoning_mode": "tree_of_thoughts",

  "reflexion_insights": [
    "학술 검색 시 'site:arxiv.org' 접두사가 효과적",
    "복잡도 관련 질문은 Big-O 표기법 포함 필요"
  ],

  "next_actions": [
    {
      "type": "search",
      "query": "linear attention transformer O(n) complexity",
      "reason": "Self-attention의 대안 탐색",
      "priority": "high"
    },
    {
      "type": "verify",
      "claim": "Performer는 O(n) 복잡도로 attention 근사",
      "method": "cross_reference",
      "priority": "medium"
    }
  ],

  "metrics": {
    "token_usage_estimate": 45000,
    "context_utilization": 0.72,
    "search_efficiency": 0.87
  }
}
```

---

## 9. Hallucination 방지 시스템

### 9.1 다층 검증 파이프라인

```
┌─────────────────────────────────────────────────────────────────────────┐
│                  HALLUCINATION PREVENTION PIPELINE                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  [Layer 1: Source Grounding]                                             │
│  ├── 모든 주장에 소스 요구                                              │
│  ├── 소스 없는 주장 플래깅                                              │
│  └── "I don't know" 허용 및 권장                                        │
│                              │                                          │
│                              ↓                                          │
│  [Layer 2: Cross-Validation]                                             │
│  ├── 2개 이상 독립 소스에서 확인                                        │
│  ├── 소스 간 모순 탐지                                                  │
│  └── 신뢰도 점수 기반 가중치                                            │
│                              │                                          │
│                              ↓                                          │
│  [Layer 3: Self-Consistency Check]                                       │
│  ├── 동일 질문에 다중 추론 경로                                         │
│  ├── 불일치 시 추가 검증                                                │
│  └── 일관성 점수 임계값 설정                                            │
│                              │                                          │
│                              ↓                                          │
│  [Layer 4: Uncertainty Quantification]                                   │
│  ├── 각 주장에 확신도 태그                                              │
│  ├── "likely", "uncertain", "speculative" 구분                          │
│  └── 사용자에게 불확실성 투명하게 전달                                   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 9.2 신뢰도 태깅 시스템

```markdown
## 출력 예시

### 확인된 사실 (Verified)
Self-attention 메커니즘은 Query, Key, Value 행렬을 사용하여 입력 시퀀스의
각 위치가 다른 모든 위치에 주의를 기울일 수 있게 합니다. [Vaswani et al. 2017] ✓✓

### 높은 확신 (High Confidence)
이 설계는 RNN의 순차적 처리와 달리 병렬 처리가 가능하여 학습 속도가
크게 향상됩니다. [Vaswani et al. 2017, Devlin et al. 2018] ✓

### 추정 (Likely)
최근 연구들은 O(n) 복잡도의 linear attention이 특정 태스크에서
유사한 성능을 달성할 수 있음을 시사합니다. [Katharopoulos et al. 2020] ~

### 불확실 (Uncertain)
Flash Attention이 모든 하드웨어에서 동일한 속도 향상을 제공하는지는
추가 검증이 필요합니다. [?]
```

---

## 10. 파일 구조 v2

```
~/.claude/skills/research/
├── research.skill.md              # 메인 스킬 정의
├── research.sh                    # 실행 스크립트
├── reasoning/
│   ├── chain_of_thought.md        # CoT 프롬프트
│   ├── tree_of_thoughts.md        # ToT 프롬프트
│   └── self_consistency.md        # Self-Consistency 프롬프트
└── templates/
    ├── state_template.json        # 상태 파일 템플릿
    └── report_template.md         # 보고서 템플릿

프로젝트 디렉토리/
├── .research/
│   ├── state.json                 # 현재 리서치 상태
│   ├── knowledge_graph.json       # 지식 그래프
│   ├── findings.md                # 누적 발견사항
│   ├── hypotheses.md              # 가설 히스토리
│   ├── sources.md                 # 참고 자료
│   ├── reflexion.json             # Reflexion 메모리
│   ├── papers/                    # 다운로드된 논문
│   │   ├── 1706.03762.pdf
│   │   └── ...
│   ├── paper_index.json           # 논문 메타데이터
│   └── iteration_logs/
│       ├── 001.md
│       └── ...
├── RESEARCH_REPORT.md             # 최종 보고서
└── config.json                    # 설정 파일
```

---

## 11. config.json v2

```json
{
  "version": "2.0",

  "search": {
    "engine": "hybrid",
    "parallel_count": 5,
    "max_retries": 3,

    "web": {
      "enabled": true,
      "provider": "claude",
      "fetch_full_content": true
    },

    "academic": {
      "enabled": true,
      "sources": ["arxiv", "semantic_scholar"],
      "auto_download_pdf": true,
      "max_papers_per_query": 3
    },

    "exa": {
      "enabled": false,
      "api_key_env": "EXA_API_KEY"
    }
  },

  "reasoning": {
    "default_mode": "adaptive",
    "modes": {
      "simple": "chain_of_thought",
      "medium": "self_consistency",
      "complex": "tree_of_thoughts",
      "exploratory": "lats"
    },
    "self_consistency_paths": 5,
    "tot_branching_factor": 3,
    "tot_max_depth": 4
  },

  "memory": {
    "compaction_threshold": 0.8,
    "compaction_interval": 5,
    "max_working_memory_items": 20,
    "knowledge_graph_enabled": true
  },

  "verification": {
    "require_sources": true,
    "min_source_count": 2,
    "cross_validation": true,
    "hallucination_check": true
  },

  "iteration": {
    "max_iterations": 100,
    "auto_stop": false,
    "report_interval": 5
  },

  "output": {
    "verbosity": "normal",
    "show_confidence": true,
    "inline_citations": true
  }
}
```

---

## 12. 벤치마크 및 평가

### 12.1 핵심 평가 지표

| 지표 | 설명 | 목표 |
|------|------|------|
| **KPR (Key Point Recall)** | 핵심 포인트 중 얼마나 발견했는가 | > 80% |
| **KPC (Key Point Coverage)** | 발견한 포인트가 얼마나 정확한가 | > 90% |
| **Citation Accuracy** | 인용의 정확성 | > 95% |
| **Factual Consistency** | 사실적 일관성 | > 90% |
| **Search Efficiency** | 검색 대비 유용 정보 비율 | > 70% |
| **Hypothesis Quality** | 가설의 검증 가능성 및 구체성 | 정성적 |

### 12.2 자체 평가 프로세스

```markdown
## 매 5회 반복마다 자체 평가

1. **진행도 평가**
   - 원본 질문의 몇 %가 답변되었는가?
   - 남은 지식 갭은 무엇인가?

2. **가설 품질 평가**
   - 현재 가설들의 평균 확신도
   - 검증된 가설 vs 미검증 가설 비율

3. **검색 효율성 평가**
   - 성공적 검색 / 전체 검색 비율
   - 중복 검색 비율

4. **사실성 평가**
   - 소스 기반 주장 비율
   - 교차 검증된 주장 비율

5. **다음 단계 권장**
   - 탐색 방향 조정 필요 여부
   - 추론 모드 변경 권장 여부
```

---

## 13. 구현 로드맵 v2

### Phase 1: Core Infrastructure (1주)
- [ ] state.json v2 구조 구현
- [ ] 기본 반복 흐름 구현
- [ ] WebSearch + WebFetch 통합
- [ ] 기본 Compaction 구현

### Phase 2: Reasoning Engines (1주)
- [ ] Chain-of-Thought 프롬프트
- [ ] Self-Consistency 구현
- [ ] Tree of Thoughts 기본 구현
- [ ] Reflexion 메모리 시스템

### Phase 3: Search & Verification (1주)
- [ ] Hybrid 검색 아키텍처
- [ ] Academic 검색 통합 (arXiv, Semantic Scholar)
- [ ] 신뢰도 평가 시스템
- [ ] Hallucination 방지 파이프라인

### Phase 4: Knowledge Management (1주)
- [ ] Knowledge Graph 구현
- [ ] 가설 관리 시스템
- [ ] 보고서 생성 시스템
- [ ] 인용 관리

### Phase 5: Polish & Optimization (1주)
- [ ] 사용자 인터페이스 개선
- [ ] 성능 최적화
- [ ] 에러 핸들링
- [ ] 문서화

---

## 14. 참고 문헌

### 핵심 논문
1. Zhang et al. (2025). "Deep Research: A Survey of Autonomous Research Agents" [arXiv:2508.12752]
2. Huang et al. (2025). "Deep Research Agents: A Systematic Examination And Roadmap" [arXiv:2506.18096]
3. Shinn et al. (2023). "Reflexion: Language Agents with Verbal Reinforcement Learning"
4. Yao et al. (2023). "Tree of Thoughts: Deliberate Problem Solving with LLMs"
5. Zhou et al. (2023). "Language Agent Tree Search Unifies Reasoning Acting and Planning"
6. Wang et al. (2023). "Self-Consistency Improves Chain of Thought Reasoning"

### 프레임워크 및 도구
- Anthropic Context Engineering Guide
- LangGraph Reflexion/LATS Implementation
- Graphiti: Real-Time Knowledge Graphs
- Mem0: Memory Layer for LLMs

### 벤치마크
- DeepResearch Bench
- DeepResearchGym
- BrowseComp
- GAIA

---

*이 문서는 리서치 스킬의 기술적 설계를 담고 있으며, 실제 구현 시 상황에 맞게 조정될 수 있습니다.*
