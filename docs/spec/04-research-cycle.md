# 연구 사이클 (9단계) + Memory Blocks

**문서:** 04-research-cycle.md
**최종 수정일:** 2026-02-01 (v5 - Memory Blocks Enhanced)
**수정자:** Claude Sonnet 4.5
**관련 파일:** `.claude/skills/deep-research/SKILL.md`, `config.json:16-36`, `.research/memory_manager.py`

---

## 목차
- [사이클 개요](#사이클-개요)
- [각 단계 상세](#각-단계-상세)
- [병렬 처리 전략](#병렬-처리-전략)
- [사고 도구](#사고-도구)
- [Loop Drift 방지](#loop-drift-방지)

---

## 사이클 개요

### 9단계 흐름

```
┌─────────────────────────────────────────────────────────┐
│  1. LOAD      - 상태 파일 읽기                           │
│       ↓                                                  │
│  2. REFLECT   - Extended Thinking으로 깊이 분석         │
│       ↓                                                  │
│  3. PLAN      - 2-Phase 전략 (10+ 후보 → 3-5개 선택)    │
│       ↓                                                  │
│  4. EXECUTE   - 병렬 검색 실행 (WebSearch/Fetch)         │
│       ↓                                                  │
│  5. VERIFY    - 4계층 검증 시스템 적용                   │
│       ↓                                                  │
│  6. SYNTHESIZE - 지식 그래프 업데이트, 가설 평가         │
│       ↓                                                  │
│  7. SAVE      - 모든 상태 파일 저장                      │
│       ↓                                                  │
│  8. OUTPUT    - 진행 상황 출력                           │
│       ↓                                                  │
│  9. LOOP      - 종료 조건 체크 → Skill 재호출            │
│       │                                                  │
│       └─────────────────────────────────────────────────┘
```

---

### 단계별 소요 시간 (예상)

| 단계 | 소요 시간 | 주요 작업 |
|------|----------|----------|
| 1. LOAD | 5초 | 파일 읽기 (4개) |
| 2. REFLECT | 30초 | Extended Thinking |
| 3. PLAN | 10초 | 쿼리 생성 |
| 4. EXECUTE | 60초 | 병렬 검색 (3-5개) |
| 5. VERIFY | 20초 | 교차 검증 |
| 6. SYNTHESIZE | 30초 | 지식 그래프 업데이트 |
| 7. SAVE | 10초 | 파일 쓰기 (6개) |
| 8. OUTPUT | 5초 | 출력 생성 |
| 9. LOOP | 5초 | 종료 조건 체크 |
| **총** | **2-3분** | **1 iteration** |

---

## 각 단계 상세

### 0. 프롬프트 초기 실행 (SKILL.md 시작 시)

**목적:** 사이클 시작 전 현재 상태 파일을 프롬프트에 자동 로드

**파일:** `.claude/skills/deep-research/SKILL.md:12-18`

**실행 명령어:**

```markdown
## 현재 상태 로드

현재 연구 상태를 확인합니다:
!`cat .research/state.json 2>/dev/null || echo '{"iteration":{"current":0}}'`

최근 검색 히스토리:
!`cat .research/search_history.json 2>/dev/null || echo '{"queries":[]}'`
```

**동작:**
- Skill 프롬프트가 실행될 때 자동으로 bash 명령어 실행
- `!` prefix로 인해 즉시 실행되어 결과가 프롬프트에 포함됨
- 파일이 없으면 기본 JSON 반환 (초기화)

**효과:**
- Agent가 사이클 시작 전에 현재 상태를 즉시 파악
- LOAD 단계에서 별도로 읽을 필요 없음 (이미 프롬프트에 포함됨)

---

### 1. LOAD - 상태 로드 (Memory Blocks Architecture)

**목적:** 3-tier Memory 구조로 효율적 컨텍스트 복원

**파일:** `.claude/skills/deep-research/SKILL.md`, `.research/memory_manager.py`

**3-Tier Memory 로드:**

```python
from memory_manager import MemoryManager

mm = MemoryManager()

# Working Memory (HOT - 최근 10 iterations만)
working = mm.get_working_memory()
recent_iterations = working["iterations"]  # Observation masking 적용

# Semantic Memory (STRUCTURED - 핵심 발견만)
truncated_findings = mm.truncate_findings_for_context(max_findings=30)

# Archival Memory (COLD - 필요 시만 접근)
# old_iter = mm.retrieve_from_archival(iteration=5)
```

**필수 읽기 파일:**

| Memory Tier | 파일 | 용도 | 크기 제한 |
|-------------|------|------|----------|
| **Working** | `working_memory.json` | 최근 10 iterations | 10개 고정 |
| **Semantic** | `findings.md` | 핵심 발견 (truncated) | 30개 최신 |
| **Archival** | `archival/iteration_NNN.json` | 전체 로그 (필요 시) | 무제한 |
| - | `state.json` | 전체 상태, 가설 | - |
| - | `search_history.json` | 검색 중복 방지 | - |

**Observation Masking 효과:**
- 컨텍스트 크기: 67% 감소 (JetBrains Research)
- Cost saving + problem-solving ability 유지
- 오래된 데이터는 archival에 자동 저장

**첫 실행 시 처리:**

```
1. 질문 분해 (Query Decomposition)
   - 복잡한 질문 → 3-5개 서브질문으로 분해
   - 각 서브질문에 우선순위 부여

2. state.json 초기화
   {
     "status": "running",
     "question": {
       "original": "사용자 질문",
       "sub_questions": ["질문1", "질문2", ...]
     },
     "iteration": {"current": 0, "max": 100},
     "active_hypotheses": [],
     "all_hypotheses": []
   }
```

---

### 2. REFLECT - 분석 (Extended Thinking)

**목적:** 현재 상황을 깊이 분석하여 다음 행동 결정

**파일:** `.claude/skills/deep-research/SKILL.md:44-53`

**분석 항목:**

```markdown
## 현재 알고 있는 것
- [지금까지 발견한 사실들 나열]

## 아직 모르는 것
- [미해결 질문들]

## 현재 가설
- 가설 1: [내용] (확신도: 75%)
  - 지지 증거: [증거들]
  - 반증 증거: [증거들]

## 막힌 부분
- 문제: [설명]
- 원인: [분석]
- 해결 방안: [대안들]

## 필요한 사고 도구
- [제1원칙 / 오컴의 면도날 / 반증 가능성 중 선택]
```

**Extended Thinking 활용:**

- 모든 분석은 `<thinking>` 블록 내에서 수행
- 최소 10단계 이상의 추론 과정
- 가정 명시, 대안 고려

---

### 3. PLAN - 계획 (2-Phase 전략)

**목적:** 이번 iteration의 구체적인 검색 전략 수립

**파일:** `.claude/skills/deep-research/SKILL.md:54-173`

**설정:** `config.json:16-36`

**구조:** 발산(Divergent) → 수렴(Convergent) → 중복제거(Deduplication)

#### Phase 0: Active Hypotheses 확인

현재 집중할 상위 5개 가설 확인:

```python
active_hypothesis_ids = state.get("active_hypotheses", [])
all_hypotheses = state.get("all_hypotheses", [])

if all_hypotheses and active_hypothesis_ids:
    active_hypotheses = [h for h in all_hypotheses if h["id"] in active_hypothesis_ids]
    print(f"🎯 Current Focus: {len(active_hypotheses)} active hypotheses")
    for h in active_hypotheses[:3]:
        print(f"  - [{h['id']}] {h['statement'][:50]}... (Priority: {h['priority_score']:.2f})")
else:
    print("🎯 첫 iteration: 전체 탐색 모드")
```

**안전성 처리:**
- 첫 iteration: `all_hypotheses` 없음 → 전체 탐색 모드
- 이후 iteration: active_hypotheses 기반 집중 탐색

#### Phase 1: Divergent Thinking (발산)

**목표:** 10개 이상 쿼리 후보 생성

**규칙:**
- 판단 보류 (no premature filtering)
- 브레인스토밍 모드
- 다양성 우선

**생성 전략:**

```markdown
## 일반 웹 검색 (3-4개)
- "keyword A B C 2026"
- "keyword D E F latest"

## 학술/기술 검색 (3-4개)
- "site:arxiv.org [topic]"
- "site:github.com [implementation]"

## 반증 증거 탐색 (3-4개)
- "[hypothesis] criticism"
- "[hypothesis] counterexample"
- "[hypothesis] limitations fails when"

결과: candidate_queries = [q1, ..., q10+]
```

#### Phase 2: Convergent Thinking (수렴)

**목표:** 상위 3-5개 최적 쿼리 선택

**평가 기준:**

| 기준 | 설명 | 가중치 |
|------|------|--------|
| 정보 가치 | 새로운 발견 가능성 | 40% |
| 다양성 | 다른 각도/소스 | 30% |
| 실행 가능성 | 구체적이고 검색 가능 | 20% |
| 중복도 | 내부 중복 제거 | 10% |

**선택 프로세스:**

각 후보를 평가하여 상위 3-5개 선택

```
결과: filtered_queries_phase2 = [top_3_to_5]
```

#### Phase 3: 중복 검색 제거 (Deduplication)

과거 검색과의 중복 제거 (>0.95 유사도):

```python
from deduplicate_search import is_duplicate_query

for query in filtered_queries_phase2:
    if not is_duplicate_query(query):
        final_queries.append(query)
```

**최종 결과:** `final_queries` = 3-5개 실행 쿼리

**전략 선택 기준:**

| 상황 | 전략 | 이유 |
|------|------|------|
| 최신 동향 필요 | Web | 일반 검색엔진이 최신 정보 보유 |
| 학술적 근거 필요 | Academic | arXiv, IEEE 등 신뢰도 높음 |
| 확신도 > 80% | Verification | 반증 증거 적극 탐색 필요 |
| 모순 발견 | Verification | 교차 검증 |

---

### 4. EXECUTE - 실행

**목적:** 계획된 검색을 **병렬로** 실행하여 시간 단축

**파일:** `.claude/skills/deep-research/SKILL.md:174-207`

**병렬 검색 예시:**

```python
# final_queries (PLAN Phase 3에서 중복 제거된 쿼리)로 검색 실행
WebSearch("final_query_1")  # 병렬
WebSearch("final_query_2")  # 병렬
WebSearch("final_query_3")  # 병렬

# 검색 실행 후 history에 추가 (embedding 자동 저장)
for query, result in zip(final_queries, search_results):
    add_query_to_history(
        query_text=query,
        iteration=current_iteration,
        results_count=len(result.get('items', [])),
        success=True
    )
```

**실행 시간:**
- 순차 실행: 30초 × 3 = 90초
- 병렬 실행: max(30초, 30초, 30초) = 30초
- **절감: 60초 (67%)**

**WebFetch 활용:**

```
검색 결과에서 유망한 URL 발견 시:
→ WebFetch("https://...", "Extract key findings")  ← 병렬
→ WebFetch("https://...", "Extract methodology")   ← 병렬
→ WebFetch("https://...", "Extract limitations")   ← 병렬
```

**학술 논문 처리:**

```bash
# 1. arXiv 검색
WebSearch("site:arxiv.org transformer architecture")

# 2. PDF URL 추출
https://arxiv.org/pdf/2103.xxxxx.pdf

# 3. 다운로드
Bash("curl -L -o .research/papers/transformer.pdf https://arxiv.org/pdf/2103.xxxxx.pdf")

# 4. 분석
Read(".research/papers/transformer.pdf")
```

**설정:** `config.json:16-36`

```json
"search": {
  "parallel_count": 3,
  "max_retries": 2,
  "strategies": {
    "web": {"enabled": true, "fetch_full_content": true},
    "academic": {
      "enabled": true,
      "sources": ["arxiv", "semantic_scholar"],
      "auto_download_pdf": true,
      "max_papers_per_query": 3
    },
    "verification": {
      "enabled": true,
      "search_contradictions": true
    }
  }
}
```

---

### 5. VERIFY - 검증

**목적:** Hallucination 방지, 모든 주장에 근거 확보

**파일:** `.claude/skills/deep-research/SKILL.md:208-231`

**상세:** [05-verification.md](./05-verification.md) 참조

**4계층 검증:**

```
Layer 1: Source Grounding
         ↓
Layer 2: Cross-Validation (2-3개 소스 교차 확인)
         ↓
Layer 3: Self-Consistency (다른 각도에서 재검토)
         ↓
Layer 4: Confidence Tagging (✓✓ / ✓ / ~ / ? / ⚠)
```

**예시:**

```markdown
## 발견 사항

✓✓ GPT-4는 2023년 3월 14일 출시되었다
   소스: openai.com, techcrunch.com, theverge.com
   신뢰도: 0.95

✓ Transformer 아키텍처는 2017년 "Attention Is All You Need" 논문에서 제안되었다
   소스: arxiv.org/abs/1706.03762
   신뢰도: 0.98

~ 양자 컴퓨터는 2030년까지 실용화될 것으로 예상된다
   소스: forbes.com (전문가 예측)
   신뢰도: 0.60

? GPT-5의 출시 시기는 불명확하다
   소스: 없음 (공식 발표 없음)
   신뢰도: 0.30

⚠ "GPT-4는 AGI를 달성했다"는 주장은 논란이 있다
   지지: wired.com (일부 전문가)
   반대: nature.com (대다수 전문가)
   신뢰도: 모순
```

---

### 6. SYNTHESIZE - 종합

**목적:** 새로운 정보를 기존 지식과 통합, 가설 평가 및 우선순위 관리

**파일:** `.claude/skills/deep-research/SKILL.md:232-330`

**작업 흐름:**

```
1. Knowledge Graph 업데이트
         ↓
2. 가설 평가 및 Priority-based Filtering
         ↓
3. Active Hypotheses 선택 (Top 5)
         ↓
4. Reflexion 메모리 업데이트
```

**1. Knowledge Graph 업데이트**

**파일:** `.research/knowledge_graph.json`

```json
{
  "nodes": [
    {
      "id": "gpt4_001",
      "label": "GPT-4",
      "type": "model",
      "confidence": 0.98,
      "added_iteration": 1
    },
    {
      "id": "transformer_001",
      "label": "Transformer Architecture",
      "type": "architecture",
      "confidence": 0.98,
      "added_iteration": 2
    }
  ],
  "edges": [
    {
      "from": "gpt4_001",
      "to": "transformer_001",
      "relation": "based_on",
      "confidence": 0.95,
      "sources": ["openai.com", "arxiv.org/..."],
      "added_iteration": 2
    }
  ]
}
```

**업데이트 규칙:**
- 새로운 개념 → 노드 추가
- 개념 간 관계 → 엣지 추가
- 모순 발견 → 플래그 추가 (`"contradicted": true`)

**2. 가설 평가 및 Priority-based Filtering**

**목표:** 상위 5개 가설에 집중하여 Cognitive Load 감소

**프로세스:**

```python
for hypothesis in hypotheses:
    # 2.1 지지/반증 증거 연결
    for finding in new_findings:
        if finding.get("hypothesis_id") == hypothesis["id"]:
            if finding["confidence"] >= 0.7:
                hypothesis["supporting_evidence"].append(...)
            else:
                hypothesis["contradicting_evidence"].append(...)

    # 2.2 확신도 재계산 (베이지안 업데이트)
    support_weight = len(supporting_evidence) * 0.1
    contra_weight = len(contradicting_evidence) * 0.15
    hypothesis["confidence"] = max(0.0, min(1.0,
        current_confidence + support_weight - contra_weight
    ))

    # 2.3 Priority Score 계산
    # 공식: Confidence(50%) + Evidence Density(30%) + Recency(20%)
    evidence_density = (support - contra*0.5) / 10  # 0~1
    recency = 1.0 if last_updated >= iter-2 else 0.5
    hypothesis["priority_score"] = (
        confidence * 0.5 +
        evidence_density * 0.3 +
        recency * 0.2
    )

# 3. Active Hypotheses 필터링 (Top 5)
hypotheses.sort(key=lambda h: h["priority_score"], reverse=True)
active_hypotheses = hypotheses[:5]
inactive_hypotheses = hypotheses[5:]

state["active_hypotheses"] = [h["id"] for h in active_hypotheses]
state["all_hypotheses"] = hypotheses
```

**스키마 예시:**

```json
{
  "id": "hyp_001",
  "statement": "양자 컴퓨터는 암호화 알고리즘을 위협할 것이다",
  "confidence": 0.85,
  "priority_score": 0.78,
  "supporting_evidence": [
    {"source": "nature.com", "summary": "Shor's algorithm 증명", "confidence": 0.95}
  ],
  "contradicting_evidence": [
    {"source": "arxiv.org", "summary": "실용화까지 10년 이상 소요", "confidence": 0.80}
  ],
  "last_updated_iteration": 5
}
```

**확신도 업데이트 규칙:**

- 지지 증거 1개 추가: +10%
- 반증 증거 1개 추가: -15%
- 범위: 0.0 ~ 1.0

**3. Reflexion 메모리**

**파일:** `.research/reflexion.json`

```json
{
  "iterations": [
    {
      "iteration": 2,
      "action": "WebSearch(\"quantum computing applications\")",
      "outcome": "success",
      "lesson": "일반 검색보다 학술 검색이 더 정확한 정보 제공",
      "adjustment": "다음부터 기술 주제는 arxiv 우선 검색"
    },
    {
      "iteration": 3,
      "action": "WebSearch(\"GPT-4 release date\")",
      "outcome": "failure",
      "reason": "이미 검색한 쿼리 반복",
      "lesson": "search_history.json 확인 필수",
      "adjustment": "검색 전 히스토리 체크 추가"
    }
  ]
}
```

---

### 7. SAVE - 저장 (Memory Blocks 자동 관리)

**목적:** 3-tier Memory 구조로 효율적 저장 및 자동 archival

**파일:** `.claude/skills/deep-research/SKILL.md`, `.research/memory_manager.py`

**3-Tier Memory 자동 업데이트:**

```python
from memory_manager import MemoryManager

mm = MemoryManager()

# Working Memory (HOT - 자동 observation masking)
mm.update_working_memory(
    iteration=current_iteration,
    findings=new_findings,
    queries_executed=final_queries,
    active_hypotheses=state["active_hypotheses"],
    next_actions=state["next_actions"]
)
# 동작:
# - working_memory.json에 추가
# - 10개 초과 시 오래된 것은 archival로 자동 이동
# - 최근 10개만 유지

# Semantic Memory (STRUCTURED)
mm.update_semantic_memory(findings_md_content)

# Archival Memory (COLD - 자동 저장)
# 11번째 이전 iterations는 .research/archival/iteration_NNN.json에 자동 저장
```

**저장 파일 목록:**

| Memory Tier | 파일 | 업데이트 내용 | 크기 제한 | 필수 여부 |
|-------------|------|--------------|----------|----------|
| **Working** | `working_memory.json` | 최근 10 iterations | 10개 고정 | ✅ 필수 |
| **Semantic** | `findings.md` | 핵심 발견 사항 | 30개 추천 | ✅ 필수 |
| **Archival** | `archival/iteration_NNN.json` | 전체 iteration 로그 | 무제한 | ✅ 자동 |
| - | `state.json` | iteration +1, active_hypotheses, metrics | - | ✅ 필수 |
| - | `search_history.json` | 실행된 쿼리 (자동) | - | ✅ 필수 |
| - | `knowledge_graph.json` | 노드/엣지 업데이트 | - | ⚠️ 활성화 시 |
| - | `reflexion.json` | 실패 학습 기록 | - | ⚠️ 활성화 시 |

**Observation Masking 효과:**
- 컨텍스트 크기: 67% 감소
- Cost saving + problem-solving ability 유지
- 과거 데이터는 archival에서 언제든 복원 가능

**state.json 업데이트 예시:**

```json
{
  "status": "running",
  "iteration": {
    "current": 3,
    "max": 100
  },
  "active_hypotheses": ["hyp_001", "hyp_003", "hyp_002", "hyp_005", "hyp_007"],
  "all_hypotheses": [
    {
      "id": "hyp_001",
      "confidence": 0.85,
      "priority_score": 0.78,
      "last_updated_iteration": 3
    }
  ],
  "next_actions": [
    "학술 논문에서 반증 증거 탐색",
    "실험 결과 교차 검증"
  ],
  "metrics": {
    "cost_estimate_usd": 0.45,
    "queries_executed": 9,
    "sources_found": 27,
    "verified_facts": 12
  }
}
```

**findings.md 형식:**

```markdown
# Research Findings

## Iteration 3 (2026-01-31 14:32)

### 핵심 발견
- ✓✓ GPT-4는 Transformer 아키텍처 기반 (openai.com, arxiv.org)
- ✓ 175B 파라미터 사용 (techcrunch.com)
- ~ 학습 비용 약 $100M 추정 (forbes.com)

### 가설 업데이트
- hyp_001: 확신도 75% → 85% (지지 증거 2개 추가)

### 다음 계획
- 반증 증거 탐색: "GPT-4 limitations"
```

---

### 8. OUTPUT - 출력

**목적:** 사용자에게 진행 상황을 명확하게 전달

**파일:** `.claude/skills/deep-research/SKILL.md:354-383`

**출력 형식:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Iteration #3 완료
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 이번 발견:
   - ✓✓ GPT-4는 Transformer 기반 (openai.com, arxiv.org)
   - ✓ 175B 파라미터 사용 (techcrunch.com)
   - ~ 학습 비용 약 $100M 추정 (forbes.com)

🎯 Active Hypotheses (Top 5):
   1. [hyp_001] GPT-4는 대규모 언어 모델이다
      확신도: 85% | Priority: 0.78 | 지지: 2개 | 반증: 0개
   2. [hyp_003] Transformer는 다양한 태스크에 적용 가능
      확신도: 80% | Priority: 0.72 | 지지: 3개 | 반증: 1개
   ...

📋 Inactive: 3개 가설 (우선순위 낮음, 재평가 대기)

📈 다음 계획: active_hypotheses 기반 탐색 전략

📊 진행도: 60% (3/5 서브질문 답변됨)
   예산: $0.45 / $10.00
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**설정:** `config.json:81-86`

```json
"output": {
  "verbosity": "normal",
  "show_confidence": true,
  "inline_citations": true,
  "progress_dashboard": true
}
```

---

### 9. LOOP - 다음 Iteration 자동 시작

**목적:** Ralph Loop 패턴 구현, 무한 반복 강제

**파일:** `.claude/skills/deep-research/SKILL.md:402-461`

**상세:** [03-ralph-loop.md](./03-ralph-loop.md) 참조

**종료 조건 체크:**

```python
# state.json 읽기
status = state["status"]
current = state["iteration"]["current"]
max_iter = state["iteration"]["max"]
budget = state["metrics"]["cost_estimate_usd"]

# 종료 조건 (OR)
should_stop = (
    status in ["completed", "paused", "stopped_by_user", "budget_exceeded"]
    or current >= max_iter
    or budget > 10.0
)

if should_stop:
    # 종료
    print("연구 종료")
else:
    # 계속
    print("다음 iteration을 시작합니다...")
    Skill("deep-research", "")
```

**중요 규칙:**

- ❌ **절대 금지:** "연구를 종료합니다", "충분합니다", "완료되었습니다"
- ✅ **필수:** 종료 조건 불만족 시 `Skill("deep-research", "")` 호출

---

## 병렬 처리 전략

### 병렬 검색 최적화

**문제:**
```
순차 실행:
WebSearch("query 1")  → 30초
  (대기)
WebSearch("query 2")  → 30초
  (대기)
WebSearch("query 3")  → 30초
─────────────────────────────
총 90초
```

**해결:**
```
병렬 실행 (단일 메시지):
WebSearch("query 1")  ┐
WebSearch("query 2")  ├─→ 동시 실행 → 30초
WebSearch("query 3")  ┘
─────────────────────────────
총 30초 (67% 절감)
```

**구현:**

```markdown
단일 응답에 여러 도구 호출:

WebSearch("quantum computing applications")
WebSearch("quantum computing limitations")
WebSearch("site:arxiv.org quantum supremacy")
```

---

### WebFetch 병렬화

**시나리오:**

```
검색 결과:
- URL 1: nature.com/article/...
- URL 2: arxiv.org/abs/...
- URL 3: ieee.org/document/...
```

**병렬 추출:**

```markdown
WebFetch("https://nature.com/article/...", "Extract key findings")
WebFetch("https://arxiv.org/abs/...", "Extract methodology")
WebFetch("https://ieee.org/document/...", "Extract experiments")
```

**시간 절감:**
- 순차: 20초 × 3 = 60초
- 병렬: max(20초) = 20초
- **절감: 40초 (67%)**

---

## 사고 도구

**파일:** `.claude/skills/deep-research/SKILL.md:384-392`

### 도구 선택 기준

| 상황 | 도구 | 적용 방식 |
|------|------|-----------|
| **막힐 때** | 제1원칙 | 기존 가정을 모두 버리고 근본 원리부터 재구성 |
| **정보 과다** | 오컴의 면도날 | 복잡한 설명보다 단순한 설명 우선 채택 |
| **확신이 생길 때** | 반증 가능성 | 가설을 반박할 증거를 적극 탐색 |
| **새 방향 필요** | 과학적 방법론 | 관찰→가설→실험→분석 사이클 적용 |

### 제1원칙 (First Principles)

**적용 시점:**
- 5회 연속 진전 없음
- 모든 검색이 같은 결과 반복
- 현재 접근법이 막다른 길

**방법:**
```markdown
1. 현재 가정 나열
   - 가정 1: [설명]
   - 가정 2: [설명]

2. 각 가정을 근본 원리로 분해
   - 가정 1 = 원리 A + 원리 B

3. 원리부터 재구성
   - 원리 A를 다르게 조합하면?
   - 원리 B를 생략하면?

4. 새로운 접근법 도출
```

### 오컴의 면도날 (Occam's Razor)

**적용 시점:**
- 여러 설명이 경쟁할 때
- 정보 과부하 상태
- 핵심 요약 필요

**방법:**
```markdown
설명 1: [복잡한 설명]
설명 2: [단순한 설명]

→ 설명 2 채택 (단순함 우선)
```

### 반증 가능성 (Falsifiability)

**적용 시점:**
- 가설 확신도 > 80%
- 지지 증거만 계속 발견
- 편향 가능성 있을 때

**방법:**
```markdown
가설: [주장]
확신도: 85%

반증 검색:
- "[가설] criticism"
- "[가설] counterexample"
- "[가설] limitations"
- "[가설] controversy"
```

---

## Loop Drift 방지

**파일:** `.claude/skills/deep-research/SKILL.md:393-401`

**상세:** [06-loop-drift.md](./06-loop-drift.md) 참조

### 탐지 규칙

**설정:** `config.json:9-13`

```json
"loop_drift_prevention": {
  "same_query_threshold": 2,
  "same_action_threshold": 3,
  "no_progress_iterations": 5
}
```

| 패턴 | 임계값 | 조치 |
|------|--------|------|
| 같은 검색 쿼리 반복 | 2회 | 쿼리 변형 필수 |
| 같은 행동 패턴 반복 | 3회 | 전략 변경 필수 |
| 새 정보 없음 | 5회 | 다른 접근법 시도 |

### 방지 메커니즘

**1. search_history.json 확인**

```json
{
  "queries": [
    {
      "iteration": 1,
      "query": "quantum computing applications",
      "result_count": 10
    },
    {
      "iteration": 2,
      "query": "quantum computing applications",
      "result_count": 10
    }
  ]
}
```

→ 2회 반복 탐지 → 쿼리 변형 필수

**2. Reflexion 메모리 참조**

```json
{
  "iterations": [
    {
      "iteration": 3,
      "action": "WebSearch(\"same query\")",
      "outcome": "failure",
      "lesson": "같은 검색은 새 정보 없음",
      "adjustment": "학술 검색으로 전환"
    }
  ]
}
```

→ 과거 실패 학습 → 대안 선택

**3. 전략 변경**

```markdown
현재 전략: Web Search (일반)
결과: 3회 연속 새 정보 없음

→ 전략 변경:
  1. Academic Search (arxiv)
  2. Verification (반증 증거)
  3. 다른 키워드 조합
```

---

## 성능 지표

### Iteration당 처리량

| 지표 | 목표 | 실제 (평균) |
|------|------|------------|
| 검색 쿼리 수 | 3-5개 | 4개 |
| 발견 소스 수 | 10-15개 | 12개 |
| 검증된 사실 수 | 3-5개 | 4개 |
| 소요 시간 | 2-3분 | 2.5분 |
| 비용 | $0.03-0.05 | $0.04 |

### 100 Iterations 누적

| 지표 | 예상 |
|------|------|
| 총 검색 쿼리 | 400개 |
| 총 발견 소스 | 1,200개 |
| 검증된 사실 | 400개 |
| 총 소요 시간 | 4-5시간 |
| 총 비용 | $3-5 |

---

**다음:** [05-verification.md](./05-verification.md) - 4계층 검증 시스템 상세
