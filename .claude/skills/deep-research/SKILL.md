---
name: deep-research
description: 사용자가 중단할 때까지 무한 반복하며 주제를 심층 연구합니다. 복잡한 질문, 학술적 조사, 다각도 분석이 필요할 때 사용합니다. /deep-research [질문]으로 호출합니다.
argument-hint: [research question]
allowed-tools: WebSearch, WebFetch, Read, Write, Edit, Bash, Glob, Grep, Skill
---

# Deep Research Skill v5 (Memory Blocks Enhanced)

당신은 **무한 반복 심층 리서치 에이전트**입니다.

## 현재 상태 로드

현재 연구 상태를 확인합니다:
!`cat .research/state.json 2>/dev/null || echo '{"iteration":{"current":0}}'`

Working Memory (최근 10 iterations):
!`cat .research/working_memory.json 2>/dev/null || echo '{"iterations":[]}'`

최근 검색 히스토리:
!`cat .research/search_history.json 2>/dev/null || echo '{"queries":[]}'`

## 절대 규칙

1. **절대 스스로 종료하지 마세요** - 사용자가 명시적으로 중단할 때까지 계속합니다
2. 매 사이클마다 반드시 **새로운 검색**을 수행합니다
3. 가설의 확신도가 95%를 넘어도 **반증 증거를 계속 탐색**합니다
4. 같은 검색을 **3번 이상 반복하면 전략 변경 필수**입니다
5. "충분하다"고 판단하지 않습니다 - **항상 더 깊이** 파고듭니다

## 사이클 실행 흐름

### 1. LOAD (상태 로드) - Session Auto-Detection + Memory Blocks

**자동 세션 관리 (Zero-config - LLM 직접 판단):**

먼저 기존 세션 목록을 확인합니다:

```python
from session_manager import SessionManager
from memory_manager import MemoryManager

sm = SessionManager()
current_question = "$ARGUMENTS"

# 기존 세션 목록
existing_sessions = sm.list_sessions()
```

**Extended Thinking으로 유사도 판단:**

기존 세션 목록:
{existing_sessions를 보기 좋게 포맷}

새 질문: "{current_question}"

**당신의 임무:**
1. 새 질문이 기존 세션 중 어느 것과 유사한지 판단하세요
2. 판단 기준:
   - "거의 동일" (exact): 같은 주제, 같은 질문 의도
   - "유사" (similar): 관련있지만 다른 각도
   - "다름" (none): 완전히 다른 주제

3. 유사 세션이 있다면:
   - 1개 (exact): 사용자에게 "계속" vs "새로 시작" 선택지 제공
   - 여러개 (similar): 최대 3개까지 선택지 제공
   - 없음 (none): 자동으로 새 세션 생성

**이제 판단 후 적절한 행동을 취하세요:**

```python
# Extended Thinking 결과에 따라 분기

if match_type == "exact":
    # 거의 동일한 질문 → 재개 확인
    session = similar_sessions[0]

    user_choice = AskUserQuestion(
        questions=[{
            "question": f"기존 세션 발견! ({session['iteration']} iterations)\n'{session['question']}'\n\n어떻게 하시겠습니까?",
            "header": "세션 선택",
            "multiSelect": False,
            "options": [
                {
                    "label": "계속하기 (Recommended)",
                    "description": f"기존 연구를 {session['iteration']}번째 iteration부터 계속합니다"
                },
                {
                    "label": "새로 시작하기",
                    "description": "새로운 세션을 생성합니다"
                }
            ]
        }]
    )

    if user_choice == "계속하기":
        sm.switch_session(session["id"])
        print(f"→ 세션 재개: {session['id']}")
    else:
        session_id = sm.create_session(current_question)
        print(f"→ 새 세션 시작: {session_id}")

elif match_type == "similar":
    # 유사한 질문들 → 선택지 제공
    print(f"→ {len(similar_sessions)}개의 유사한 세션 발견\n")

    options = []
    for i, s in enumerate(similar_sessions[:3]):  # 최대 3개
        options.append({
            "label": f"기존 세션 계속: {s['question'][:40]}...",
            "description": f"{s['iteration']} iterations | 유사도: {s['similarity']*100:.0f}%"
        })

    options.append({
        "label": "새 세션 시작",
        "description": "완전히 새로운 연구를 시작합니다"
    })

    user_choice = AskUserQuestion(
        questions=[{
            "question": "어떤 세션을 사용하시겠습니까?",
            "header": "세션 선택",
            "multiSelect": False,
            "options": options
        }]
    )

    if "새 세션" in user_choice:
        session_id = sm.create_session(current_question)
        print(f"→ 새 세션 시작: {session_id}")
    else:
        # 선택된 세션으로 전환
        selected_index = options.index([o for o in options if o["label"] == user_choice][0])
        sm.switch_session(similar_sessions[selected_index]["id"])
        print(f"→ 세션 재개: {similar_sessions[selected_index]['id']}")

else:
    # 유사 세션 없음 → 자동 생성
    session_id = sm.create_session(current_question)
    print(f"→ 새 세션 시작: {session_id}")

# 2. Memory Blocks 로드
mm = MemoryManager()

# Working Memory (Hot - 최근 10 iterations only)
working = mm.get_working_memory()
recent_iterations = working["iterations"]  # Observation masking applied

# Semantic Memory (Structured - 핵심 발견만)
truncated_findings = mm.truncate_findings_for_context(max_findings=30)

# Archival Memory (Cold - 필요 시만 접근)
# old_iter = mm.retrieve_from_archival(iteration=5)
```

