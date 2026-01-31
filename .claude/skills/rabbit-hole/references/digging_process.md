# DIG: 구멍 파기 프로세스

**목표:** 선택한 구멍을 여러 번 파며 깊이 이해하기

**철학:** 한 번에 다 알 수 없음. 조금씩 파며 발견하기.

---

## 파기 루프 (Digging Loop)

```
DIG (한 구멍):
  ┌─────────────────────────────────────┐
  │ 1. 발산 (여러 각도 시도)              │
  │    📖 divergent_thinking.md          │
  │    → 검색 쿼리 생성                  │
  │                                      │
  │ 2. 검색 (정보 수집)                  │
  │    + 중복 제거                       │
  │                                      │
  │ 3. 발견 (새 구멍 찾기)                │
  │    📖 curiosity_heuristics.md        │
  │    → 興미 판단 → 큐 추가             │
  │                                      │
  │ 4. 수렴 (이 구멍 이해)                │
  │    📖 convergent_thinking.md         │
  │                                      │
  │ 5. 검증 (사실 확인)                  │
  │    📖 verify_4layers.md              │
  │                                      │
  │ 6. 반성 (더 팔까?)                   │
  │    YES → depth++ → 1로 돌아가기 ────┘
  │    NO  → REFLECT로 (다른 구멍)
  └─────────────────────────────────────┘
```

**핵심:** 작은 루프. 계속 파다가 만족하거나 더 흥미로운 것 발견하면 나감.

---

## Step 1: 발산 (여러 각도 시도)

**목적:** 이 구멍을 어떻게 파볼지 여러 각도 탐색

**도구:** `divergent_thinking.md`

### 프로세스

```markdown
구멍: "Majorana 페르미온"
depth: 0 (처음)

📖 divergent_thinking.md

Extended Thinking:

제1원칙 (근본 분해):
  - Majorana = 뭔가?
  - 페르미온 = 물질 구성 입자
  - "자기 자신이 반입자" 뭔 소리?

  → 쿼리: "Majorana fermion what is"

Matrix of Thought (다중 경로):
  Path A: 이론적 이해
    → "Majorana fermion theory physics"

  Path B: 실험적 검증
    → "Majorana zero modes experiment"

  Path C: 응용
    → "Majorana topological quantum computing"

SCAMPER (창의적 변형):
  - Compare: 다른 입자와 비교?
    → "Majorana vs Dirac fermion"

  - Adapt: 다른 분야에서?
    → "Majorana condensed matter"

→ 검색 쿼리 (발산):
  q1: "Majorana fermion what is"
  q2: "Majorana vs Dirac fermion"
  q3: "Majorana zero modes experiment"
  q4: "Majorana topological quantum"
  q5: "Majorana condensed matter"
```

### 중복 제거

```python
from deduplicate_search import is_duplicate_query

final_queries = []
for q in candidate_queries:
    is_dup, similar = is_duplicate_query(q)
    if not is_dup:
        final_queries.append(q)

# 최종: [q1, q2, q3, q4]
# q5는 이미 검색한 것과 유사하여 제외됨
```

---

## Step 2: 검색 (정보 수집)

**목적:** 병렬로 정보 수집

```python
# 병렬 검색 (단일 메시지에 여러 도구 호출)
WebSearch(final_queries[0])  # 병렬
WebSearch(final_queries[1])  # 병렬
WebSearch(final_queries[2])  # 병렬
WebSearch(final_queries[3])  # 병렬

# 결과 수집
results = [result_0, result_1, result_2, result_3]

# 히스토리 저장
for query, result in zip(final_queries, results):
    add_query_to_history(
        query_text=query,
        iteration=current_iteration,
        hole_id=selected_hole.id,
        results_count=len(result.get('items', [])),
        success=True
    )
```

---

## Step 3: 발견 (새 구멍 찾기)

**목적:** 검색 결과에서 흥미로운 새 개념 발견

**도구:** `curiosity_heuristics.md`

### 프로세스

```markdown
검색 결과 분석:

Result 1 (Nature - Majorana what is):
  "Majorana fermions are quasi-particles..."
  "...described by the Kitaev chain model..."
  "...crucial for topological quantum computing..."

  💡 발견 1: "Kitaev chain"
  💡 발견 2: "quasi-particles" (준입자)

Result 2 (Science - Majorana vs Dirac):
  "Unlike Dirac fermions, Majorana..."
  "...Majorana is its own antiparticle..."

  💡 발견: Dirac과 차이점 이해 (새 개념은 아님)

Result 3 (arXiv - Majorana experiment):
  "Experimental evidence in superconductor..."
  "...Microsoft's topological qubit project..."

  💡 발견 3: "Microsoft topological qubit"
  💡 발견 4: "superconductor" (초전도체 관련)

Result 4 (MIT - topological quantum):
  "Topological protection against errors..."
  "...Majorana zero modes..."

  💡 발견 5: "topological protection"
```

### 興미 판단

