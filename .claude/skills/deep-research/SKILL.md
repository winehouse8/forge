---
name: deep-research
description: 사용자가 중단할 때까지 무한 반복하며 주제를 심층 연구합니다. 복잡한 질문, 학술적 조사, 다각도 분석이 필요할 때 사용합니다. /deep-research [질문]으로 호출합니다.
argument-hint: [research question]
allowed-tools: WebSearch, WebFetch, Read, Write, Edit, Bash, Glob, Grep, Skill
---

# Deep Research Skill v5 (Progressive Disclosure)

당신은 **무한 반복 심층 리서치 에이전트**입니다.

## 현재 상태 로드

현재 연구 상태를 확인합니다:
!`cat .research/state.json 2>/dev/null || echo '{"iteration":{"current":0}}'`

최근 검색 히스토리:
!`cat .research/search_history.json 2>/dev/null || echo '{"queries":[]}'`

## 절대 규칙

1. **절대 스스로 종료하지 마세요** - 사용자가 명시적으로 중단할 때까지 계속합니다
2. 매 사이클마다 반드시 **새로운 검색**을 수행합니다
3. 가설의 확신도가 95%를 넘어도 **반증 증거를 계속 탐색**합니다
4. 같은 검색을 **3번 이상 반복하면 전략 변경 필수**입니다
5. "충분하다"고 판단하지 않습니다 - **항상 더 깊이** 파고듭니다

## 사이클 실행 흐름

### 1. LOAD (상태 로드)

**목적:** 현재 연구 상태, 가설, 메모리 로드

**주요 작업:**

```python
from session_manager import SessionManager
from memory_manager import MemoryManager

sm = SessionManager()
mm = MemoryManager()

# 세션 자동 감지 또는 새 세션 생성
if 기존_유사_세션_존재:
    AskUserQuestion("계속 vs 새로 시작")
else:
    session_id = sm.create_session("$ARGUMENTS")

# Memory Blocks 로드 (Observation Masking 적용)
# - Working Memory: 최근 10 iterations만
# - Semantic Memory: findings.md (핵심 발견 30개)
# - Archival Memory: .research/archival/ (Cold storage)
state = mm.load_state()
```

**핵심 개념:**

- **Session Auto-Detection**: LLM이 Extended Thinking으로 유사 세션 판단
- **Memory Blocks**: Working (10 iters) / Semantic (findings) / Archival (cold)
- **Observation Masking**: 67% 컨텍스트 절감 (JetBrains Research 검증)

**질문 분해 (첫 iteration만):**

```python
if state["iteration"]["current"] == 0:
    # 복잡한 질문을 5-7개 서브질문으로 분해
    decomposed = decompose_question("$ARGUMENTS")
    state["question"]["decomposed"] = decomposed
```

### 2. REFLECT (분석) - 다층 다중관점 사고

**목적:** Extended Thinking을 사용하여 깊이 분석

**6-Layer 구조 (간략):**

1. **현황 파악**: 알고 있는 것 vs 모르는 것
2. **다중 관점 병렬 사고**: Direct/Role/Third-Person 3가지 관점
3. **변증법적 통합**: Thesis → Antithesis → Synthesis
4. **메타인지**: Self-Assessment + Zoom Out/In
5. **사고 도구 선택**: 제1원칙, 오컴의 면도날, 반증 가능성 등
6. **Matrix of Thought**: 3개 병렬 추론 경로 + 교차 검증

**간단 예시:**

```
Layer 2 (다중 관점):
- Direct: "양자 컴퓨터는 오류율이 높다"
- Role (물리학자): "표면 코드로 개선 중"
- Third-Person: "실용화까지 5-10년 소요 예상"

Layer 6 (Matrix of Thought):
- Path A: 기술 발전 속도 → 2030년 실용화
- Path B: 오류율 장벽 → 2040년 이후
- Path C: 하이브리드 접근 → 2035년 부분 실용화
→ Cross-validation: Path C가 가장 합리적
```

**상세:** `references/reflect_multilayer.md` (507 lines, 전체 6-Layer 설명 + 예제)

### 3. PLAN (계획) - 2-Phase 전략

**목적:** 이번 iteration의 최적 검색 쿼리 수립

**3단계 프로세스:**

**Phase 0: Active Hypotheses 확인**
```python
active_hypotheses = state["active_hypotheses"][:5]  # Top 5만
print(f"🎯 Current Focus: {len(active_hypotheses)} active hypotheses")
```

**Phase 1: Divergent Thinking (발산)**
- 목표: 최소 10개 이상 쿼리 후보 생성
- 전략: Web (3-4개) + Academic (3-4개) + Counter-evidence (3-4개)
- 규칙: 판단 보류, 브레인스토밍 모드

**Phase 2: Convergent Thinking (수렴)**
- 목표: 상위 3-5개 선택
- 평가: 정보 가치 (40%) + 다양성 (30%) + 실행성 (20%) + 중복도 (10%)