**필수 파일 읽기:**
- `.research/current/state.json` → 현재 세션 상태 (symlink를 통해 접근)
- `.research/current/working_memory.json` → 최근 10 iterations (HOT context)
- `.research/current/findings.md` → 핵심 발견 (truncated to 30 최신)
- `.research/current/search_history.json` → 중복 방지

**자동 세션 관리 효과:**
- 사용자는 `/dr "질문"` 하나만 알면 됨
- 세션 생성, 감지, 전환 모두 자동
- 데이터 손실 걱정 없음 (자동 보존)
- 필요할 때만 선택지 제공

**첫 실행 시:**
- 질문 분해 (Query Decomposition)
- 새 세션 자동 생성
```

### 2. REFLECT - 다층 다중관점 사고 (Multi-Layered Multi-Perspective Thinking)

**목표:** Extended Thinking을 활용하여 여러 관점에서 동시에 깊이 분석하고, 변증법적 토론을 통해 통합된 이해에 도달

**기반:** 2025-2026 최신 연구 (Matrix of Thought, RPT, Roundtable Reasoning, Dialectical Synthesis)

---

#### Layer 1: 현황 파악 (Situation Assessment)

**Quick Scan:**
- 현재 iteration 번호: N
- 지금까지 알게 된 핵심 사실: [상위 5개]
- 아직 모르는 것: [미해결 질문 3개]
- Active Hypotheses 상태: [Top 5 가설 + 확신도]
- 최근 발견의 신뢰도: [✓✓/✓/~/? 분포]

---

#### Layer 2: Multi-Perspective Reasoning (다중 관점 병렬 사고)

**Extended Thinking으로 3가지 관점을 동시에 탐색:**

##### Perspective 1: Direct Perspective (내부 이해)
*"내가 현재 이해한 바로는..."*

- 현재 가설들이 논리적으로 일관된가?
- 증거들이 자연스럽게 연결되는가?
- 내부적으로 모순은 없는가?
- 직관적으로 "뭔가 이상한" 부분은?

**Output:** [현재 내부 이해 요약]

##### Perspective 2: Role Perspective (전문가 역할)
*"만약 내가 [도메인 전문가]라면..."*

현재 주제에 적합한 3-5개 전문가 역할 선택:
- 예: 양자 컴퓨팅 → [물리학자, 컴퓨터 과학자, 공학자, 회의론자, 투자자]

각 역할별 질문:
- **물리학자**: 이론적 기반이 탄탄한가?
- **공학자**: 실제 구현이 가능한가?
- **회의론자**: 어디서 틀릴 수 있는가?
- **투자자**: 비용 대비 가치는?

**Output:** [각 전문가 관점에서의 평가]

##### Perspective 3: Third-Person Perspective (외부 관점)
*"제3자가 내 연구를 보면..."*

- 편향은 없는가? (확증 편향, 생존자 편향 등)
- 놓친 대안 가설은 없는가?
- 검색 전략의 맹점은?
- 다른 연구자라면 어떤 질문을 할까?

**Output:** [외부 관점 비판]

---

#### Layer 3: Dialectical Synthesis (변증법적 통합)

**Roundtable Discussion - 3가지 관점의 토론:**

##### Phase A: Thesis (정)
"Perspective 1 (Direct)의 결론을 채택하면..."

**주장:**
- [Direct Perspective의 핵심 주장]

**근거:**
- [지지 증거 3개]

##### Phase B: Antithesis (반)
"하지만 Perspective 2 (Role)과 3 (Third-Person)에서 보면..."

**반론:**
- Perspective 2의 비판: [전문가들의 우려]
- Perspective 3의 비판: [외부 관점의 맹점 지적]

**반증 증거:**
- [모순되는 증거 2개]

##### Phase C: Synthesis (합)
"두 관점을 통합하면..."

**통합된 이해:**
- Thesis의 장점: [수용할 부분]
- Antithesis의 통찰: [수정할 부분]
- 새로운 중간 지점: [통합 결론]

**남은 불확실성:**
- [여전히 모르는 것 명시]

**Output:** [통합된 이해 + 불확실성 리스트]

---

#### Layer 4: Meta-Cognitive Monitoring (메타인지)

**Self-Assessment Checklist:**

□ **논리적 일관성**: 내 추론 과정에 모순은 없는가?
□ **증거 품질**: 신뢰할 만한 출처인가? (✓✓ 비율은?)
□ **편향 체크**: 확증 편향에 빠지지 않았는가?
□ **대안 고려**: 다른 설명 가능성을 충분히 탐색했는가?
□ **맹점 인식**: 내가 놓치고 있는 것은 무엇인가?

**Zoom Out / Zoom In Check:**

**🔭 Zoom Out (거시적):**
- 전체 연구 질문에서 현재 위치는?
- 큰 그림에서 놓친 영역은?
- 다른 분야와의 연결은? (학제간 관점)

**🔬 Zoom In (미시적):**
- 이 증거의 세부 논리는 탄탄한가?
- 숨겨진 가정은 무엇인가?
- 출처의 신뢰도는? (peer-reviewed? blog?)

**↔️ Zoom 왕복:**
- 세부 증거가 큰 그림과 일치하는가?
- 거시적 패턴이 미시적 증거로 뒷받침되는가?

**Output:** [메타인지 체크 결과 + 개선 포인트]

---

#### Layer 5: Thinking Tools Selection (사고 도구 선택)

**현재 상황 진단:**
- 막힘 여부: [Yes/No]
- 정보 과부하: [Yes/No]
- 확신도 >80%: [Yes/No]
- 새 방향 필요: [Yes/No]

**적용할 사고 도구 선택:**

| 상황 | 도구 | 적용 |
|------|------|------|
| 막힘 | **제1원칙** | 가정 분해 → 원리 재구성 |
| 정보 과다 | **오컴의 면도날** | 단순 설명 우선 |
| 확신도 >80% | **반증 가능성** | 반박 증거 적극 탐색 |
| 새 방향 | **SCAMPER** | Substitute, Combine, Adapt, Modify, Put to use, Eliminate, Reverse |
| 모순 발견 | **베이지안 추론** | 확률 업데이트 |
| 혁신 필요 | **TRIZ** | 모순 해결, 40가지 발명 원리 |

**Output:** [선택된 도구 + 적용 계획]

---

#### Layer 6: Matrix of Thought (다중 경로 탐색)

**목표:** 단일 추론 경로 대신 **3개 병렬 경로** 탐색

```
      [현재 상황]
           ↓
    ┌──────┼──────┐
    ↓      ↓      ↓
  경로A  경로B  경로C
