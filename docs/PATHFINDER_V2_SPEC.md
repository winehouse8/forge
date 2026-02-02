# Pathfinder v2 구현 기획서

> 관찰-가설-정설 프레임워크 기반 자율 연구 에이전트

---

## 1. 개요

### 1.1 목표

```
웹 검색 기반으로 질문에 대한 깊은 연구를 수행하고,
창의적 사고 도구를 활용하여 새로운 통찰을 도출하는 자율 연구 에이전트
```

### 1.2 핵심 철학

- **과학적 방법론**: 관찰(Observation) → 가설(Hypothesis) → 정설(Thesis)
- **이중 트랙 엔진**: 탐험가(Explorer)의 발산 + 사상가(Thinker)의 수렴
- **창의적 사고**: 3 iteration마다 6개 사고 도구로 Type B 가설 생성
- **지속적 검증**: 가설의 신뢰도는 탐색을 통해 계속 갱신
- **Lazy Thesis**: 최종 정설은 사용자 요청 시에만 판정

### 1.3 vs 기존 Pathfinder

| 구분 | v1 (기존) | v2 (신규) |
|------|----------|----------|
| 데이터 | Evidence, Claim | Observation, Hypothesis (A/B), Thesis |
| 사고 | 충돌 해결만 | 6개 사고 도구로 창의적 가설 생성 (3회마다) |
| 저장소 | 파일 + summary.md | CogniGraph (그래프 색인) |
| 탐색 | hole 기반 | 가설 상태(unvisited/tested/verified) 기반 |
| 종료 | iteration 수 | 포화 감지 + 사용자 요청 |

---

## 2. 핵심 개념

### 2.1 데이터 계층 (Scientific Framework)

```
┌─────────────────────────────────────────────────────────┐
│  Layer 1: Thesis (정설)                                 │
│    - 검증이 완료되어 채택된 가설들의 집합               │
│    - 사용자 요청 시에만 생성                            │
│    - = 최종 연구 결론                                   │
├─────────────────────────────────────────────────────────┤
│  Layer 2: Hypothesis (가설)                             │
│    - Type A (Derived): 외부에서 가져온 타인의 주장      │
│    - Type B (Generated): 에이전트가 추론한 통찰         │
│    - 신뢰도(strength)가 계속 갱신됨                     │
├─────────────────────────────────────────────────────────┤
│  Layer 3: Observation (관찰)                            │
│    - 웹에서 수집한 순수 사실/데이터                     │
│    - 통계, 실험 결과, 인용문                            │
│    - 불변 (한번 저장되면 변하지 않음)                   │
└─────────────────────────────────────────────────────────┘
```

### 2.2 이중 트랙 엔진 (Dual-Track Engine)

```
┌─────────────────────────────────────────────────────────┐
│  Track 1: 탐험가 (Explorer) - 발산과 수집               │
│                                                         │
│  역할: 외부 세계(웹)를 탐색하여 정보 수집               │
│  로직: "모르는 것이 있으면 찾는다" (래빗홀 전략)        │
│  산출물: Observation, Type A Hypothesis                 │
│                                                         │
│  검색 모드:                                             │
│    - 광역 검색 (Broad): 발산, 새 영역 탐색              │
│    - 정밀 검색 (Deep): 특정 가설 검증                   │
├─────────────────────────────────────────────────────────┤
│  Track 2: 사상가 (Thinker) - 수렴과 생성                │
│                                                         │
│  역할: 수집된 정보를 연결하여 새로운 통찰 생성          │
│  로직: "아는 것들을 연결해 새로운 의미를 만든다"        │
│  산출물: Type B Hypothesis, 신뢰도 조정                 │
│                                                         │
│  사고 도구: 패턴인식, 유추, 제1원리, 인과체인,          │
│            SCAMPER, 역발상                              │
└─────────────────────────────────────────────────────────┘
```

### 2.3 CogniGraph (인지 그래프)

LiCoMemory의 그래프 기반 메모리 전략을 적용한 "가벼운 의미론적 색인"

```
CogniGraph = 파일들을 연결하는 네비게이션 지도

- 모든 관계가 한 파일(cognigraph.json)에 색인됨
- 충돌, 지지, 관련 관계를 즉시 조회 가능
- 물리적 파일(obs_*.md, hyp_*.md)은 상세 내용만 저장
```

---

## 3. 파일 구조

### 3.1 디렉토리 구조

```
.research/current/
├── cognigraph.json       # 그래프 색인 (관계 + 메타데이터)
├── observations/         # 관찰 상세
│   ├── obs_1.md
│   ├── obs_2.md
│   └── ...
├── hypotheses/           # 가설 상세
│   ├── hyp_1.md
│   ├── hyp_2.md
│   └── ...
└── thesis.md             # 정설 (최종 판정 시 생성)
```

### 3.2 cognigraph.json 스키마

```json
{
  "question": "연구 질문",
  "iteration": 0,

  "observations": {
    "obs_1": {
      "summary": "1~3줄 요약. 핵심 수치/사실 포함. 예: 'GPT-4는 128K 토큰 컨텍스트 지원. 실험에서 64K 이상시 정확도 15% 하락 (Liu et al. 2024)'",
      "authority": 0.9,
      "source_url": "https://...",
      "source_type": "paper|official|blog|forum",
      "created_at": 1
    }
  },

  "hypotheses": {
    "hyp_1": {
      "type": "A|B",
      "summary": "1~3줄 요약. 주장+근거+조건 포함. 예: 'RAG가 fine-tuning보다 효과적 (비용 대비). 단, 실시간 업데이트 필요한 경우에 한함. obs_1,obs_3 기반'",
      "strength": 0.5,
      "status": "unvisited|tested|verified|rejected",
      "visit_count": 0,
      "last_visited": null,
      "created_at": 1,
      "reasoning_tool": null,
      "verify_keywords": ["검증용 검색 키워드"]
    }
  },

  "edges": [
    {
      "from": "obs_1",
      "to": "hyp_1",
      "type": "SUPPORTS|CONTRADICTS|CONFLICTS",
      "weight": 0.8,
      "created_at": 1,
      "resolved": false,        // CONFLICTS용: 해결 여부
      "resolution": null        // CONFLICTS용: "조건 차이: X일 때 A, Y일 때 B"
    }
  ],

  "lens_index": 0,

  "unexplored": [
    {"keyword": "검색 방향 1", "from": "hyp_1", "used": false}
  ],

  "health": {
    "last_check": 0,
    "issues": []
  }
}
```

**핵심 설계 원칙:**
- `cognigraph.json`만 읽으면 IDEATE 판단 가능 (상세 파일 안 봐도 됨)
- summary는 "무엇을 주장하는지 + 왜 그런지 + 조건" 포함
- 상세 파일(obs_*.md, hyp_*.md)은 원문 인용, 히스토리 등 백업용

### 3.3 노드 정의