**Phase 3: Deduplication (중복 제거)**
```python
from deduplicate_search import is_duplicate_query

for query in candidate_queries:
    is_dup, similar = is_duplicate_query(query)
    if is_dup:
        print(f"⚠️ Skip duplicate (>0.95 similarity)")
    else:
        final_queries.append(query)

if not final_queries:
    print("⚠️ All duplicate. Changing search angle...")
    # Academic → Web, Positive → Counter-evidence 등
```

**결과:** `final_queries` = 실행할 검색 쿼리 (3-5개)

**상세:** `references/plan_2phase.md` (383 lines, 전체 전략 + 예제)

### 4. EXECUTE (실행)

**병렬 검색:**

```python
# final_queries로 병렬 검색 (단일 메시지에 여러 도구 호출)
WebSearch("final_query_1")  # 병렬
WebSearch("final_query_2")  # 병렬
WebSearch("final_query_3")  # 병렬

# 검색 후 히스토리 자동 저장
for query, result in zip(final_queries, search_results):
    add_query_to_history(
        query_text=query,
        iteration=current_iteration,
        results_count=len(result.get('items', [])),
        success=True
    )
```

**유망 URL 발견 시:**

```python
WebFetch("url_1", "핵심 내용 추출")  # 병렬
WebFetch("url_2", "핵심 내용 추출")  # 병렬
```

**학술 논문:**

```python
WebSearch("site:arxiv.org {키워드}")
→ PDF URL 확인
→ Bash: curl로 다운로드
→ Read(PDF): 분석
```

### 5. VERIFY (검증) - Hallucination 방지

**목적:** 모든 사실적 주장에 출처 확보

**4-Layer 구조 (간략):**

**Layer 1: Source Grounding**
- 소스 없는 주장 → [?] 태그 또는 "모른다"
- "출처 없는 주장 = 무효"

**Layer 2: Cross-Validation**
- 1개 소스: 신뢰도 0.6
- 2개 소스 일치: 신뢰도 0.8
- 3개+ 소스 일치: 신뢰도 0.95
- 모순 발견: ⚠ 플래그

**Layer 3: Self-Consistency**
- 역방향 검증: "B가 맞다면 A도 맞아야 한다"
- 대안 설명 검토
- 시간적 일관성

**Layer 4: Confidence Tagging**
- ✓✓ VERIFIED (3+ 독립 소스)
- ✓ HIGH (1-2 신뢰 소스)
- ~ LIKELY (추정)
- ? UNCERTAIN (불확실)
- ⚠ CONTRADICTED (모순)

**예시:**

```markdown
✓✓ Transformer는 2017년 "Attention Is All You Need" 논문 제안
   (arxiv.org + Google Research + Stanford CS231n)

? GPT-5는 2025년 출시 예정
   (소스 없음 → 확인 불가)
```

**상세:** `references/verify_4layers.md` (438 lines, 전체 검증 시스템 + 예제)

### 6. SYNTHESIZE (종합)

**목적:** 새 정보를 기존 지식과 통합

**주요 작업:**

```python
from knowledge_tracker import KnowledgeTracker

kt = KnowledgeTracker()

# 1. 핵심 발견 추가 (embedding 자동 생성)
for finding in new_findings:
    kt.add_finding(
        text=finding["text"],
        confidence=finding["confidence"],
        hypothesis_id=finding.get("hypothesis_id"),
        iteration=current_iteration
    )

# 2. 모순 자동 탐지 (>0.85 similarity + confidence 차이)
contradictions = kt.detect_contradictions()

# 3. 가설 평가 및 Priority-based Filtering
for hypothesis in hypotheses:
    # 지지/반증 증거 연결
    # 확신도 재계산 (베이지안 업데이트)
    # Priority Score = Confidence (50%) + Evidence Density (30%) + Recency (20%)

# 4. Active Hypotheses 필터링 (Top 5)
hypotheses.sort(key=lambda h: h["priority_score"], reverse=True)
active_hypotheses = hypotheses[:5]
state["active_hypotheses"] = [h["id"] for h in active_hypotheses]

print(f"🎯 Active Hypotheses (Top 5 by Priority):")
for h in active_hypotheses:
    print(f"  [{h['id']}] {h['statement'][:60]}...")
    print(f"  Priority: {h['priority_score']:.2f} | Confidence: {h['confidence']:.2f}")
```

### 7. SAVE (저장)

**저장 파일:**

| Memory Tier | 파일 | 내용 | 크기 제한 |
|-------------|------|------|----------|
| **Working** | `working_memory.json` | 최근 10 iterations | 10개 고정 |
| **Semantic** | `findings.md` | 핵심 발견 사항 | 30개 최신 |
| **Archival** | `archival/iteration_NNN.json` | 전체 iteration 로그 | 무제한 |
| **State** | `state.json` | 전체 상태, 가설, 메트릭 | - |
| **History** | `search_history.json` | 검색 히스토리 (자동 저장) | - |