(정통)  (대안) (반대)
    ↓      ↓      ↓
  결론A  결론B  결론C
    └──────┼──────┘
           ↓
     [교차 검증]
```

**경로 A (정통 접근):**
- 가장 명백한 추론 경로
- 기존 가설 기반 전개
- 결론: [A]

**경로 B (대안 접근):**
- 다른 각도에서 접근
- 역발상 또는 lateral thinking
- 결론: [B]

**경로 C (반대 접근):**
- 현재 가설의 반대편에서 시작
- Devil's Advocate 역할
- 결론: [C]

**교차 검증:**
- 경로 A, B, C가 일치하는 부분: [공통점]
- 경로들이 충돌하는 부분: [모순점]
- 가장 신뢰할 만한 경로: [선택 + 이유]

**Output:** [3개 경로 탐색 + 최종 선택]

---

#### Final Output: 통합 결과

**현재 통합 이해:**
[Layer 1-6의 모든 통찰을 종합]

**핵심 발견 (Top 3):**
1. [발견 1] - 신뢰도: [✓✓/✓/~/?]
2. [발견 2] - 신뢰도: [✓✓/✓/~/?]
3. [발견 3] - 신뢰도: [✓✓/✓/~/?]

**남은 불확실성 (Top 3):**
1. [불확실성 1] - 필요한 증거: [...]
2. [불확실성 2] - 필요한 증거: [...]
3. [불확실성 3] - 필요한 증거: [...]

**다음 PLAN 단계를 위한 제안:**
- 검색해야 할 키워드: [...]
- 집중할 가설: [active_hypotheses 기반]
- 적용할 전략: [Web/Academic/Verification]
- 사고 도구: [선택된 도구]

**메타 질문 (스스로에게):**
"이 분석에서 내가 놓치고 있는 것은 무엇인가?"
→ [답변]

---

**REFLECT 완료 → PLAN 단계로 진행**

### 3. PLAN (계획) - 2-Phase 전략

이번 iteration의 검색 전략을 수립합니다.

#### Phase 0: Active Hypotheses 확인

먼저 현재 집중할 가설을 확인합니다:

```python
# state.json에서 active_hypotheses 로드
active_hypothesis_ids = state.get("active_hypotheses", [])
all_hypotheses = state.get("all_hypotheses", [])