| 노드 타입 | 정의 | 메타데이터 |
|----------|------|-----------|
| Observation | 순수 사실/데이터 | authority, source_url, source_type |
| Hypothesis | 주장/통찰 | type(A/B), strength, status, visit_count, reasoning_tool, verify_keywords |

### 3.4 엣지 정의 (단순화)

| 엣지 타입 | 의미 | 방향 |
|----------|------|------|
| SUPPORTS | 관찰이 가설을 지지 | Obs → Hyp |
| CONTRADICTS | 관찰이 가설을 반박 | Obs → Hyp |
| CONFLICTS | 가설 간 충돌 (상반된 주장) | Hyp → Hyp (단방향 1개만 저장) |

**엣지 weight (숫자):**
```
0.8 = STRONG: 직접적 증거, 같은 주제, 논리적 필연
0.5 = MEDIUM: 관련 있지만 간접적
0.3 = WEAK:   연관은 있으나 논리적 비약 존재
```

**CONFLICTS 처리:**
- 단방향 1개만 저장 (hyp_1 → hyp_2)
- 조회 시 양방향 모두 체크: `e.from == id OR e.to == id`
- 한쪽이 rejected 되면 해당 CONFLICTS 엣지는 무시 (삭제 안 함)

**삭제된 것들 (복잡도 대비 효과 낮음):**
- ~~INSPIRES~~: Type B의 derived_from은 summary에 텍스트로 기록
- ~~QUALIFIES~~: 조건은 가설 summary에 텍스트로 기록
- ~~Concept 노드~~: 검색 키워드는 unexplored에서 관리

### 3.5 가설 상태 (status) - 단순화

```
unvisited  → 아직 한 번도 탐색 안 됨 (검증 대기)
tested     → 1회 이상 탐색됨 (strength 변동 중)
verified   → 충분히 검증됨:
             - strength >= 0.65 AND
             - visit_count >= 2 AND
             - 강한 반박(weight >= 0.5) 없음 (★ v2.5)
rejected   → 기각됨 (strength < 0.25)
```

**verified의 의미:** "지지가 많다"가 아니라 **"반박을 견뎠다"**

**삭제된 것들:**
- ~~exploring~~: SELECT 시작~UPDATE 완료는 한 iteration 내에서 끝남. 중간 상태 불필요
- ~~archived~~: rejected면 그냥 무시. 복구 로직 없이 복잡도만 증가

### 3.6 Observation 파일 포맷 (obs_{id}.md)

```markdown
# Observation {id}

## Source
- URL: https://...
- Type: paper | official_doc | blog | forum
- Authority: 0.9
- Retrieved: 2024-01-15

## Content
순수 사실/데이터 내용

## Quotes
> 원문 인용 (있으면)

## Extracted Concepts
- 키워드1
- 키워드2
```

### 3.7 Hypothesis 파일 포맷 (hyp_{id}.md)

```markdown
# Hypothesis {id}

## Type
B (generated)

## Statement
가설 내용

## Reasoning Tool
패턴 인식 + 유추

## Derived From
- obs_1, obs_3: 패턴 발견
- hyp_2: 확장

## Strength
0.45

## Status
unvisited

## Visit History
| Iteration | Action | Result | Strength Change |
|-----------|--------|--------|-----------------|
| 5 | EXPLORE | obs_7 SUPPORTS | +0.08 |
| 8 | EXPLORE | obs_12 CONTRADICTS | -0.12 |

## Verification Direction
- "검색 키워드 1"
- "검색 키워드 2"
```

---

## 4. 사이클 설계

### 4.1 오케스트레이터 (메인 루프)

**핵심 원칙:** cognigraph.json이 **단일 진실의 원천**. 모든 상태는 여기에 저장.

```python
def run_iteration(cognigraph_path):
    """한 번의 iteration 실행 - Claude CLI가 이 함수를 호출"""

    # 1. LOAD
    cg = load_json(cognigraph_path)

    # 2. SELECT
    select_input = build_select_input(cg)
    select_output = call_claude("SELECT", select_input)

    # 3. EXPLORE (재시도 포함)
    explore_input = build_explore_input(cg, select_output)
    explore_output = run_explore_with_retry(explore_input)

    # 4. EXPLORE 결과 먼저 반영 (IDEATE가 최신 데이터를 볼 수 있도록)
    if explore_output["status"] != "failure":
        cg = apply_explore_updates(cg, select_output, explore_output)

    # 5. IDEATE (조건부) - 이제 최신 cg 사용
    ideate_output = None
    if cg["iteration"] >= 3 and cg["iteration"] % 3 == 0:
        ideate_input = build_ideate_input(cg)
        ideate_output = call_claude("IDEATE", ideate_input)
        if ideate_output:
            cg = apply_ideate_updates(cg, ideate_output)

    # 6. 상태 전환 및 마무리
    cg = finalize_iteration(cg, select_output, explore_output)

    # 7. CHECK (조건부)
    if cg["iteration"] % 5 == 0:
        issues = health_check(cg)
        cg["health"]["issues"] = issues
        cg["health"]["last_check"] = cg["iteration"]

    # 8. SAVE
    save_json(cognigraph_path, cg)

    return cg["health"].get("issues", [])
```

### 4.2 오케스트레이터 헬퍼 함수

```python
def build_explore_input(cg, select_output):
    """EXPLORE 입력 생성 - ID 계산 포함"""
    return {
        "search_query": select_output["search_query"],
        "search_mode": select_output["search_mode"],
        "target_type": select_output["target_type"],
        "target_id": select_output["target_id"],
        "conflict_with": select_output.get("conflict_with"),  # ★ 충돌 상대방
        "existing_hypotheses": {k: v["summary"] for k, v in cg["hypotheses"].items()
                                if v["status"] != "rejected"},
        "next_obs_id": max_id(cg["observations"], "obs_") + 1,  # ★ ID 계산
        "next_hyp_id": max_id(cg["hypotheses"], "hyp_A") + 1,
        "retry_count": 0
    }


def max_id(collection, prefix):
    """컬렉션에서 prefix로 시작하는 최대 ID 추출"""
    ids = [int(k.replace(prefix, "").replace("A", "").replace("B", ""))
           for k in collection.keys() if k.startswith(prefix)]
    return max(ids) if ids else 0


def build_ideate_input(cg):
    """IDEATE 입력 생성"""
    active_hyps = {k: v for k, v in cg["hypotheses"].items() if v["status"] != "rejected"}
    return {
        "question": cg["question"],
        "health_issues": cg["health"].get("issues", []),
        "observations": {k: v["summary"] for k, v in cg["observations"].items()},
        "hypotheses": {
            hid: f"[{h['type']}|{h['status']}|{h['strength']:.2f}] {h['summary']}"
            for hid, h in active_hyps.items()
        },
        "conflicts": get_active_conflicts(cg),
        "edges": [{"from": e["from"], "to": e["to"], "type": e["type"]} for e in cg["edges"]],
        "next_hyp_id": max_id(cg["hypotheses"], "hyp_B") + 1  # ★ Type B ID
    }
```