```markdown
📖 curiosity_heuristics.md

발견 1: "Kitaev chain model"
  - 근본성: 0.9 (Majorana의 기초 모델)
  - 연결성: 0.7 (부모 구멍과 연관)
  - 신선도: 0.9 (완전 새로움)
  - 구체성: 0.6 (이론적 모델)

  興미 = 0.9*0.3 + 0.7*0.3 + 0.9*0.25 + 0.6*0.15
       = 0.27 + 0.21 + 0.225 + 0.09
       = 0.795

  → 0.795 > 0.70 ✓ 큐 추가!

발견 3: "Microsoft topological qubit"
  - 근본성: 0.4 (응용)
  - 연결성: 1.0 (원래 질문 "실용화"와 직결!)
  - 신선도: 0.6 (알려진 프로젝트)
  - 구체성: 0.9 (구체적 구현)

  興미 = 0.4*0.3 + 1.0*0.3 + 0.6*0.25 + 0.9*0.15
       = 0.12 + 0.30 + 0.15 + 0.135
       = 0.705

  → 0.705 > 0.70 ✓ 큐 추가!

발견 2, 4, 5: 興미 < 0.70 → 무시
```

### 큐 추가

```python
from curiosity_manager import CuriosityManager

cm = CuriosityManager()

# 발견 1 추가
cm.add_hole(
    topic="Kitaev chain model",
    interest=0.795,
    parent=selected_hole.id,
    depth=0,
    source="Nature article on Majorana"
)

# 발견 3 추가
cm.add_hole(
    topic="Microsoft topological qubit",
    interest=0.705,
    parent=selected_hole.id,
    depth=0,
    source="arXiv paper on experimental Majorana"
)
```

---

## Step 4: 수렴 (이 구멍 이해)

**목적:** 지금까지 수집한 정보를 정리하여 이해

**도구:** `convergent_thinking.md`

### 프로세스

```markdown
📖 convergent_thinking.md

구멍: "Majorana 페르미온"
depth: 0 (1차 파기)

수집된 정보:
1. Majorana = 자기 자신이 반입자인 페르미온
2. Quasi-particle (준입자)
3. Kitaev chain으로 모델링
4. 토폴로지 양자 컴퓨팅에 핵심
5. Microsoft가 구현 중

오컴의 면도날 (단순한 설명 우선):
  복잡: "Majorana는 Bogoliubov 준입자로..."
  단순: "자기 자신 = 반입자인 특수 입자"

  → 단순 설명 채택

베이지안 추론 (확률 업데이트):
  사전 확률: "Majorana = 모름" (0.0)

  증거:
  - Nature 논문: "토폴로지 큐비트 핵심"
  - Science: "실험적 검증 진행 중"
  - MIT: "오류 보호 효과"

  사후 확률: "Majorana가 실용화 핵심" (0.75)

변증법적 사고 (정-반-합):
  Thesis: "Majorana는 이론적으로 중요"
  Antithesis: "실험 검증 어려움"
  Synthesis: "중요하지만 아직 도전 과제"

핵심 이해:
  "Majorana는 토폴로지 양자 컴퓨팅의 핵심 요소.
   이론적으로 강력하지만 실험 구현은 도전적.
   Microsoft 등이 실용화 시도 중."

이해도: 75%
```

---

## Step 5: 검증 (사실 확인)

**목적:** Hallucination 방지, 출처 확보

**도구:** `verify_4layers.md`

### 프로세스

```markdown
📖 verify_4layers.md

주장: "Majorana는 토폴로지 큐비트의 핵심 요소"

Layer 1: Source Grounding
  출처 확인:
  ✓ Nature (peer-reviewed)
  ✓ Science (peer-reviewed)
  ✓ arXiv (preprint)
  ✓ Microsoft 블로그 (공식)

  → 모든 주장에 출처 있음

Layer 2: Cross-Validation
  3개 독립 소스 일치:
  - Nature: "Majorana for topological qubits"
  - Science: "topological quantum computing with Majorana"
  - Microsoft: "our qubit uses Majorana zero modes"

  신뢰도: 0.95 (3+ 소스 일치)

Layer 3: Self-Consistency
  역방향 검증:
  "토폴로지 큐비트 → Majorana 필요?"
  → YES (이론적으로 필수 요소)

  대안 설명:
  - Majorana 없이 토폴로지? → 어려움
  - 다른 방법? → 아직 없음

  → 일관성 OK

Layer 4: Confidence Tagging
  ✓✓ VERIFIED (높은 신뢰도)
```

### 결과

```python
verified_understanding = {
    "claim": "Majorana는 토폴로지 큐비트 핵심",
    "confidence": 0.95,
    "tag": "VERIFIED",
    "sources": 4,
    "last_verified": current_iteration
}
```

---

## Step 6: 반성 (더 팔까?)

**목적:** 이 구멍 계속 팔지, 다른 구멍으로 갈지 결정

### Extended Thinking