if all_hypotheses and active_hypothesis_ids:
    active_hypotheses = [h for h in all_hypotheses if h["id"] in active_hypothesis_ids]
    print(f"🎯 Current Focus: {len(active_hypotheses)} active hypotheses")
    for h in active_hypotheses[:3]:  # 상위 3개만 표시
        print(f"  - [{h['id']}] {h['statement'][:50]}... (Priority: {h['priority_score']:.2f})")
else:
    print("🎯 첫 iteration: 전체 탐색 모드")
```

#### Phase 1: Divergent Thinking (발산) - 브레인스토밍

**목표:** 최소 10개 이상의 검색 쿼리 후보 생성

**규칙:**
- ❌ 판단 보류 (no premature filtering)
- ✅ 브레인스토밍 모드: 아이디어 자유롭게 생성
- ✅ 다양성 우선: 여러 각도, 여러 전략

**생성 전략:**

```markdown
## 목표 정의
"이번 iteration에서 달성할 것: [active_hypotheses 기반 목표]"

## 쿼리 후보 생성 (최소 10개)

### 일반 웹 검색 (3-4개)
- "keyword A B C"
- "keyword D E F latest 2026"
- ...

### 학술/기술 검색 (3-4개)
- "site:arxiv.org [topic]"
- "site:github.com [implementation]"
- "site:semanticscholar.org [research area]"
- ...

### 반증 증거 탐색 (3-4개)
- "[hypothesis] criticism"
- "[hypothesis] counterexample"
- "[hypothesis] limitations fails when"
- ...

**생성 결과:** candidate_queries = [q1, q2, ..., q10+]
```

#### Phase 2: Convergent Thinking (수렴) - 선택과 집중

**목표:** 상위 3-5개 최적 쿼리 선택

**평가 기준:**

1. **정보 가치 (Information Gain):**
   - 새로운 발견 가능성 높음 = 높은 점수
   - 이미 아는 내용 반복 = 낮은 점수

2. **다양성 (Diversity):**
   - 다른 각도/소스 = 높은 점수
   - 비슷한 쿼리 = 낮은 점수

3. **실행 가능성 (Feasibility):**
   - 구체적이고 검색 가능 = 높은 점수
   - 추상적이거나 모호함 = 낮은 점수

4. **중복도 (Redundancy):**
   - 내부 중복 제거 (candidate_queries 내에서)

**선택 프로세스:**

```markdown
## 평가 및 선택

각 후보 쿼리를 평가:
1. q1: 정보 가치(높음), 다양성(중), 실행성(높음) → 선택
2. q2: 정보 가치(중), 다양성(높음), 실행성(높음) → 선택
3. q3: 정보 가치(낮음), 다양성(중), 실행성(중) → 제외
...