### 4.3 인터페이스 계약 (I/O Schema)

**모든 단계는 JSON으로 입출력. 키 이름 통일.**

#### SELECT I/O

```yaml
SELECT_INPUT:
  question: string
  iteration: number
  health_issues: string[]          # CHECK에서 감지된 이슈
  conflicts: [{from, to}]          # 활성 CONFLICTS 쌍
  unvisited_type_b: [hyp_id]
  unvisited_type_a: [hyp_id]
  tested_uncertain: [hyp_id]       # strength 0.35~0.65
  unexplored_unused: [{keyword, from}]
  lens_index: number
  hypotheses_summary: {hyp_id: summary}  # 검색어 생성용

SELECT_OUTPUT:
  target_type: "hypothesis" | "unexplored" | "6lens"
  target_id: string | null         # hypothesis ID or keyword
  conflict_with: string | null     # CONFLICTS 해결 시 상대방 ID
  search_query: string
  search_mode: "broad" | "deep"
  reason: string
```

#### EXPLORE I/O

```yaml
EXPLORE_INPUT:
  search_query: string
  search_mode: "broad" | "deep"
  target_type: string              # SELECT에서 그대로 전달
  target_id: string | null
  conflict_with: string | null     # CONFLICTS 해결 시 상대방 ID
  existing_hypotheses: {hyp_id: summary}  # 충돌 감지용
  next_obs_id: number              # 다음 observation ID (오케스트레이터가 계산)
  next_hyp_id: number              # 다음 hypothesis ID (오케스트레이터가 계산)
  retry_count: number              # 재시도 횟수 (0, 1, 2)

EXPLORE_OUTPUT:
  status: "success" | "partial" | "failure"
  observations: [{
    id: string,                    # "obs_{auto_increment}"
    summary: string,
    source_url: string,
    source_type: string,
    authority: number
  }]
  type_a_hypotheses: [{
    id: string,                    # "hyp_A{auto_increment}"
    summary: string,
    verify_keywords: string[]
  }]
  edges: [{from, to, type, weight}]
  retry_keywords: string[]         # 실패 시 대안 키워드 3개
```

#### IDEATE I/O

```yaml
IDEATE_INPUT:
  question: string
  health_issues: string[]          # "ALL_WEAK" 등 힌트용
  observations: {obs_id: summary}
  hypotheses: {hyp_id: "[type|status|strength] summary"}
  conflicts: [{from, to}]
  edges: [{from, to, type}]        # 관계 파악용
  next_hyp_id: number              # 사용할 hypothesis ID (오케스트레이터가 계산)

IDEATE_OUTPUT:
  hypothesis: {
    id: string,                    # "hyp_B{auto_increment}"
    summary: string,
    reasoning_tool: string,
    derived_from: string[],
    verify_keywords: string[]
  }
```

### 4.4 상태 전달 흐름

```
┌─────────────────────────────────────────────────────────────────┐
│  cognigraph.json (Single Source of Truth)                       │
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │ health:     │    │ iteration:  │    │ lens_index: │         │
│  │  issues: [] │    │  15         │    │  3          │         │
│  └──────┬──────┘    └─────────────┘    └─────────────┘         │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    ORCHESTRATOR                          │   │
│  │                                                          │   │
│  │   health.issues ──────────────────┐                      │   │
│  │                                   ▼                      │   │
│  │   ┌────────┐  select_output  ┌─────────┐  explore_out   │   │
│  │   │ SELECT │ ───────────────▶│ EXPLORE │ ──────────┐    │   │
│  │   └────────┘                 └─────────┘           │    │   │
│  │        │                          │                │    │   │
│  │        │ health.issues            │                │    │   │
│  │        ▼                          │                │    │   │
│  │   ┌────────┐                      │                │    │   │
│  │   │ IDEATE │ (3회마다)            │                │    │   │
│  │   └────────┘                      │                │    │   │
│  │        │                          │                │    │   │
│  │        │ ideate_output            │                │    │   │
│  │        ▼                          ▼                ▼    │   │
│  │   ┌─────────────────────────────────────────────────┐   │   │
│  │   │                    UPDATE                        │   │   │
│  │   │  - select_output.target_type/id                 │   │   │
│  │   │  - explore_output.observations/hypotheses/edges │   │   │
│  │   │  - ideate_output.hypothesis (있으면)            │   │   │
│  │   └─────────────────────────────────────────────────┘   │   │
│  │                          │                               │   │
│  │                          ▼                               │   │
│  │   ┌────────┐  issues  ┌──────────────────┐              │   │
│  │   │ CHECK  │ ────────▶│ health.issues    │ (5회마다)    │   │
│  │   └────────┘          └──────────────────┘              │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 4.5 EXPLORE 재시도 로직

```python
def run_explore_with_retry(explore_input, max_retry=2):
    """EXPLORE 실패 시 자동 재시도"""
    original_query = explore_input["search_query"]

    for retry in range(max_retry + 1):
        explore_input["retry_count"] = retry
        if retry > 0 and last_output.get("retry_keywords"):
            explore_input["search_query"] = last_output["retry_keywords"][retry - 1]

        explore_output = call_claude("EXPLORE", explore_input)

        if explore_output["status"] != "failure":
            return explore_output

        last_output = explore_output

    # 3회 모두 실패
    return {
        "status": "failure",
        "observations": [],
        "type_a_hypotheses": [],
        "edges": [],
        "retry_keywords": [],
        "conflict_resolution": None
    }
```

### 4.6 CONFLICTS 해결 판정

**문제:** 조건 차이를 찾아도 CONFLICTS 엣지가 그대로 남아 계속 우선순위 1로 선택됨

**해결:** CONFLICTS 엣지에 `resolved` 플래그 추가

```json
// cognigraph.json edges
{
  "from": "hyp_A2",
  "to": "hyp_A1",
  "type": "CONFLICTS",
  "weight": 1.0,
  "created_at": 2,
  "resolved": false,           // ★ 추가
  "resolution": null           // "조건 차이: 도메인 특화 vs 실시간"
}
```

**SELECT에서 CONFLICTS 필터링:**
```python
active_conflicts = [
    e for e in edges
    if e["type"] == "CONFLICTS"
    and not e.get("resolved", False)
    and hypotheses[e["from"]]["status"] != "rejected"
    and hypotheses[e["to"]]["status"] != "rejected"
]
```

**EXPLORE에서 해결 판정:**
```yaml
EXPLORE_OUTPUT:
  # ... 기존 필드
  conflict_resolution: {         # 충돌 해결 정보 (있으면)
    conflict_edge: {from, to},
    resolution_type: "condition_difference" | "definition_mismatch" | "scope_mismatch" | "one_rejected" | "merged",
    description: "..."
  } | null
```

**resolution_type 정의:**
```
condition_difference  - 조건에 따라 둘 다 맞음
                        예: "컨텍스트 <32K: 인덱싱, >100K: 압축"

definition_mismatch   - 용어의 정의가 다름 (★ v2.5 추가)
                        예: "hyp_A2는 RAG='vector retrieval', hyp_A4는 RAG='retrieval+rerank'"