```markdown
현재 구멍: "Majorana 페르미온"
depth: 0 → 1 (1차 파기 완료)
이해도: 75%

질문 1: 이 구멍 더 팔 가치 있나?

분석:
- 기본 개념 이해 ✓
  "자기 자신 = 반입자, 토폴로지 큐비트 핵심"

- Kitaev chain 발견 ✓
  (더 근본적인 모델)

- Microsoft 구현 발견 ✓
  (실용화 직결)

- 더 파면?
  → Majorana의 수학적 세부사항
  → 너무 이론적, 실용화와 거리 멂

결론: 기본은 충분히 이해했음

질문 2: 새 발견이 더 흥미로운가?

큐 상태:
- hole_7 "Kitaev chain" (興미 0.795)
  → 이론적, 덜 실용적

- hole_8 "Microsoft qubit" (興미 0.705)
  → 실용화 직결! ← 원래 질문과 연결

- hole_2 "비용 하락" (興미 0.65)
  → 낮은 흥미

비교:
- Majorana 더 파기: 이론만 깊어짐
- Microsoft로 pivot: 실용화 타임라인 알 수 있을 듯
- Kitaev로 pivot: 근본적이지만 너무 이론적

직관:
"Microsoft가 더 흥미롭다!
 원래 질문이 '실용화 시기'니까
 구체적 타임라인 알 수 있을 것 같은데?"

최종 판단:
❌ Majorana 더 파기: 기본은 충분
✅ Pivot to hole_8: "Microsoft qubit"

이유:
- 원래 질문과 직결
- 구체적 정보 기대 (타임라인, 로드맵)
- 더 흥미로움 (실용화 > 이론)
```

### 결정

```python
decision = {
    "continue_digging": False,
    "reason": "기본 이해 충분, 더 흥미로운 구멍 발견",
    "next_hole": "hole_8",
    "current_hole_status": "explored"
}

# 현재 구멍 상태 업데이트
cm.update_hole(
    hole_id=selected_hole.id,
    depth=1,
    status="explored",
    understanding=0.75,
    children=["hole_7", "hole_8"]
)

→ REFLECT로 이동 (pivot 확정)
```

---

## 깊이 파기 예시

### 예시 1: 깊이 3까지 (계속 파기)

```
구멍: "표면 코드"

[1차 파기] depth: 0 → 1
  발산: "surface code theory", "surface code lattice"
  검색: 3개 쿼리
  발견: "2D 격자 구조" (興미 0.75)
  수렴: 표면 코드 = 2D 격자에서 큐비트 배치
  검증: Nature 2개 (신뢰도 0.85)
  반성: 더 알고 싶다! → YES

[2차 파기] depth: 1 → 2
  발산: "surface code error threshold", "surface code syndrome"
  검색: 3개 쿼리
  발견: "오류 임계값 1%" (興미 0.80)
  수렴: 임계값 이하로 오류율 낮춰야 함
  검증: Science 1개 (신뢰도 0.80)
  반성: 현재 달성률은? → YES

[3차 파기] depth: 2 → 3
  발산: "quantum error rate 2026", "IBM Google error rate"
  검색: 2개 쿼리
  발견: "IBM 0.1% 달성" (興미 0.85)
  수렴: 아직 임계값(1%) 미달
  검증: IBM 공식 (신뢰도 0.90)
  반성: 충분히 이해했음 → NO

최종 상태:
  depth: 3
  이해도: 90%
  status: explored
```

### 예시 2: 즉시 pivot (흥미로운 것 발견)

```
구멍: "양자 오류율"

[1차 파기] depth: 0 → 1
  발산: "quantum error rate improvement"
  검색: 3개 쿼리
  발견: "토폴로지 코드" (興미 0.95!) ← 매우 흥미로움!
  수렴: 오류율 개선 방법론 이해
  검증: Nature (신뢰도 0.80)
  반성: 토폴로지가 더 흥미로운데? → NO (pivot)

최종 상태:
  depth: 1
  이해도: 60% (얕게 팠음)
  status: explored

→ hole_new "토폴로지 코드" 파러 감
```

---

## 종료 조건

다음 중 하나 만족 시 파기 중단:

1. **충분한 이해**
   ```
   이해도 > 70%
   기본 개념 파악 완료
   ```

2. **더 흥미로운 발견**
   ```
   새 구멍 興미 > 현재 구멍 興미 + 0.1
   ```

3. **너무 깊음**
   ```
   depth > 5
   (토끼굴이지만 무한은 아님)
   ```

4. **바닥 도달**
   ```
   검색 결과 없음
   새 정보 없음
   ```

5. **막힘**
   ```
   3회 연속 진전 없음
   → 다른 구멍으로 pivot
   ```

---

## 재사용 도구

파기 과정에서 사용하는 도구들 (deep-research에서):

- **divergent_thinking.md** - 1. 발산
- **convergent_thinking.md** - 4. 수렴
- **verify_4layers.md** - 5. 검증
- **deduplicate_search.py** - 2. 중복 제거
- **curiosity_heuristics.md** - 3. 흥미도 판단

---

**한 구멍씩, 깊이 파며, 새로운 구멍 발견하기!** 🐰🕳️