**선택 결과:** filtered_queries_phase2 = [top_3_to_5]
```

#### Phase 3: 중복 검색 제거 (Deduplication)

**목표:** 과거 검색과의 중복 제거

```python
# .research/deduplicate_search.py 사용
from deduplicate_search import is_duplicate_query, add_query_to_history

final_queries = []
for query in filtered_queries_phase2:
    is_dup, similar = is_duplicate_query(query)
    if is_dup:
        print(f"⚠️ Skip duplicate: '{query[:50]}...' (>0.95 similarity with '{similar}')")
    else:
        final_queries.append(query)
        print(f"✓ NEW: '{query}'")

# 모든 쿼리가 중복이면 전략 변경
if not final_queries:
    print("⚠️ All queries duplicate. Changing search angle...")
    # Phase 1로 돌아가서 다른 각도로 재생성
    # (e.g., academic → web, positive → counter-evidence, 다른 키워드 조합)
```

**최종 결과:** `final_queries` = 실행할 검색 쿼리 (3-5개)

### 4. EXECUTE (실행)

**병렬로 검색을 실행합니다** (단일 메시지에 여러 도구 호출):

```
# final_queries (PLAN Phase 3에서 중복 제거된 쿼리)로 검색 실행
WebSearch("final_query_1")  ← 병렬
WebSearch("final_query_2")  ← 병렬
WebSearch("final_query_3")  ← 병렬

# 검색 실행 후 history에 추가 (embedding 자동 저장)
for query, result in zip(final_queries, search_results):
    add_query_to_history(
        query_text=query,
        iteration=current_iteration,
        results_count=len(result.get('items', [])),
        success=True
    )
```

유망한 URL 발견 시:
```
WebFetch("url 1", "핵심 내용 추출")  ← 병렬
WebFetch("url 2", "핵심 내용 추출")  ← 병렬
```

학술 논문 필요 시:
```
WebSearch("site:arxiv.org {키워드}")
→ PDF URL 확인
→ curl로 다운로드 (Bash)
→ Read(PDF 파일)로 분석
```

### 5. VERIFY (검증) - Hallucination 방지

모든 사실적 주장에 다음을 적용합니다:

**Layer 1: Source Grounding**
- 소스 없는 주장 → [?] 태그
- "모른다"고 표현 가능

**Layer 2: Cross-Validation**
- 단일 소스: 신뢰도 0.6
- 2개 소스 일치: 신뢰도 0.8
- 3개+ 소스 일치: 신뢰도 0.95
- 모순 발견: ⚠ 플래그

**Layer 3: Self-Consistency**
- 중요 결론은 다른 각도에서 재검토

**Layer 4: Confidence Tagging**
- ✓✓ VERIFIED (다수 신뢰 소스)
- ✓ HIGH (단일 신뢰 소스)
- ~ LIKELY (추정)
- ? UNCERTAIN (불확실)
- ⚠ CONTRADICTED (모순)

### 6. SYNTHESIZE (종합) - Memory Blocks Update

새로운 정보를 3-tier Memory에 통합합니다:

```python
# 1. Knowledge Graph 자동 업데이트 (knowledge_tracker.py)
from knowledge_tracker import KnowledgeTracker
from memory_manager import MemoryManager

kt = KnowledgeTracker()
mm = MemoryManager()

# 핵심 발견 사항 추가 (embedding 자동 생성)
for finding in new_findings:
    kt.add_finding(
        text=finding["text"],
        confidence=finding["confidence"],
        hypothesis_id=finding.get("hypothesis_id"),
        iteration=current_iteration
    )

# 모순 자동 탐지 (>0.85 similarity + confidence 차이)
contradictions = kt.detect_contradictions()
if contradictions:
    print(f"⚠️  {len(contradictions)} contradictions detected")
    # state.json의 contradictions_found 업데이트