scope_mismatch        - 적용 범위가 다름 (★ v2.5 추가)
                        예: "hyp_A1은 텍스트 전용, hyp_A3은 멀티모달 포함"

one_rejected          - 한쪽이 틀림
merged                - 통합됨
```

**UPDATE에서 적용:**
```python
if explore_output.get("conflict_resolution"):
    res = explore_output["conflict_resolution"]
    for edge in cg["edges"]:
        if (edge["type"] == "CONFLICTS" and
            edge["from"] == res["conflict_edge"]["from"] and
            edge["to"] == res["conflict_edge"]["to"]):
            edge["resolved"] = True
            edge["resolution"] = res["description"]
```

### 4.7 SELECT 단계

**목적:** 이번 iteration에서 무엇을 탐색할지 결정

**탐색 대상 선택 우선순위:**

```
1. 미해결 CONFLICTS (resolved=false, 둘 다 active)
2. unvisited Type B 가설
3. unvisited Type A 가설
4. tested but strength 0.35~0.65 가설
5. unexplored 키워드 (used=false)
6. 6렌즈 발산
```

**검색 모드:**
```
Early Stage (가설 < 5개) → broad
Late Stage (가설 >= 5개) → deep
```

**6렌즈 발산:**
```
lens = ["definition", "scope", "comparison", "cases", "limitations", "application"]
current = lens[lens_index % 6]
```

**SELECT 프롬프트:**

```markdown
## SELECT

### 입력 (SELECT_INPUT)
- question: "{question}"
- iteration: {iteration}
- health_issues: {health_issues}
- conflicts: {active_conflicts}  # resolved=false만
- unvisited_type_b: {list}
- unvisited_type_a: {list}
- tested_uncertain: {list}
- unexplored_unused: {list}
- lens_index: {number}
- hypotheses_summary: {hyp_id: summary}

### 우선순위
1. conflicts 있으면 → 충돌 해결
2. unvisited_type_b 있으면 → Type B 검증
3. unvisited_type_a 있으면 → Type A 검증
4. tested_uncertain 있으면 → 애매한 것 확정
5. unexplored_unused 있으면 → 키워드 탐색
6. 위 모두 없으면 → 6렌즈 발산

### health_issues 대응
- "STALEMATE" → conflicts 강제 선택
- "LOW_QUALITY" → 검색어에 "research paper" 추가
- "ALL_WEAK" → 새 관점 탐색 (6렌즈 또는 unexplored)

### 출력 (SELECT_OUTPUT)
```json
{
  "target_type": "hypothesis" | "unexplored" | "6lens",
  "target_id": "hyp_A1" | "keyword" | null,
  "conflict_with": "hyp_B1" | null,
  "search_query": "검색어",
  "search_mode": "broad" | "deep",
  "reason": "선택 이유"
}
```

**conflict_with 규칙:**
- conflicts에서 선택 시: 상대방 가설 ID
- 그 외: null
```

### 4.8 EXPLORE 단계

**목적:** 웹 검색으로 Observation과 Type A Hypothesis 수집

**source_type 판별 & authority:**
```
paper    (arxiv, doi, acm, ieee, scholar)     → 0.9
official (docs.*, github.io/docs)             → 0.85
blog     (medium, dev.to, 개인 블로그)        → 0.5
forum    (reddit, stackoverflow, 커뮤니티)   → 0.3
unknown  (출처 불명)                          → 0.2
```

**EXPLORE 프롬프트:**

```markdown
## EXPLORE

### 입력 (EXPLORE_INPUT)
- search_query: "{search_query}"
- search_mode: "{broad|deep}"
- target_type: "{hypothesis|unexplored|6lens}"
- target_id: "{hyp_id|keyword|null}"
- conflict_with: "{hyp_id|null}"   # 충돌 해결 대상
- existing_hypotheses: {hyp_id: summary}
- next_obs_id: {number}            # 사용할 observation 시작 ID
- next_hyp_id: {number}            # 사용할 hypothesis 시작 ID
- retry_count: {0|1|2}

### 작업

1. **웹 검색 실행**
   - search_mode=broad: 다양한 관점 수집
   - search_mode=deep: 특정 가설 검증/반박 집중

2. **Observation 추출** (순수 사실만)
   - id: "obs_{다음 번호}"
   - summary: 1~3줄, 핵심 수치/사실 포함

3. **Type A 가설 추출** (타인의 주장)
   - id: "hyp_A{다음 번호}"
   - summary: 주장 + 근거 + 조건

4. **Edge 생성**
   - SUPPORTS/CONTRADICTS: obs → 기존 hyp (weight 0.8/0.5/0.3)
   - CONFLICTS: 새 hyp_A ↔ 기존 hyp (상반된 주장일 때)

5. **충돌 해결 감지** (conflict_with가 있을 때)
   - target_id vs conflict_with 간의 조건 차이 탐색
   - 발견 시 conflict_resolution 작성 (conflict_edge: {from: target_id, to: conflict_with})

### 출력 (EXPLORE_OUTPUT)
```json
{
  "status": "success" | "partial" | "failure",
  "observations": [
    {"id": "obs_5", "summary": "...", "source_url": "...", "source_type": "paper", "authority": 0.9}
  ],
  "type_a_hypotheses": [
    {"id": "hyp_A3", "summary": "...", "verify_keywords": ["kw1", "kw2"]}
  ],
  "edges": [
    {"from": "obs_5", "to": "hyp_A1", "type": "SUPPORTS", "weight": 0.8}
  ],
  "retry_keywords": ["대안 키워드1", "대안 키워드2", "대안 키워드3"],
  "conflict_resolution": {
    "conflict_edge": {"from": "hyp_A2", "to": "hyp_A1"},
    "resolution_type": "condition_difference",
    "description": "도메인 특화 시 fine-tuning, 실시간 업데이트 시 RAG"
  } | null
}
```
```

**재시도:** 오케스트레이터가 status=failure 시 retry_keywords[0]으로 재호출 (최대 2회)

### 4.9 IDEATE 단계 ★ (핵심)

**목적:** 6개 사고 도구로 창의적 가설 생성

**실행 조건:** `iteration >= 3 AND iteration % 3 == 0`

**IDEATE 프롬프트:**

```markdown
## IDEATE

### 입력 (IDEATE_INPUT)
- question: "{question}"
- health_issues: {issues}  # "ALL_WEAK" 시 새 프레이밍 강조
- observations: {obs_id: summary}
- hypotheses: {hyp_id: "[type|status|strength] summary"}
- conflicts: [{from, to}]
- edges: [{from, to, type}]

### 작업

6개 사고 도구를 **모두** 사용하여 각각 1개씩 가설 생성:

1. **패턴 인식**: 공통점 → 일반화
2. **유추**: 다른 분야에서 원리 차용
3. **제1원리**: 가정 의심
4. **인과 체인**: 연장/분기
5. **SCAMPER**: 결합
6. **역발상**: 뒤집기 (항상 포함 - 확증 편향 방지)

