# LOOP: Ralph Loop & Loop Drift Prevention

**목표:** 사용자가 중단할 때까지 무한 반복, 막힘 없이 진행

**핵심 원리:** "LLM은 종료하지 않는다. 외부가 통제한다."

---

## Ralph Loop란?

### 개념

**Ralph Loop**는 LLM의 종료 판단을 완전히 무시하고 외부에서 강제로 반복을 제어하는 패턴입니다.

| 전통적 AI Agent | Ralph Loop |
|----------------|-----------|
| LLM이 "충분하다" 판단 → 종료 | LLM 판단 무시, 외부만 제어 |
| 주관적 조기 종료 위험 | Objective criteria만으로 종료 |
| "완료했습니다" 출력 후 멈춤 | "계속합니다" 출력 후 재호출 |

### 출처

- [Alibaba Cloud Blog - From ReAct to Ralph Loop](https://www.alibabacloud.com/blog/from-react-to-ralph-loop-a-continuous-iteration-paradigm-for-ai-agents_602799)
- [Google ADK - Loop Guardrails](https://google.github.io/adk-docs/agents/workflow-agents/loop-agents/)

**핵심 인용:**
> "External control script cuts off exit signal via exit codes"
> "Loop Guardrails use External Enforcement, system guarantees termination"

### 장점

1. **LLM 주관 제거**: "충분하다"는 판단 불가
2. **일관된 종료 조건**: Objective criteria (max_iterations, budget, status)
3. **무한 심화 가능**: 사용자가 중단하지 않는 한 계속 탐색

---

## 구현 메커니즘

### Architecture

```
┌─────────────────────────────────────────┐
│ SKILL.md (LLM 실행)                      │
│                                         │
│ OUTPUT 단계 완료 → LOOP 단계 진입        │
│   ↓                                     │
│ Step 1: state.json 읽기                 │
│ Step 2: 종료 조건 체크                   │
│ Step 3: 조건 불만족 → Skill() 재호출     │
└─────────────────────────────────────────┘
                ↓ (재호출)
┌─────────────────────────────────────────┐
│ Stop Hook (.claude/hooks/stop-hook.py)  │
│                                         │
│ 1. state.json 다시 확인                 │
│ 2. Completion criteria 검증              │
│ 3. status != "running" → exit(0) 차단   │
│ 4. status == "running" → allow          │
└─────────────────────────────────────────┘
```

**이중 보호 (Defense in Depth):**

1. **SKILL.md**: LOOP 단계에서 재호출 결정
2. **stop-hook.py**: 툴 호출 차단으로 추가 검증

### Step 1: 종료 조건 체크

매 iteration 종료 시 state.json을 읽어서 확인:

```python
# .research/state.json 로드
state = json.load(open(".research/state.json"))

status = state["status"]  # "running", "completed", "paused", "stopped_by_user", "budget_exceeded"
current = state["iteration"]["current"]  # 현재 iteration 번호
max_iter = state["iteration"]["max"]  # 최대 iteration (기본 100)
budget = state["metrics"]["cost_estimate_usd"]  # 누적 비용
```

### Step 2: 종료 결정

다음 중 **하나라도** 해당하면 종료:

```python
should_stop = (
    status in ["completed", "paused", "stopped_by_user", "budget_exceeded"]
    or current >= max_iter
    or budget > 10.0
)

if should_stop:
    print("종료 조건 만족. 연구를 종료합니다.")
    # Skill() 호출 없이 종료
else:
    print("종료 조건 불만족. 다음 iteration을 시작합니다...")
    # Step 3로 진행
```

**종료 조건 상세:**

| 조건 | 설명 | 예시 |
|------|------|------|
| `status == "completed"` | 모든 서브질문 답변 완료 | 진행도 100% |
| `status == "paused"` | 사용자 일시정지 | `/research-pause` 실행 |
| `status == "stopped_by_user"` | 사용자 중단 | Ctrl+C 또는 `/research-stop` |
| `status == "budget_exceeded"` | 예산 초과 | cost > 10.0 USD |
| `current >= max_iter` | 최대 iteration 도달 | 100/100 |
| `budget > 10.0` | 비용 한도 초과 | $10.50 |

**안전 장치:**

- 기본 `max_iterations: 100` (무한 루프 방지)
- 기본 `budget_limit: 10.0` (비용 폭주 방지)

### Step 3: 다음 Iteration 호출

종료 조건을 만족하지 않으면 **즉시 Skill tool 재호출**:

**OUTPUT 메시지 형식:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Iteration #N 완료
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 이번 발견:
   - (핵심 발견 1) [✓✓ VERIFIED]
   - (핵심 발견 2) [✓ HIGH]

🎯 Active Hypotheses (Top 5):
   1. [H1] (가설 내용)
      확신도: 85% | Priority: 0.78 | 지지: 2개 | 반증: 0개
   ...

📈 다음 계획: (active_hypotheses 기반 탐색 전략)

📊 진행도: 45% (답변된 서브질문 / 전체)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

상태 확인:
- Iteration: 2/100
- Status: running
- Budget: $0.25/$10.00

→ 종료 조건 불만족 → 계속 실행

다음 iteration을 시작합니다...
```

**그 다음 즉시 Skill tool 호출:**

```
Skill(skill="deep-research", args="")
```

**중요 규칙:**

- ❌ **절대 금지 표현:**
  - "연구를 종료합니다"
  - "충분합니다"
  - "완료되었습니다"
  - "이 정도면 됩니다"

- ✅ **필수 표현:**
  - "다음 iteration을 시작합니다..."
  - "계속 탐색합니다..."
  - "더 깊이 파고듭니다..."

**종료는 오직 다음 경우에만:**

1. `state.json`의 `status`가 `"completed"`, `"paused"`, `"stopped_by_user"`, `"budget_exceeded"`
2. `current >= max_iterations`
3. `budget > 10.0`

**그 외 모든 경우: 무조건 재호출**

---

## Loop Drift 방지

### 문제 정의

**Loop Drift**란 무한 루프가 진행되면서 다음과 같은 비효율이 발생하는 현상:

1. 같은 검색 반복
2. 같은 행동 패턴 반복
3. 새 정보 없이 공회전
4. 막혔는데 돌파구 못 찾음

**결과:**

- 시간/비용 낭비
- 연구 진전 없음
- 사용자 신뢰 하락

### 4가지 방지 규칙

#### 규칙 1: 같은 검색 쿼리 2회 반복 금지

**탐지:**

```python
# PLAN 단계 Phase 3 (Deduplication)
from deduplicate_search import is_duplicate_query

for query in candidate_queries:
    is_dup, similar = is_duplicate_query(query)
    if is_dup:
        print(f"⚠️ Skip duplicate: '{query[:50]}...'")
        print(f"   Already searched: '{similar}'")
        # 이 쿼리는 final_queries에 추가 안 함
```

**조치:**

- 중복 쿼리 자동 필터링 (>0.95 유사도)
- 모든 쿼리가 중복이면 **전략 변경** 필수
  - Academic → Web
  - Positive → Counter-evidence
  - Recent → Historical
  - Broad → Niche

**예시:**

```
Phase 3 중복 체크:
1. ✓ "quantum error correction breakthrough 2026" (NEW)
2. ⚠️ Skip "quantum computing error correction" (>0.96 similarity with iteration 3 query)
3. ✓ "site:arxiv.org quantum error correction 2025" (NEW)

→ 최종 2개 쿼리 실행
```

#### 규칙 2: 같은 행동 패턴 3회 반복 금지

**탐지:**

```python
# state.json의 loop_drift 추적
loop_drift = state.get("loop_drift", {})
consecutive_same_action = loop_drift.get("consecutive_same_action", 0)
last_action_hash = loop_drift.get("last_action_hash", "")

# 현재 행동 패턴 해시 (예: "web_search_academic")
current_action_hash = compute_action_hash(current_iteration_actions)

if current_action_hash == last_action_hash:
    consecutive_same_action += 1
else:
    consecutive_same_action = 1

if consecutive_same_action >= 3:
    print("⚠️ Loop Drift 감지: 같은 행동 3회 반복")
    # 전략 강제 변경
    change_strategy()
```

**조치:**

- 3회 이상 반복 시 전략 변경
  - Web Search → GitHub Code Search
  - Hypothesis Testing → Counter-Evidence Search
  - Forward Reasoning → Backward Reasoning

**예시:**

```
Iteration 5: Web search "AI safety"
Iteration 6: Web search "AI alignment"
Iteration 7: Web search "AI ethics"

→ 3회 연속 Web search → 전략 변경
→ Iteration 8: "site:arxiv.org AI safety paper 2025"
```

#### 규칙 3: 5회 연속 새 정보 없음 → 다른 접근법

**탐지:**

```python
# SYNTHESIZE 단계에서 새 발견 카운트
new_findings_count = len(new_findings_this_iteration)

if new_findings_count == 0:
    state["loop_drift"]["no_new_info_count"] += 1
else:
    state["loop_drift"]["no_new_info_count"] = 0

if state["loop_drift"]["no_new_info_count"] >= 5:
    print("⚠️ Loop Drift 감지: 5회 연속 새 정보 없음")
    # 접근법 근본적 변경
    switch_approach()
```

**조치:**

- 접근법 근본적 변경
  - 다른 언어로 검색 (English → Korean, Chinese)
  - 다른 도메인으로 확장 (Technical → Business)
  - 다른 시간대 (Recent → Historical)
  - 제1원칙 사고 적용 (근본 가정 재검토)

**예시:**

```
Iteration 10-14: 새 정보 없음 (같은 결과 반복)

→ 5회 연속 → 접근법 변경
→ Iteration 15: 한국어 검색 "양자 컴퓨팅 실용화 2026"
→ Iteration 16: 제1원칙 적용 "양자 우위 = 무엇?"
```

#### 규칙 4: 막힘 감지 시 → Reflexion 메모리 참조

**탐지:**

```python
# REFLECT 단계 Layer 4 (Meta-Cognitive Monitoring)
# Self-Assessment에서 "막힘" 감지

if self_assessment["stuck"] == True:
    print("⚠️ 막힘 감지")
    # reflexion.json에서 과거 실패 패턴 로드
    reflexion = load_reflexion_memory()
    similar_failures = find_similar_failures(current_situation, reflexion)
    for failure in similar_failures:
        print(f"과거 실패: {failure['situation']}")
        print(f"원인: {failure['root_cause']}")
        print(f"해결책: {failure['solution']}")
```

**조치:**

- `.research/reflexion.json`에서 과거 실패 학습
- 비슷한 상황에서 성공한 전략 재사용
- 비슷한 상황에서 실패한 전략 회피

**Reflexion 메모리 구조:**

```json
{
  "failures": [
    {
      "iteration": 12,
      "situation": "검색 결과 없음 (너무 niche한 키워드)",
      "root_cause": "키워드가 너무 구체적",
      "solution": "더 넓은 키워드로 변경",
      "result": "성공 (새 정보 발견)"
    },
    {
      "iteration": 23,
      "situation": "모순된 소스 3개",
      "root_cause": "소스 신뢰도 미확인",
      "solution": "Peer-reviewed 논문 우선",
      "result": "성공 (모순 해결)"
    }
  ],
  "success_patterns": [
    {
      "strategy": "Academic → Web 전환",
      "situations": [5, 18, 31],
      "success_rate": 0.85
    }
  ]
}
```

**예시:**

```
Iteration 20: 막힘 (검색 결과 없음)

→ reflexion.json 참조
→ 과거 iteration 12에서 비슷한 상황
→ 해결책: "더 넓은 키워드로 변경"
→ 적용: "quantum computing" → "quantum technology"
→ 성공: 새 정보 발견
```

---

## search_history.json 중복 체크

### 목적

**과거 검색과의 중복 제거** (>0.95 유사도)

### 구현

`deduplicate_search.py` 모듈 사용:

```python
from deduplicate_search import is_duplicate_query, add_query_to_history

# PLAN 단계 Phase 3에서 호출
for query in candidate_queries:
    is_dup, similar = is_duplicate_query(query)

    if is_dup:
        print(f"⚠️ Skip duplicate: '{query[:50]}...'")
        print(f"   Similar to: '{similar}' (similarity >0.95)")
    else:
        final_queries.append(query)
        print(f"✓ NEW: '{query}'")

# EXECUTE 단계에서 검색 후 자동 저장
for query, result in zip(final_queries, search_results):
    add_query_to_history(
        query_text=query,
        iteration=current_iteration,
        results_count=len(result.get('items', [])),
        success=True
    )
```

### 중복 판단 기준

1. **Embedding 유사도 >0.95**: 거의 동일한 쿼리
2. **키워드 완전 일치**: 순서만 다른 경우

**예시:**

```python
query1 = "quantum error correction breakthrough 2026"
query2 = "quantum error correction 2026 breakthrough"

# Embedding 유사도: 0.98 → 중복!
```

### 전략 변경 (모두 중복 시)

```python
if not final_queries:
    print("⚠️ All queries duplicate. Changing search angle...")
    # Phase 1로 돌아가서 다른 각도로 재생성
```

**변경 옵션:**

| 현재 전략 | 변경 방향 |
|----------|----------|
| Academic (arxiv) | → Web (일반 검색) |
| Positive (지지 증거) | → Counter-evidence (반증) |
| Recent (2025-2026) | → Historical (고전 논문) |
| English | → Korean / Chinese |
| Broad keyword | → Specific niche |

**예시:**

```
Phase 3 결과: 5개 쿼리 모두 중복!

현재: "site:arxiv.org quantum error correction"
변경: "quantum error correction industry practical"

현재: "quantum computing breakthrough"
변경: "quantum computing failure case study"

→ 새 각도로 검색 재개
```

---

## Stop Hook과의 연계

### 역할 분담

| 구성 요소 | 역할 | 시점 |
|----------|------|------|
| **SKILL.md LOOP** | 재호출 결정 | OUTPUT 후 |
| **stop-hook.py** | 툴 호출 차단 | 매 턴 종료 시 |

### Stop Hook 동작

**파일:** `.claude/hooks/stop-hook.py`

**동작:**

1. state.json 읽기
2. Completion criteria 검증
3. `status != "running"` → `exit(0)` (툴 차단)
4. `status == "running"` → `allow` (계속 진행)

**예시:**

```python
# stop-hook.py (simplified)
state = json.load(open(".research/state.json"))

if state["status"] in ["completed", "paused", "stopped_by_user", "budget_exceeded"]:
    sys.exit(0)  # 툴 호출 차단 → 강제 종료

if state["iteration"]["current"] >= state["iteration"]["max"]:
    sys.exit(0)

if state["metrics"]["cost_estimate_usd"] > 10.0:
    sys.exit(0)

# 그 외: allow (계속 진행)
```

**효과:**

- LLM이 재호출을 시도해도 Hook이 최종 게이트키퍼
- 이중 보호로 안전성 확보

---

## 종합 예시

### 정상 진행 (Iteration 2)

```
OUTPUT 단계 완료
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Iteration #2 완료
🔍 이번 발견: ...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LOOP 단계 진입:

Step 1: state.json 읽기
- status: "running"
- current: 2
- max: 100
- budget: $0.25

Step 2: 종료 조건 체크
- status in ["completed", "paused", ...] → False
- current >= max → False (2 < 100)
- budget > 10.0 → False (0.25 < 10.0)

→ 종료 조건 불만족

Step 3: 다음 Iteration 호출
다음 iteration을 시작합니다...

Skill(skill="deep-research", args="")

→ Iteration 3 시작
```

### Loop Drift 감지 (Iteration 15)

```
PLAN 단계 Phase 3:

candidate_queries = [
  "quantum computing applications",
  "quantum computing use cases",
  "quantum computing practical"
]

중복 체크:
1. ⚠️ Skip "quantum computing applications" (>0.96 with iteration 12)
2. ⚠️ Skip "quantum computing use cases" (>0.97 with iteration 13)
3. ⚠️ Skip "quantum computing practical" (>0.95 with iteration 14)

→ final_queries = [] (모두 중복!)

⚠️ All queries duplicate. Changing search angle...

전략 변경:
- 현재: Web search, broad keywords
- 변경: Academic search, specific topics

새 쿼리:
1. "site:arxiv.org quantum error mitigation 2025"
2. "site:github.com qiskit variational quantum"
3. "quantum computing limitations counterexample"

→ 3개 새 쿼리로 EXECUTE 진행
```

### 종료 (Iteration 100)

```
OUTPUT 단계 완료
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Iteration #100 완료
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LOOP 단계 진입:

Step 1: state.json 읽기
- status: "running"
- current: 100
- max: 100
- budget: $8.50

Step 2: 종료 조건 체크
- current >= max → True (100 >= 100)

→ 종료 조건 만족

연구를 종료합니다. 최대 iteration에 도달했습니다.

Skill() 호출 없음 → 종료
```

---

## 자주 하는 실수

### ❌ 잘못된 예

1. **LLM이 주관적으로 종료**
   ```
   "충분한 정보를 얻었습니다. 연구를 종료합니다."
   → 절대 금지!
   ```

2. **종료 조건 체크 생략**
   ```
   OUTPUT 후 바로 Skill() 호출
   → state.json 체크 필수!
   ```

3. **중복 검색 방치**
   ```
   same query 5회 반복
   → deduplicate_search.py 사용 필수!
   ```

4. **Loop Drift 무시**
   ```
   새 정보 없는데 계속 같은 행동
   → 전략 변경 필수!
   ```

### ✅ 올바른 예

1. **Objective criteria만 확인**
   ```
   state.json 읽기 → status/iterations/budget 체크 → 결정
   ```

2. **철저한 중복 제거**
   ```
   Phase 3에서 is_duplicate_query() 호출
   모두 중복이면 전략 변경
   ```

3. **Loop Drift 적극 방지**
   ```
   3회 반복 → 전략 변경
   5회 새 정보 없음 → 접근법 변경
   ```

4. **Reflexion 활용**
   ```
   막힘 감지 → reflexion.json 참조 → 과거 성공 패턴 재사용
   ```

---

**LOOP 완료 → 다음 Iteration 시작 또는 종료**