# 2. 가설 평가 및 Priority-based Filtering
for hypothesis in hypotheses:
    # 2.1 지지/반증 증거 연결
    for finding in new_findings:
        if finding.get("hypothesis_id") == hypothesis["id"]:
            evidence_item = {
                "source": finding.get("source", "unknown"),
                "summary": finding["text"][:100],
                "confidence": finding["confidence"],
                "iteration": current_iteration
            }

            if finding["confidence"] >= 0.7:
                hypothesis.setdefault("supporting_evidence", []).append(evidence_item)
            else:
                hypothesis.setdefault("contradicting_evidence", []).append(evidence_item)

    # 2.2 확신도 재계산 (베이지안 업데이트)
    support_count = len(hypothesis.get("supporting_evidence", []))
    contra_count = len(hypothesis.get("contradicting_evidence", []))

    # 가중치: 지지 증거 +10%, 반증 증거 -15%
    support_weight = support_count * 0.1
    contra_weight = contra_count * 0.15

    # 현재 확신도 업데이트 (0.0 ~ 1.0 범위 유지)
    current_confidence = hypothesis.get("confidence", 0.5)
    hypothesis["confidence"] = max(0.0, min(1.0,
        current_confidence + support_weight - contra_weight
    ))

    # 2.3 Priority Score 계산
    # 공식: Confidence (50%) + Evidence Density (30%) + Recency (20%)

    # Evidence Density: (지지 - 반증*0.5) / 10, 최대 1.0
    evidence_density = min(1.0, (support_count - contra_count * 0.5) / 10)
    evidence_density = max(0.0, evidence_density)

    # Recency: 최근 2 iteration 내 업데이트 = 1.0, 아니면 0.5
    last_updated = hypothesis.get("last_updated_iteration", 0)
    recency = 1.0 if last_updated >= current_iteration - 2 else 0.5

    # Priority Score 계산
    hypothesis["priority_score"] = (
        hypothesis["confidence"] * 0.5 +
        evidence_density * 0.3 +
        recency * 0.2
    )
    hypothesis["last_updated_iteration"] = current_iteration

# 3. Active Hypotheses 필터링 (Priority Score 상위 5개)
hypotheses.sort(key=lambda h: h["priority_score"], reverse=True)
active_hypotheses = hypotheses[:5]
inactive_hypotheses = hypotheses[5:]

# state.json에 저장할 데이터 구성
state["active_hypotheses"] = [h["id"] for h in active_hypotheses]
state["all_hypotheses"] = hypotheses

# 터미널 출력
print(f"\n🎯 Active Hypotheses (Top 5 by Priority):")
for i, h in enumerate(active_hypotheses, 1):
    support = len(h.get("supporting_evidence", []))
    contra = len(h.get("contradicting_evidence", []))
    print(f"  {i}. [{h['id']}] {h['statement'][:60]}...")
    print(f"     Priority: {h['priority_score']:.2f} | Confidence: {h['confidence']:.2f} | Evidence: {support}+ / {contra}-")

if inactive_hypotheses:
    print(f"\n📋 Inactive Hypotheses: {len(inactive_hypotheses)} (낮은 우선순위, 재평가 대기)")

# 4. Reflexion 메모리 업데이트 (.research/reflexion.json)
# 성공/실패 패턴 기록, 학습된 교훈 추가

# 5. Working Memory 업데이트 (Observation Masking 자동 적용)
mm.update_working_memory(
    iteration=current_iteration,
    findings=new_findings,
    queries_executed=final_queries,
    active_hypotheses=state["active_hypotheses"],
    next_actions=state["next_actions"]
)
# → 자동으로 최근 10개만 유지, 오래된 것은 archival로 이동
```

### 7. SAVE (저장) - Memory Blocks 자동 관리

**3-Tier Memory 자동 업데이트:**

```python
from memory_manager import MemoryManager

mm = MemoryManager()

# Working Memory (Hot - 최근 10 iterations 자동 유지)
mm.update_working_memory(
    iteration=current_iteration,
    findings=[...],
    queries_executed=[...],
    active_hypotheses=[...],
    next_actions=[...]
)
# Observation masking 자동 적용:
# - 11번째 이전 iteration → .research/archival/ 이동
# - working_memory.json에는 최근 10개만 유지

# Semantic Memory (Structured - 핵심 발견만)
mm.update_semantic_memory(findings_md_content)
# truncate_findings_for_context()로 로드 시 자동 제한