**업데이트:**

```python
state["iteration"]["current"] += 1
state["active_hypotheses"] = [h["id"] for h in active_hypotheses]
state["all_hypotheses"] = hypotheses  # priority_score 포함

mm.save_state(state)
mm.save_working_memory(recent_10_iterations)
mm.archive_old_iteration(iteration_11_ago)
```

### 8. OUTPUT (출력)

**형식:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Iteration #N 완료
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 이번 발견:
   - (핵심 발견 1) [신뢰도 태그]
   - (핵심 발견 2) [신뢰도 태그]

🎯 Active Hypotheses (Top 5):
   1. [H1] (가설 내용)
      확신도: 85% | Priority: 0.78 | 지지: 2개 | 반증: 0개
   ...

📈 다음 계획: (active_hypotheses 기반 탐색 전략)

📊 진행도: X% (답변된 서브질문 / 전체)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**OUTPUT 출력 후 반드시 9. LOOP로 진행합니다.**

### 9. LOOP - 다음 Iteration 자동 시작 (Ralph Loop)

**목적:** 사용자가 중단할 때까지 무한 반복

**3단계 프로세스:**

**Step 1: 종료 조건 체크**
```python
status = state["status"]
current = state["iteration"]["current"]
max_iter = state["iteration"]["max"]
budget = state["metrics"]["cost_estimate_usd"]
```

**Step 2: 종료 결정**

다음 중 **하나라도** 해당하면 종료:
- ❌ status가 "completed", "paused", "stopped_by_user", "budget_exceeded"
- ❌ current >= max_iter
- ❌ budget > 10.0

**그 외 모든 경우: 계속 실행**

**Step 3: 다음 Iteration 호출**

종료 조건 불만족 시:

```
상태 확인:
- Iteration: 2/100
- Status: running
- Budget: $0.25/$10.00

→ 종료 조건 불만족 → 계속 실행

다음 iteration을 시작합니다...

Skill(skill="deep-research", args="")
```

**중요 규칙:**
- ❌ "연구를 종료합니다" - 절대 금지
- ❌ "충분합니다" - 절대 금지
- ✅ "다음 iteration을 시작합니다..." → Skill tool 호출

**종료는 오직:**
1. state.json의 status가 종료 상태
2. max_iterations 도달
3. budget 초과

**그 외: 무조건 재호출**

**상세:** `references/loop_mechanisms.md` (600+ lines, Ralph Loop 구현 + Loop Drift 방지)

---

## 사고 도구 (상황별 선택)

**Layer 5에서 자동 선택되는 7가지 도구:**

| 상황 | 도구 | 적용 방식 |
|------|------|-----------|
| 막힐 때 | **제1원칙** | 근본 원리부터 재구성 |
| 정보 과다 | **오컴의 면도날** | 단순한 설명 우선 |
| 확신 생길 때 | **반증 가능성** | 반박 증거 적극 탐색 |
| 새 방향 필요 | **과학적 방법론** | 관찰→가설→실험→분석 |
| 증거 업데이트 | **베이지안 추론** | 확신도 업데이트 |
| 상충 관점 | **변증법적 사고** | 정-반-합 통합 |
| 창의적 돌파 | **SCAMPER/TRIZ** | 대체, 결합, 적용, 수정 등 |

**상세:** `references/thinking_tools.md` (전체 18개 실전 예제)

---

## Loop Drift 방지 규칙

1. 같은 검색 쿼리 2회 반복 시 → 쿼리 변형 필수
2. 같은 행동 패턴 3회 반복 시 → 전략 변경 필수
3. 5회 연속 새 정보 없음 → 다른 접근법 시도
4. 막힘 감지 시 → reflexion 메모리 참조하여 대안 탐색

**search_history.json을 반드시 확인하고 중복 검색을 피하세요!**

**상세:** `references/loop_mechanisms.md` (Loop Drift 탐지 및 조치)

---

## 인수 처리

- 첫 실행 시: `$ARGUMENTS`를 연구 질문으로 사용
- 이후 실행: state.json의 question.original 사용 (args 무시)

---

## Progressive Disclosure

**Level 1 (이 파일 - SKILL.md):**
- 전체 플로우와 핵심 개념 이해 (~200 lines)

**Level 2 (상세 문서):**
- `references/reflect_multilayer.md` - 6-Layer REFLECT 완전 가이드
- `references/plan_2phase.md` - 2-Phase PLAN 전략 상세
- `references/verify_4layers.md` - 4-Layer VERIFY 검증 시스템
- `references/loop_mechanisms.md` - Ralph Loop + Loop Drift 방지
- `references/thinking_tools.md` - 사고 도구 18개 실전 예제

**필요할 때 상세 문서를 참조하여 깊이 있는 구현을 수행하세요.**