### health_issues 대응
- "ALL_WEAK" → 기존 가설이 모두 약함, 완전히 새로운 프레이밍 시도
- "STALEMATE" → 충돌 해결에 도움되는 통합 가설 우선

### 최종 선택 기준
1. 원래 질문의 답을 바꿀 가능성
2. 기존 가설들을 통합하거나 뒤집을 가능성
3. **검증 가능성** (너무 추상적이면 X)

### 출력 (IDEATE_OUTPUT)
```json
{
  "hypothesis": {
    "id": "hyp_B{다음 번호}",
    "summary": "1~3줄 요약. 주장 + 근거 + 조건",
    "reasoning_tool": "SCAMPER",
    "derived_from": ["obs_1", "hyp_A2"],
    "verify_keywords": ["검증용 키워드1", "검증용 키워드2"]
  }
}
```
```

### 4.10 UPDATE 단계 (3단계 분리)

**목적:** cognigraph.json 갱신. 3개 함수로 분리하여 IDEATE가 최신 데이터 사용 가능.

#### apply_explore_updates (EXPLORE 결과 반영)

```python
def apply_explore_updates(cg, select_output, explore_output):
    """EXPLORE 결과를 cognigraph에 반영 (IDEATE 전에 호출)"""

    # 1. 새 Observation 추가
    for obs in explore_output["observations"]:
        cg["observations"][obs["id"]] = {
            "summary": obs["summary"],
            "authority": obs["authority"],
            "source_url": obs["source_url"],
            "source_type": obs["source_type"],
            "created_at": cg["iteration"]
        }

    # 2. 새 Type A 추가 (초기 strength = 0.5)
    for hyp_a in explore_output["type_a_hypotheses"]:
        cg["hypotheses"][hyp_a["id"]] = {
            "type": "A",
            "summary": hyp_a["summary"],
            "strength": 0.5,
            "status": "unvisited",
            "visit_count": 0,
            "last_visited": None,
            "created_at": cg["iteration"],
            "reasoning_tool": None,
            "verify_keywords": hyp_a.get("verify_keywords", [])
        }
        # ★ Type A도 verify_keywords → unexplored 추가
        for kw in hyp_a.get("verify_keywords", []):
            if not any(u["keyword"] == kw for u in cg["unexplored"]):  # 중복 방지
                cg["unexplored"].append({"keyword": kw, "from": hyp_a["id"], "used": False})

    # 3. 엣지 추가 (중복 방지)
    for new_edge in explore_output["edges"]:
        if not edge_exists(cg, new_edge):  # ★ 중복 체크
            new_edge["created_at"] = cg["iteration"]
            new_edge["resolved"] = False
            cg["edges"].append(new_edge)

    # 4. CONFLICTS 해결 처리
    if explore_output.get("conflict_resolution"):
        res = explore_output["conflict_resolution"]
        conflict_pair = {res["conflict_edge"]["from"], res["conflict_edge"]["to"]}
        for edge in cg["edges"]:
            if (edge["type"] == "CONFLICTS" and
                {edge["from"], edge["to"]} == conflict_pair):
                edge["resolved"] = True
                edge["resolution"] = res["description"]

    # 5. 신뢰도 재계산
    for hyp_id, hyp in cg["hypotheses"].items():
        if hyp["status"] != "rejected":
            hyp["strength"] = calculate_strength(hyp_id, cg)

    return cg


def edge_exists(cg, new_edge):
    """동일한 엣지가 이미 존재하는지 확인"""
    for e in cg["edges"]:
        if (e["from"] == new_edge["from"] and
            e["to"] == new_edge["to"] and
            e["type"] == new_edge["type"]):
            return True
    return False
```

#### apply_ideate_updates (IDEATE 결과 반영)

```python
def apply_ideate_updates(cg, ideate_output):
    """IDEATE 결과를 cognigraph에 반영"""
    if not ideate_output:
        return cg

    hyp_b = ideate_output["hypothesis"]
    cg["hypotheses"][hyp_b["id"]] = {
        "type": "B",
        "summary": hyp_b["summary"],
        "strength": 0.4,  # Type B 초기값
        "status": "unvisited",
        "visit_count": 0,
        "last_visited": None,
        "created_at": cg["iteration"],
        "reasoning_tool": hyp_b["reasoning_tool"],
        "verify_keywords": hyp_b["verify_keywords"]
    }

    # verify_keywords → unexplored
    for kw in hyp_b["verify_keywords"]:
        if not any(u["keyword"] == kw for u in cg["unexplored"]):
            cg["unexplored"].append({"keyword": kw, "from": hyp_b["id"], "used": False})

    return cg
```

#### finalize_iteration (상태 전환 및 마무리)

```python
def finalize_iteration(cg, select_output, explore_output):
    """iteration 마무리: 상태 전환, 소비 처리"""

    # ★ EXPLORE 실패 시 상태 변경 없이 iteration만 증가
    if explore_output["status"] == "failure":
        cg["iteration"] += 1
        return cg

    # 1. 탐색 대상 상태 갱신 (hypothesis 타입일 때만)
    if select_output["target_type"] == "hypothesis":
        target_id = select_output["target_id"]
        if target_id in cg["hypotheses"]:
            hyp = cg["hypotheses"][target_id]
            hyp["visit_count"] += 1
            hyp["last_visited"] = cg["iteration"]

            # 상태 전환
            if hyp["visit_count"] >= 2 and hyp["strength"] >= 0.65:
                # ★ v2.5: 강한 반박이 없어야 verified (반박을 견뎠다는 의미)
                has_strong_contradict = any(
                    e["to"] == target_id and e["type"] == "CONTRADICTS" and e["weight"] >= 0.5
                    for e in cg["edges"]
                )
                if not has_strong_contradict:
                    hyp["status"] = "verified"
                # else: tested 유지 (반박 해결 필요)
            elif hyp["strength"] < 0.25:
                hyp["status"] = "rejected"
            elif hyp["status"] == "unvisited":
                hyp["status"] = "tested"

    # 2. unexplored 소비 처리 (unexplored 타입일 때만)
    if select_output["target_type"] == "unexplored":
        used_kw = select_output["target_id"]
        for item in cg["unexplored"]:
            if item["keyword"] == used_kw and not item["used"]:
                item["used"] = True
                break

    # 3. 6렌즈 인덱스 갱신 (6lens 타입일 때만)
    if select_output["target_type"] == "6lens":
        cg["lens_index"] += 1

    # 4. iteration 증가
    cg["iteration"] += 1

    return cg