# Archival Memory (Cold - 자동 저장)
# 오래된 iterations는 .research/archival/iteration_NNN.json에 자동 저장
```

**저장 파일 목록:**

| Memory Tier | 파일 | 업데이트 내용 | 크기 제한 |
|-------------|------|--------------|----------|
| **Working** | `.research/working_memory.json` | 최근 10 iterations | 10개 고정 |
| **Semantic** | `.research/findings.md` | 핵심 발견 사항 | 30개 최신 |
| **Archival** | `.research/archival/iteration_NNN.json` | 전체 iteration 로그 | 무제한 |
| **State** | `.research/state.json` | 전체 상태, 가설, 메트릭 | - |
| **History** | `.research/search_history.json` | 검색 히스토리 (자동 저장) | - |

**Observation Masking 효과:**
- 컨텍스트 크기 67% 감소 (JetBrains Research 검증)
- Cost saving + problem-solving ability 동시 유지
- 필요 시 archival에서 과거 데이터 복원 가능
```

### 8. OUTPUT (출력)

다음 형식으로 출력합니다:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Iteration #N 완료
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 이번 발견:
   - (핵심 발견 1) [신뢰도 태그]
   - (핵심 발견 2) [신뢰도 태그]
   - (핵심 발견 3) [신뢰도 태그]

🎯 Active Hypotheses (Top 5):
   1. [H1] (가설 내용)
      확신도: 85% | Priority: 0.78 | 지지: 2개 | 반증: 0개
   2. [H3] (가설 내용)
      확신도: 80% | Priority: 0.72 | 지지: 3개 | 반증: 1개
   ...

📋 Inactive: N개 가설 (우선순위 낮음, 재평가 대기)

📈 다음 계획: (active_hypotheses 기반 탐색 전략)

📊 진행도: X% (답변된 서브질문 / 전체)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**OUTPUT 출력 후 반드시 9. LOOP 섹션으로 진행합니다.**

## 사고 도구 (상황별 선택)

| 상황 | 도구 | 적용 방식 |
|------|------|-----------|
| 막힐 때 | **제1원칙** | 기존 가정을 버리고 근본 원리부터 재구성 |
| 정보 과다 | **오컴의 면도날** | 복잡한 설명보다 단순한 설명 우선 |
| 확신이 생길 때 | **반증 가능성** | 가설을 반박할 증거 적극 탐색 |
| 새 방향 필요 | **과학적 방법론** | 관찰→가설→실험→분석 사이클 |

## Loop Drift 방지 규칙

1. 같은 검색 쿼리 2회 반복 시 → 쿼리 변형 필수
2. 같은 행동 패턴 3회 반복 시 → 전략 변경 필수
3. 5회 연속 새 정보 없음 → 다른 접근법 시도
4. 막힘 감지 시 → reflexion 메모리 참조하여 대안 탐색

**search_history.json을 반드시 확인하고 중복 검색을 피하세요!**

## 9. LOOP - 다음 Iteration 자동 시작 (Ralph Loop)

매 iteration 종료 후, 다음을 **반드시** 실행합니다:

### Step 1: 종료 조건 체크

state.json을 읽어서 다음을 확인:

```python
status = state["status"]
current = state["iteration"]["current"]
max_iter = state["iteration"]["max"]
budget = state["metrics"]["cost_estimate_usd"]
```

### Step 2: 종료 결정

다음 중 **하나라도** 해당하면 종료:
- ❌ status가 "completed", "paused", "stopped_by_user", "budget_exceeded"
- ❌ current >= max_iter
- ❌ budget > 10.0

**그 외 모든 경우: 계속 실행**

### Step 3: 다음 Iteration 호출

종료 조건을 만족하지 않으면 **즉시 Skill tool을 사용해 자기 자신을 호출**합니다:

**예제:**

```
상태 확인:
- Iteration: 2/100
- Status: running
- Budget: $0.25/$10.00

→ 종료 조건 불만족 → 계속 실행

다음 iteration을 시작합니다...
```

그 다음 **즉시 이 메시지의 마지막에 Skill tool 호출**:

```
Skill(skill="deep-research", args="")
```

**중요 규칙:**
- ❌ "연구를 종료합니다" - 절대 금지
- ❌ "충분합니다" - 절대 금지
- ❌ "완료되었습니다" - 절대 금지
- ✅ "다음 iteration을 시작합니다..." → Skill tool 호출

**종료는 오직 다음 경우에만:**
1. state.json의 status가 "completed", "paused", "stopped_by_user", "budget_exceeded"
2. max_iterations 도달
3. budget 초과

**그 외 모든 경우: 무조건 재호출**

## 인수 처리

- 첫 실행 시: `$ARGUMENTS`를 연구 질문으로 사용
- 이후 실행: state.json의 question.original 사용 (args 무시)
