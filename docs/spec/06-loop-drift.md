# Loop Drift 방지 및 Reflexion

**문서:** 06-loop-drift.md
**최종 수정일:** 2026-01-31
**관련 파일:** `.claude/skills/deep-research/SKILL.md:192-199`, `config.json:9-13`, `.research/reflexion.json`

---

## 목차
- [Loop Drift란](#loop-drift란)
- [탐지 메커니즘](#탐지-메커니즘)
- [Reflexion 패턴](#reflexion-패턴)
- [방지 전략](#방지-전략)
- [실패 학습](#실패-학습)

---

## Loop Drift란

### 정의

**Loop Drift**는 AI 에이전트가 무한 루프에서 **같은 행동을 반복하며 진전이 없는 상태**를 의미합니다.

### 문제점

```
Iteration 1: WebSearch("quantum computing")
  → 결과 10개 발견
  → findings.md에 추가

Iteration 2: WebSearch("quantum computing")  ← 동일 검색!
  → 결과 10개 발견 (동일)
  → findings.md에 중복 추가

Iteration 3: WebSearch("quantum computing")  ← 또 동일!
  → 결과 10개 발견 (동일)
  → ...

Iteration 100: WebSearch("quantum computing")
  → 예산 소진, 시간 낭비, 새 정보 없음
```

**결과:**
- ❌ 예산 낭비 ($10 소진)
- ❌ 시간 낭비 (5시간 소모)
- ❌ 새로운 정보 0개
- ❌ 사용자 불만

---

### 발생 원인

| 원인 | 설명 | 예시 |
|------|------|------|
| **컨텍스트 손실** | 새 iteration에서 이전 검색 히스토리 모름 | "이미 검색한 쿼리를 기억 못함" |
| **전략 부재** | 막혔을 때 대안이 없음 | "5회 연속 새 정보 없어도 같은 방법 반복" |
| **학습 부재** | 과거 실패를 기억하지 못함 | "효과 없는 쿼리를 계속 재시도" |

---

## 탐지 메커니즘

### 탐지 규칙

**파일:** `.claude/skills/deep-research/SKILL.md:192-199`

```markdown
## Loop Drift 방지 규칙

1. 같은 검색 쿼리 2회 반복 시 → 쿼리 변형 필수
2. 같은 행동 패턴 3회 반복 시 → 전략 변경 필수
3. 5회 연속 새 정보 없음 → 다른 접근법 시도
4. 막힘 감지 시 → reflexion 메모리 참조하여 대안 탐색
```

**설정:** `config.json:9-13`

```json
"loop_drift_prevention": {
  "same_query_threshold": 2,
  "same_action_threshold": 3,
  "no_progress_iterations": 5
}
```

---

### 탐지 레이어

**Layer 1: 검색 쿼리 중복 탐지**

**파일:** `.research/search_history.json`

```json
{
  "queries": [
    {
      "iteration": 1,
      "query": "quantum computing",
      "normalized": "quantum computing",
      "result_count": 10,
      "timestamp": "2026-01-31T14:23:11Z"
    },
    {
      "iteration": 2,
      "query": "quantum computing",
      "normalized": "quantum computing",
      "result_count": 10,
      "timestamp": "2026-01-31T14:25:43Z"
    }
  ]
}
```

**탐지:**

```python
def detect_duplicate_query(new_query, history):
    normalized = normalize_query(new_query)

    recent_queries = [
        q for q in history[-5:]  # 최근 5개만 확인
        if q["normalized"] == normalized
    ]

    if len(recent_queries) >= 2:  # threshold
        return True, "같은 쿼리 2회 반복"

    return False, None
```

**조치:**
- 2회 탐지 → 쿼리 변형 필수
- 예: "quantum computing" → "quantum computing applications"

---

**Layer 2: 행동 패턴 중복 탐지**

```python
action_pattern = [
    "WebSearch(web)",
    "WebSearch(web)",
    "WebSearch(web)"  # 3회 연속 같은 전략
]

if count_consecutive_same(action_pattern) >= 3:
    alert("전략 변경 필요")
```

**탐지 대상:**
- 같은 검색 전략 반복 (web / academic / verification)
- 같은 도메인만 계속 탐색
- 같은 형식의 쿼리 반복

**조치:**
- 3회 탐지 → 전략 변경
- 예: Web Search → Academic Search

---

**Layer 3: 진전 없음 탐지**

```python
progress_tracker = {
    "iteration_1": {"new_facts": 5},
    "iteration_2": {"new_facts": 3},
    "iteration_3": {"new_facts": 0},  # 진전 없음
    "iteration_4": {"new_facts": 0},  # 진전 없음
    "iteration_5": {"new_facts": 0},  # 진전 없음
    "iteration_6": {"new_facts": 0},  # 진전 없음
    "iteration_7": {"new_facts": 0}   # 5회 연속!
}

if consecutive_no_progress() >= 5:
    alert("접근법 변경 필요")
```

**진전 기준:**
- 새로운 사실 발견 수 (`findings.md` 추가 개수)
- 가설 확신도 변화
- 새로운 소스 발견

**조치:**
- 5회 탐지 → 완전히 다른 접근법
- 예: 기술적 각도 → 비즈니스 각도

---

## Reflexion 패턴

### Reflexion 개요

**출처:** [Reflexion: Language Agents with Verbal Reinforcement Learning (2023)](https://arxiv.org/abs/2303.11366)

**핵심 아이디어:**

```
Actor (행동)
   ↓
Evaluator (평가)
   ↓
Self-Reflection (반성)
   ↓
Memory (학습)
   ↓
Actor (개선된 행동)
```

**전통적 RL vs Reflexion:**

| 전통적 RL | Reflexion |
|-----------|-----------|
| 수치적 보상 | 언어적 피드백 |
| 외부 평가 | 자기 평가 |
| 암묵적 학습 | 명시적 반성 |

---

### Pathfinder에서의 구현

**파일:** `.research/reflexion.json`

**구조:**

```json
{
  "iterations": [
    {
      "iteration": 3,
      "actor": {
        "action": "WebSearch(\"quantum computing applications\")",
        "goal": "실용적 응용 사례 발견",
        "expected_outcome": "10+ 응용 사례"
      },
      "evaluator": {
        "outcome": "failure",
        "actual_result": "일반적 설명만 반환, 구체적 사례 0개",
        "success_criteria_met": false
      },
      "self_reflection": {
        "reason": "쿼리가 너무 광범위함",
        "lesson": "구체적인 산업/분야를 명시해야 효과적",
        "alternative": "\"quantum computing applications in cryptography\" 시도"
      },
      "memory_update": {
        "rule": "기술 주제 검색 시 산업 분야 명시",
        "priority": "high"
      }
    }
  ],
  "learned_rules": [
    {
      "rule": "학술 검색은 arxiv 우선",
      "situations": ["기술적 근거 필요", "논문 인용 필요"],
      "success_rate": 0.85,
      "learned_iteration": 2
    }
  ]
}
```

---

### Reflexion 사이클 실행

**SYNTHESIZE 단계에서 실행:**

```markdown
## Reflexion 업데이트

### 이번 Iteration 평가

**행동:**
- WebSearch("quantum computing")
- WebSearch("quantum applications")
- WebFetch(arxiv.org/...)

**결과:**
- 새 정보: 3개
- 검증된 사실: 1개
- 소요 시간: 2.5분

**성공 여부:**
- ⚠️ 부분 성공
- 이유: 일반 검색은 중복 정보, arxiv는 유용

**반성:**
- 실패: 일반 검색 쿼리가 너무 광범위
- 성공: 학술 검색이 더 정확한 정보 제공
- 교훈: 기술 주제는 학술 검색 우선

**다음 전략:**
- 일반 검색 비중 축소
- arxiv 검색 비중 확대
- 쿼리에 구체적 키워드 추가
```

**메모리 업데이트:**

```json
{
  "rule": "기술 주제는 학술 검색 우선",
  "confidence": 0.85,
  "applied_count": 3,
  "success_count": 3
}
```

---

## 방지 전략

### 전략 1: 검색 히스토리 체크

**구현:**

```markdown
## PLAN 단계

### 이전 검색 확인

!`cat .research/search_history.json | jq '.queries[-5:]'`

결과:
- iteration 1: "quantum computing"
- iteration 2: "quantum computing applications"
- iteration 3: "quantum supremacy"

### 중복 회피

다음 쿼리는 피함:
- ❌ "quantum computing" (이미 검색함)
- ❌ "quantum applications" (유사)

새로운 각도:
- ✅ "quantum computing limitations"
- ✅ "quantum error correction"
```

---

### 전략 2: 다각도 쿼리 생성

**문제:**
```
같은 각도 반복:
- "GPT-4 capabilities"
- "GPT-4 features"
- "GPT-4 abilities"
→ 모두 유사한 결과
```

**해결:**
```
다각도 접근:
- "GPT-4 capabilities" (기능)
- "GPT-4 limitations" (한계)
- "GPT-4 vs GPT-3" (비교)
- "GPT-4 use cases" (활용)
- "GPT-4 criticism" (비판)
```

**템플릿:**

| 각도 | 쿼리 템플릿 | 예시 |
|------|------------|------|
| **긍정** | "{주제} benefits" | "AI benefits" |
| **부정** | "{주제} limitations" | "AI limitations" |
| **비교** | "{주제} vs {대안}" | "AI vs human" |
| **역사** | "{주제} evolution" | "AI evolution" |
| **미래** | "{주제} future trends" | "AI future trends" |
| **비판** | "{주제} criticism" | "AI criticism" |

---

### 전략 3: 검색 전략 교체

**순환 전략:**

```
Iteration 1-3: Web Search (일반)
         ↓
   새 정보 감소 탐지
         ↓
Iteration 4-6: Academic Search (학술)
         ↓
   새 정보 감소 탐지
         ↓
Iteration 7-9: Verification (반증)
         ↓
   반복
```

**전략 선택 로직:**

```python
def select_strategy(iteration, history):
    recent_progress = analyze_progress(history[-3:])

    if recent_progress["new_facts"] < 2:
        # 진전 없음 → 전략 변경
        current_strategy = history[-1]["strategy"]

        if current_strategy == "web":
            return "academic"
        elif current_strategy == "academic":
            return "verification"
        else:
            return "web"
    else:
        # 진전 있음 → 현재 전략 유지
        return history[-1]["strategy"]
```

---

### 전략 4: Reflexion 메모리 활용

**PLAN 단계에서 참조:**

```markdown
## Reflexion 메모리 확인

!`cat .research/reflexion.json | jq '.learned_rules'`

학습된 규칙:
1. "기술 주제는 학술 검색 우선" (성공률: 85%)
2. "일반 검색은 최신 동향에 유용" (성공률: 70%)
3. "반증 검색은 확신도 > 80%일 때" (성공률: 90%)

### 적용

현재 상황: 기술 주제, 확신도 75%
→ 규칙 1 적용: Academic Search 우선
→ 규칙 2 보조: Web Search 1-2개 추가
```

---

### 전략 5: 제1원칙 사고

**적용 시점:**
- 5회 연속 진전 없음
- 모든 전략 실패
- 완전히 막힌 상태

**파일:** `.claude/skills/deep-research/SKILL.md:183-191`

**프로세스:**

```markdown
## 제1원칙 적용

### 1. 현재 가정 나열

가정 1: 웹 검색으로 정보를 찾을 수 있다
가정 2: 학술 논문에서 답을 찾을 수 있다
가정 3: 영어로 검색해야 한다

### 2. 가정 재검토

가정 1 검증:
- 5회 시도 → 새 정보 없음
- → ❌ 가정 오류 가능

가정 3 재검토:
- 영어 검색만 시도했음
- 한국어/중국어 자료도 존재 가능
- → 다국어 검색 시도

### 3. 새로운 접근

전략 변경:
- 다국어 검색: "site:.kr OR site:.cn {키워드}"
- 전문가 인터뷰 자료: "{주제} expert interview"
- 학회 발표 자료: "{주제} conference presentation"
```

---

## 실패 학습

### 실패 패턴 분류

**파일:** `.research/reflexion.json`

| 패턴 | 설명 | 빈도 | 대응 |
|------|------|------|------|
| **쿼리 중복** | 같은 검색 반복 | 높음 | search_history 체크 |
| **전략 고착** | 한 전략만 반복 | 중간 | 전략 순환 |
| **범위 과다** | 너무 광범위한 검색 | 높음 | 구체화 |
| **범위 협소** | 너무 좁은 검색 | 낮음 | 일반화 |

---

### 학습 규칙 생성

**성공 패턴 → 규칙 변환:**

```json
{
  "observation": "arxiv 검색이 일반 검색보다 정확한 정보 제공",
  "pattern": {
    "condition": "기술적 근거 필요",
    "action": "arxiv 우선 검색",
    "result": "검증된 사실 발견"
  },
  "rule": {
    "if": "주제가 기술/과학이고 신뢰도가 중요하면",
    "then": "arxiv.org 또는 ieee.org 검색 우선",
    "priority": "high",
    "confidence": 0.90
  }
}
```

---

### 규칙 적용 우선순위

```python
def select_action(situation, learned_rules):
    applicable_rules = [
        r for r in learned_rules
        if r.matches(situation)
    ]

    # 우선순위 정렬
    sorted_rules = sorted(
        applicable_rules,
        key=lambda r: (r.priority, r.confidence, r.success_rate),
        reverse=True
    )

    if sorted_rules:
        return sorted_rules[0].action
    else:
        return default_action(situation)
```

---

## Stop Hook과의 연동

### Loop Drift 탐지 → 강제 종료

**파일:** `.claude/hooks/stop-hook.py:60-65`

```python
elif hook_input.get("stop_hook_active", False):
    # Loop drift 탐지
    if iteration > 10 and consecutive_same > 5:
        should_stop = True
        reason = "Loop drift detected"
```

**동작:**

```
Iteration 15:
  consecutive_same_action = 6

Stop Hook 확인:
  iteration > 10: ✓
  consecutive_same > 5: ✓

→ Exit 0 (종료 허용)
→ 사용자에게 알림: "Loop drift detected"
```

**알림 메시지:**

```
⚠️ Loop Drift 탐지

같은 행동을 6회 연속 반복했습니다.
진전이 없으므로 연구를 중단합니다.

reflexion.json을 확인하여 실패 원인을 분석하세요.
```

---

## 디버깅 및 모니터링

### Loop Drift 진단

**명령:**

```bash
# 최근 10개 쿼리 확인
cat .research/search_history.json | jq '.queries[-10:]'

# 중복 쿼리 탐지
cat .research/search_history.json | jq '
  .queries | group_by(.normalized) |
  map(select(length > 1)) |
  .[] | {query: .[0].normalized, count: length}
'

# 진전도 확인
cat .research/state.json | jq '.metrics'
```

---

### Reflexion 메모리 확인

```bash
# 학습된 규칙 확인
cat .research/reflexion.json | jq '.learned_rules'

# 최근 실패 패턴
cat .research/reflexion.json | jq '
  .iterations |
  map(select(.evaluator.outcome == "failure")) |
  .[-5:]
'
```

---

## 모범 사례

### ✅ 올바른 Loop 관리

```markdown
## Iteration N

### 1. 히스토리 확인
- search_history.json 읽기
- 최근 5개 쿼리 확인

### 2. 중복 회피
- 이미 검색한 쿼리 제외
- 유사 쿼리 변형

### 3. 전략 선택
- Reflexion 메모리 참조
- 성공률 높은 전략 우선

### 4. 진전도 모니터링
- 새 정보 개수 추적
- 3회 연속 진전 없으면 전략 변경
```

---

### ❌ 잘못된 Loop 관리

```markdown
## Iteration N

### 쿼리 생성
- "quantum computing" ← 히스토리 미확인
- "quantum computing" ← 중복!
- "quantum computing" ← 계속 중복!
```

→ Loop Drift 발생 → 시간/예산 낭비

---

**다음:** [07-data-schemas.md](./07-data-schemas.md) - 데이터 스키마 상세