```

**핵심 변경:**
- **3단계 분리:** IDEATE가 EXPLORE 결과를 볼 수 있음
- **Type A 키워드 보존:** verify_keywords → unexplored 추가
- **중복 엣지 방지:** `edge_exists()` 체크
- **실패 처리:** EXPLORE 실패 시 상태 변경 스킵

### 4.11 CHECK 단계 (매 5 iteration)

**목적:** 시스템 건강 상태 점검 및 대응

**CHECK 로직:**

```python
def health_check(cognigraph):
    issues = []

    obs_list = list(cognigraph["observations"].values())
    hyp_list = [h for h in cognigraph["hypotheses"].values()
                if h["status"] != "rejected"]

    # 1. 품질 체크 (LOW_QUALITY)
    avg_authority = mean([o["authority"] for o in obs_list]) if obs_list else 0
    if avg_authority < 0.5:
        issues.append("LOW_QUALITY")

    # 2. 전멸 체크 (ALL_WEAK)
    if len(hyp_list) >= 3 and all(h["strength"] < 0.35 for h in hyp_list):
        issues.append("ALL_WEAK")

    # 3. 교착 체크 (STALEMATE)
    conflicts = [e for e in cognigraph["edges"] if e["type"] == "CONFLICTS"]
    # 미해결(resolved=false) AND 양쪽 다 active인 것만
    active_conflicts = [
        c for c in conflicts
        if not c.get("resolved", False)  # ★ resolved 체크 추가
        and cognigraph["hypotheses"].get(c["from"], {}).get("status") != "rejected"
        and cognigraph["hypotheses"].get(c["to"], {}).get("status") != "rejected"
    ]
    old_conflicts = [c for c in active_conflicts
                     if cognigraph["iteration"] - c["created_at"] > 3]
    if len(old_conflicts) >= 1:
        issues.append("STALEMATE")

    # 4. 폭발 체크 (DATA_EXPLOSION)
    if len(cognigraph["observations"]) > 50 or len(hyp_list) > 25:
        issues.append("DATA_EXPLOSION")

    # 5. 포화 체크 (SATURATED)
    if cognigraph["iteration"] >= 15:
        verified_count = len([h for h in hyp_list if h["status"] == "verified"])
        unvisited_count = len([h for h in hyp_list if h["status"] == "unvisited"])
        if verified_count >= 3 and unvisited_count == 0:
            issues.append("SATURATED")

    return issues
```

**이슈별 대응 (단순화):**

| 이슈 | 대응 |
|------|------|
| LOW_QUALITY | 검색어에 "research paper" 추가 |
| ALL_WEAK | 다음 IDEATE에서 "기존 가설 모두 약함, 새 프레이밍 필요" 힌트 |
| STALEMATE | 다음 SELECT에서 충돌 가설 강제 선택 + "vs comparison" 검색 |
| DATA_EXPLOSION | strength < 0.3 가설을 rejected로 변경 (단순 삭제 효과) |
| SATURATED | 사용자에게 Thesis 생성 제안 |

**삭제된 것:**
- ~~CONSENSUS_BIAS~~: 자동 판단 어려움. 대신 IDEATE에서 항상 역발상(Inversion) 도구 포함

**삭제된 것:**
- ~~SEARCH_FAILURE~~: EXPLORE에서 즉시 대응하므로 CHECK 불필요

---

## 5. 신뢰도 계산

### 5.1 공식

```python
def calculate_strength(hyp_id, cognigraph):
    hyp = cognigraph["hypotheses"][hyp_id]

    # 기본값
    base = 0.4 if hyp["type"] == "B" else 0.5

    # 지지 점수
    support_edges = [e for e in cognigraph["edges"]
                     if e["to"] == hyp_id and e["type"] == "SUPPORTS"]
    support_score = sum(
        cognigraph["observations"][e["from"]]["authority"] * e["weight"] * 0.1
        for e in support_edges
        if e["from"] in cognigraph["observations"]
    )

    # 반박 점수
    contradict_edges = [e for e in cognigraph["edges"]
                        if e["to"] == hyp_id and e["type"] == "CONTRADICTS"]
    contradict_score = sum(
        cognigraph["observations"][e["from"]]["authority"] * e["weight"] * 0.15
        for e in contradict_edges
        if e["from"] in cognigraph["observations"]
    )

    # 다양성 보너스 (source_url에서 도메인 추출)
    supporting_obs = [e["from"] for e in support_edges]
    domains = set(
        extract_domain(cognigraph["observations"][o]["source_url"])
        for o in supporting_obs
        if o in cognigraph["observations"]
    )
    diversity_bonus = min(len(domains) * 0.03, 0.15)

    # 최종 계산
    strength = base + support_score - contradict_score + diversity_bonus
    return max(0.0, min(1.0, strength))  # clamp to [0, 1]


def extract_domain(url):
    """https://arxiv.org/abs/123 → arxiv.org"""
    from urllib.parse import urlparse
    return urlparse(url).netloc
```

### 5.2 엣지 weight 기준

*3.4 엣지 정의 참조*

```
0.8 = 직접적 증거, 같은 주제, 논리적 필연
0.5 = 관련 있지만 간접적
0.3 = 연관은 있으나 논리적 비약 존재
```

### 5.3 Authority 기준 (source_type별)

```
paper    → 0.9   (arxiv, doi, acm, ieee, scholar)
official → 0.85  (docs.*, github.io/docs, 공식 문서)
blog     → 0.5   (medium, dev.to, 개인 블로그)
forum    → 0.3   (reddit, stackoverflow, 커뮤니티)
unknown  → 0.2   (출처 불명)
```

*4.3 EXPLORE의 authority 자동 계산과 동일*

---

## 6. Thesis 생성

### 6.1 트리거

- 사용자 명시적 요청: `pathfinder-thesis`
- 시스템 제안 (SATURATED 상태)

### 6.2 생성 로직

```python
def generate_thesis(cognigraph):
    # 1. 핵심 가설 선정 (verified + 강한 tested)
    core_hypotheses = [
        (hyp_id, h) for hyp_id, h in cognigraph["hypotheses"].items()
        if h["status"] == "verified" or
           (h["status"] == "tested" and h["strength"] >= 0.55)
    ]

    # 2. strength 순 정렬
    core_hypotheses.sort(key=lambda x: x[1]["strength"], reverse=True)

    # 3. 관련 observation 수집
    evidence = get_supporting_observations(cognigraph, [h[0] for h in core_hypotheses])

    # 4. 구조화 (Type B 가설은 "에이전트 통찰"로 별도 표기)
    return structure_thesis(core_hypotheses, evidence, cognigraph["question"])


def get_supporting_observations(cognigraph, hyp_ids):
    """가설들을 지지하는 observation 수집"""
    obs_ids = set()
    for edge in cognigraph["edges"]:
        if edge["type"] == "SUPPORTS" and edge["to"] in hyp_ids:
            obs_ids.add(edge["from"])

    return [
        (obs_id, cognigraph["observations"][obs_id])
        for obs_id in obs_ids
        if obs_id in cognigraph["observations"]
    ]
```

**변경점:**
- verified 조건 완화: `strength >= 0.65` (기존 0.7)
- tested + `strength >= 0.55`도 Thesis에 포함
- get_supporting_observations 구현 추가

### 6.3 thesis.md 포맷

```markdown
# 정설: {질문에 대한 답}

## 연구 개요
- 질문: {original_question}
- 연구 기간: {iterations} iterations
- 수집된 관찰: {obs_count}개
- 생성된 가설: {hyp_count}개 (Type A: {a_count}, Type B: {b_count})

## 핵심 결론

[가장 강한 verified 가설 기반 1-2문장 답변]

## 주요 발견

### 발견 1: {제목} (신뢰도: 0.85)
**가설:** {statement}

**근거:**
- obs_1: {요약}
- obs_5: {요약}

**사고 도구:** {reasoning_tool}

### 발견 2: {제목} (신뢰도: 0.78)
...

## 조건 및 한계

[qualified 가설들 - "단, ~인 경우에만" 형태]

## 기각된 가설

| 가설 | 기각 이유 | 반박 증거 |
|------|----------|----------|
| hyp_3 | strength 0.18 | obs_7, obs_12가 강하게 반박 |

## 미해결 영역

- {unvisited 가설 목록}
- {unexplored 방향 목록}

## 연구 히스토리

| Iteration | 주요 이벤트 |
|-----------|------------|
| 1 | 초기 6렌즈 발산 |
| 5 | hyp_B2 생성 (패턴 인식) |
| 10 | hyp_A1 vs hyp_A3 충돌 해결 |
| ... | ... |

## 참고 출처 (Authority 순)

1. [논문] {title} - {url}
2. [공식문서] {title} - {url}
3. [블로그] {title} - {url}
```

---

## 7. 엣지 케이스 대응 (단순화)

### 7.1 LOW_QUALITY (저품질 소스)

```
감지: 평균 authority < 0.5

대응:
- 검색어에 "research paper" 추가
- source_type이 forum인 결과 가중치 하향
```

### 7.2 ALL_WEAK (모든 가설 약함)

```
감지: 모든 가설 strength < 0.35

대응:
- 다음 IDEATE(3회차)에 힌트 전달:
  "기존 가설 모두 약함. 질문 재프레이밍 또는 새 관점 필요"
```

### 7.3 STALEMATE (충돌 미해결)

```
감지: CONFLICTS 엣지가 3 iteration 이상 미해결

대응:
- SELECT에서 충돌 가설 강제 선택
- 검색어: "[가설A] vs [가설B] comparison when"
- 조건 차이를 찾아 QUALIFIES 형태로 summary에 기록
```

### 7.4 DATA_EXPLOSION (데이터 폭발)

```
감지: obs > 50 or hyp > 25

대응:
- strength < 0.3 가설을 rejected로 변경
- rejected 가설은 IDEATE와 SELECT에서 무시
- 파일은 삭제 안 함 (Thesis에서 "기각된 가설" 목록용)
```

**삭제된 케이스:**
- ~~SEARCH_FAILURE~~: EXPLORE에서 즉시 대응
- ~~순환 참조~~: INSPIRES 엣지 삭제로 불필요
- ~~CONSENSUS_BIAS~~: 자동 판단 어려움 → IDEATE에서 항상 역발상 포함으로 대체

---

## 8. 구현 체크리스트

### 8.1 파일 변경

```
[ ] bin/pathfinder-research   # 메인 루프 수정 (IDEATE 3회마다)
[ ] bin/pathfinder-thesis     # 새로 생성
[ ] bin/pathfinder-status     # cognigraph 기반으로 수정
[ ] lib/init-session.sh       # cognigraph.json 초기화
[ ] prompts/explore.md        # EXPLORE 프롬프트 (충돌 감지 포함)
[ ] prompts/ideate.md         # IDEATE 프롬프트 (cognigraph.json만 참조)
[ ] prompts/thesis.md         # Thesis 생성 프롬프트
```

### 8.2 새로 구현할 기능

```
[ ] cognigraph.json CRUD
[ ] source_type 자동 판별 (URL 기반)
[ ] 신뢰도 계산 로직
[ ] 상태 전환 로직 (unvisited→tested→verified/rejected)
[ ] 건강 체크 로직 (5개 이슈)
[ ] EXPLORE 내 충돌 감지
[ ] Thesis 생성 로직
```

**삭제된 것들:**
- ~~2-Hop 컨텍스트 스코핑~~: cognigraph.json 전체 summary 사용
- ~~INSPIRES 엣지 관리~~: summary에 텍스트로 기록
- ~~archived 상태 관리~~: rejected로 단순화

### 8.3 마이그레이션

```
기존 세션 (v1) → 새 세션 (v2)

evidence/ → observations/ (summary 추가 필요)
claims/ → hypotheses/ (type: A, summary 추가 필요)
summary.md → cognigraph.json 생성
holes.json → cognigraph.unexplored로 이전 (used: false로)
```

---

## 9. 부록

### 9.1 사고 도구 상세

| 도구 | 질문 | 적합한 상황 |
|------|------|------------|
| 패턴 인식 | "공통점은 무엇인가?" | 여러 obs에서 규칙성 보일 때 |
| 유추 | "다른 분야에서 비슷한 것은?" | 막힐 때, 새 관점 필요 |
| 제1원리 | "왜 이게 당연한가?" | 기존 가정 의심 |
| 인과 체인 | "그 다음은 무엇인가?" | 결과 예측, 영향 분석 |
| SCAMPER | "합치면 어떻게 되는가?" | 두 아이디어 통합 |
| 역발상 | "반대면 어떻게 되는가?" | 확증 편향 방지 |

### 9.2 CogniGraph 쿼리 예시

```python
# 활성 충돌 쌍 찾기 (resolved=false, 양쪽 active)
def get_active_conflicts(cg):
    return [
        (e["from"], e["to"])
        for e in cg["edges"]
        if e["type"] == "CONFLICTS"
        and not e.get("resolved", False)
        and cg["hypotheses"].get(e["from"], {}).get("status") != "rejected"
        and cg["hypotheses"].get(e["to"], {}).get("status") != "rejected"
    ]

# 특정 가설의 지지 증거
supports = [e["from"] for e in edges
            if e["to"] == "hyp_1" and e["type"] == "SUPPORTS"]

# unvisited Type B 가설 (SELECT 우선순위 2)
unvisited_b = [hid for hid, h in hypotheses.items()
               if h["type"] == "B" and h["status"] == "unvisited"]

# 미사용 unexplored 키워드 (SELECT 우선순위 5)
unused_keywords = [u for u in unexplored if not u["used"]]

# SELECT_INPUT 빌드 (오케스트레이터용)
def build_select_input(cg):
    hyp_list = [(hid, h) for hid, h in cg["hypotheses"].items() if h["status"] != "rejected"]
    return {
        "question": cg["question"],
        "iteration": cg["iteration"],
        "health_issues": cg["health"].get("issues", []),
        "conflicts": get_active_conflicts(cg),
        "unvisited_type_b": [hid for hid, h in hyp_list if h["type"] == "B" and h["status"] == "unvisited"],
        "unvisited_type_a": [hid for hid, h in hyp_list if h["type"] == "A" and h["status"] == "unvisited"],
        "tested_uncertain": [hid for hid, h in hyp_list if h["status"] == "tested" and 0.35 <= h["strength"] <= 0.65],
        "unexplored_unused": [u for u in cg["unexplored"] if not u["used"]],
        "lens_index": cg["lens_index"],
        "hypotheses_summary": {hid: h["summary"] for hid, h in hyp_list}
    }

# IDEATE_INPUT 빌드는 4.2 헬퍼 함수 섹션 참조
# (next_hyp_id 포함 버전)
```

### 9.3 신뢰도 변화 예시

```
hyp_1 (Type A) 초기: 0.5

Iteration 3:
  obs_2 (authority 0.9) SUPPORTS (weight 0.8)
  → +0.9 * 0.8 * 0.1 = +0.072
  → 0.572

Iteration 5:
  obs_5 (authority 0.85) SUPPORTS (weight 0.5)
  → +0.85 * 0.5 * 0.1 = +0.0425
  → 0.6145
  다양성 보너스 (2 domains): +0.06
  → 0.6745

Iteration 8:
  obs_9 (authority 0.9) CONTRADICTS (weight 0.8)
  → -0.9 * 0.8 * 0.15 = -0.108
  → 0.5665

최종: 0.5665 (tested 상태, verified 미달)
```

---

## 10. 버전 히스토리

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| v2.0 | 2024-02 | 초기 설계 - 관찰-가설-정설 프레임워크 |
| v2.1 | 2024-02 | 단순화 - 오컴의 면도날 적용 |
| v2.2 | 2024-02 | 논리 충돌 해결, 미정의 로직 보완 |
| v2.3 | 2024-02 | 인터페이스 계약 추가, 컴포넌트 간 연결 명확화 |
| v2.4 | 2024-02 | 컴포넌트 간 유기적 소통 강화, 책임 분리 |
| v2.5 | 2024-02 | verified 조건 강화, resolution_type 확장 |

### v2.1 주요 변경사항

**IDEATE 빈도 조정:**
- 매 루프 → 3회마다 (iteration % 3 == 0)
- Type B 폭발 방지 (50회 기준 50개 → 16개)

**cognigraph.json 단순화:**
- summary 강화: 1~3줄로 판단 가능한 정보량
- 삭제: concepts, archived, exploring 상태
- 엣지: INSPIRES, QUALIFIES 삭제 → summary에 텍스트로

**SELECT 우선순위:**
- CONFLICTS 해결을 1순위로 승격

**EXPLORE 즉시 대응:**
- 검색 실패 시 같은 iteration 내 질문 분해
- source_type 자동 판별 로직 추가

**상태/조건 완화:**
- verified: strength > 0.7 → >= 0.65
- rejected: strength < 0.2 → < 0.25
- Thesis: tested + strength >= 0.55도 포함

### v2.2 주요 변경사항

**타입/필드명 통일:**
- 엣지 `strength` → `weight` (숫자 0.8/0.5/0.3)
- `source` → `source_url` 통일
- 모든 코드를 dictionary 접근 방식으로 통일

**누락 로직 추가:**
- `lens_index`: cognigraph.json에 추가, 6렌즈 순환 상태 저장
- `used_keyword`: EXPLORE 출력에 추가
- Type A 초기 strength = 0.5, Type B = 0.4 명시
- `get_supporting_observations()` 구현 추가
- Early/Late Stage 기준: 가설 5개 기준

**CONFLICTS 처리 명확화:**
- 단방향 1개만 저장
- 한쪽 rejected 시 해결된 것으로 간주 (STALEMATE에서 제외)

**삭제:**
- CONSENSUS_BIAS 자동 감지 (판단 어려움)
- SELECT 프롬프트의 Exploring 상태 (삭제된 상태)

### v2.3 주요 변경사항

**오케스트레이터 추가:**
- 메인 루프 `run_iteration()` 정의
- 각 단계 호출 순서와 데이터 전달 명확화
- EXPLORE 재시도 로직 (`run_explore_with_retry`)

**인터페이스 계약 (I/O Schema):**
- SELECT_INPUT/OUTPUT 스키마 정의
- EXPLORE_INPUT/OUTPUT 스키마 정의
- IDEATE_INPUT/OUTPUT 스키마 정의
- 키 이름 통일 (`target_type`, `target_id` 등)

**CONFLICTS 해결 메커니즘:**
- edges에 `resolved`, `resolution` 필드 추가
- EXPLORE에서 `conflict_resolution` 출력
- UPDATE에서 해결된 충돌 마킹
- SELECT/CHECK에서 `resolved=false`만 활성 충돌로 취급

**상태 전달 명확화:**
- `health.issues` → SELECT, IDEATE로 전달
- `select_output.target_type`으로 UPDATE 분기
- cognigraph.json이 단일 진실의 원천

### v2.4 주요 변경사항

**컴포넌트 간 컨텍스트 전달 강화:**
- SELECT_OUTPUT에 `conflict_with` 추가: EXPLORE가 어떤 충돌을 해결해야 하는지 명시
- EXPLORE_INPUT에 `conflict_with`, `next_obs_id`, `next_hyp_id` 추가
- IDEATE_INPUT에 `next_hyp_id` 추가

**UPDATE 3단계 분리:**
- `apply_explore_updates()`: EXPLORE 결과 먼저 반영
- `apply_ideate_updates()`: IDEATE 결과 반영
- `finalize_iteration()`: 상태 전환 및 마무리
- ★ IDEATE가 EXPLORE 결과를 볼 수 있게 됨

**ID 관리 중앙화:**
- 오케스트레이터가 `next_obs_id`, `next_hyp_id` 계산
- EXPLORE/IDEATE는 전달받은 ID 사용
- ID 충돌 원천 차단

**Type A verify_keywords 보존:**
- Type A 가설의 verify_keywords도 unexplored에 추가
- 검증 경로 누락 방지

**실패 처리 강화:**
- EXPLORE 실패 시 상태 변경 없이 iteration만 증가
- "탐색 안 됐는데 완료 처리" 버그 수정

**중복 방지:**
- `edge_exists()`: 동일 엣지 중복 추가 방지
- unexplored 키워드 중복 체크

### v2.5 주요 변경사항

**verified 조건 강화:**
- 기존: `strength >= 0.65 AND visit_count >= 2`
- 추가: `AND 강한 반박(weight >= 0.5) 없음`
- **의미 변경:** "지지가 많다" → "반박을 견뎠다"
- 강한 반박이 있으면 tested 유지, 반박 해결 후 verified 가능

**resolution_type 확장:**
- 기존: `condition_difference | one_rejected | merged`
- 추가: `definition_mismatch | scope_mismatch`
- **이유:** 연구에서 대부분의 충돌은 "A vs B"가 아니라 "같은 용어를 다르게 정의"
- 예: RAG='vector retrieval' vs RAG='retrieval+rerank+tool'

---

*이 문서는 Pathfinder v2의 구현 기획서입니다.*
