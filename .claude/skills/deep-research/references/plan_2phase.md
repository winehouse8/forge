# PLAN: 2-Phase Strategy (Divergent → Convergent → Deduplication)

**목표:** 이번 iteration의 최적 검색 전략 수립

**구조:** 발산(10+ 후보) → 수렴(3-5개 선택) → 중복제거(최종)

---

## Phase 0: Active Hypotheses 확인

### 목적

현재 집중할 가설 확인하여 검색 방향 설정

### 방법

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

### 안전성 처리

- **첫 iteration**: `all_hypotheses` 없음 → 전체 탐색 모드
- **이후 iteration**: active_hypotheses 기반 집중 탐색

---

## Phase 1: Divergent Thinking (발산) - 브레인스토밍

### 목표

**최소 10개 이상**의 검색 쿼리 후보 생성

### 규칙

- ❌ **판단 보류** (no premature filtering)
- ✅ **브레인스토밍 모드**: 아이디어 자유롭게 생성
- ✅ **다양성 우선**: 여러 각도, 여러 전략
- ✅ **양 > 질**: 이 단계에서는 많이 생성하는 게 중요

### 생성 전략

```markdown
## 목표 정의
"이번 iteration에서 달성할 것: [active_hypotheses 기반 목표]"

## 쿼리 후보 생성 (최소 10개)

### 일반 웹 검색 (3-4개)
- "keyword A B C"
- "keyword D E F latest 2026"
- "keyword G H practical applications"
- ...

### 학술/기술 검색 (3-4개)
- "site:arxiv.org [topic]"
- "site:github.com [implementation]"
- "site:semanticscholar.org [research area]"
- "site:ieee.org [technology]"
- ...

### 반증 증거 탐색 (3-4개)
- "[hypothesis] criticism"
- "[hypothesis] counterexample"
- "[hypothesis] limitations fails when"
- "[hypothesis] controversy debate"
- ...

**생성 결과:** candidate_queries = [q1, q2, ..., q10+]
```

### 예시 (양자 컴퓨팅)

```markdown
목표: H3 검증 (양자 오류율 개선 속도)

일반 웹:
1. "quantum error correction breakthrough 2026"
2. "quantum computing error rate improvement"
3. "surface code quantum error correction"

학술:
4. "site:arxiv.org quantum error correction 2025 2026"
5. "site:nature.com quantum error mitigation"
6. "site:github.com qiskit error correction"

반증:
7. "quantum error correction limitations"
8. "quantum computing error rate plateau"
9. "quantum error correction skepticism"
10. "quantum vs classical error rates comparison"

→ 10개 후보 생성 완료
```

---

## Phase 2: Convergent Thinking (수렴) - 선택과 집중

### 목표

상위 **3-5개** 최적 쿼리 선택

### 평가 기준

#### 1. 정보 가치 (Information Gain) - 40%

**높은 점수:**
- 새로운 발견 가능성 높음
- 현재 모르는 것을 알려줄 가능성
- 불확실성 감소 효과

**낮은 점수:**
- 이미 아는 내용 반복
- 현재 발견과 중복

#### 2. 다양성 (Diversity) - 30%

**높은 점수:**
- 다른 각도/소스
- 다른 도메인
- 다른 시간대 (최신 vs 고전)

**낮은 점수:**
- 비슷한 쿼리
- 같은 소스 타입

#### 3. 실행 가능성 (Feasibility) - 20%

**높은 점수:**
- 구체적이고 검색 가능
- 결과 예상 가능
- 키워드 명확

**낮은 점수:**
- 추상적이거나 모호함
- 검색 결과 불확실
- 키워드 애매

#### 4. 중복도 (Redundancy) - 10%

**내부 중복 제거:**
- candidate_queries 내에서 유사한 것 제거
- 같은 정보를 얻을 수 있는 쿼리 통합

### 선택 프로세스

```markdown
## 평가 및 선택

각 후보 쿼리를 평가:

1. q1: "quantum error correction breakthrough 2026"
   - 정보 가치: 높음 (최신 정보)
   - 다양성: 중 (일반 웹)
   - 실행성: 높음 (구체적 키워드)
   - 중복도: 낮음
   - **총점: 8/10 → 선택**

2. q2: "quantum computing error rate improvement"
   - 정보 가치: 중 (일반적)
   - 다양성: 낮음 (q1과 유사)
   - 실행성: 중
   - 중복도: 높음 (q1과 중복)
   - **총점: 5/10 → 제외**

3. q4: "site:arxiv.org quantum error correction 2025 2026"
   - 정보 가치: 높음 (학술 논문)
   - 다양성: 높음 (다른 소스)
   - 실행성: 높음
   - 중복도: 낮음
   - **총점: 9/10 → 선택**

...

**선택 결과:** filtered_queries_phase2 = [q1, q4, q7, q9, q10]
```

### 예시 결과

```
Phase 2 선택:
1. "quantum error correction breakthrough 2026" (8/10)
2. "site:arxiv.org quantum error correction 2025 2026" (9/10)
3. "quantum error correction limitations" (7/10)
4. "quantum vs classical error rates comparison" (8/10)
5. "site:github.com qiskit error correction" (7/10)

→ 5개 선택 완료
```

---

## Phase 3: 중복 검색 제거 (Deduplication)

### 목적

**과거 검색과의 중복 제거** (>0.95 유사도)

### 방법

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

### 중복 판단 기준

- **임베딩 유사도 >0.95**: 거의 동일한 쿼리
- **키워드 완전 일치**: 순서만 다른 경우

### 전략 변경 (모두 중복 시)

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
모두 중복 감지!

현재: "site:arxiv.org quantum error correction"
변경: "quantum error correction industry practical"

현재: "quantum computing breakthrough"
변경: "quantum computing failure case study"
```

### 최종 결과

```python
**최종 결과:** final_queries = [실행할 검색 쿼리 3-5개]
```

**예시:**
```
Phase 3 최종:
1. ✓ "quantum error correction breakthrough 2026"
2. ✓ "site:arxiv.org quantum error correction 2025 2026"
3. ⚠️ Skip "quantum error correction limitations" (이미 iteration 3에서 검색)
4. ✓ "quantum vs classical error rates comparison"
5. ✓ "site:github.com qiskit error correction"

→ 최종 4개 쿼리 실행
```

---

## 전략 선택 기준

### 상황별 최적 전략

| 상황 | 전략 | 이유 |
|------|------|------|
| **최신 동향 필요** | Web | 일반 검색엔진이 최신 정보 보유 |
| **학술적 근거 필요** | Academic | arXiv, IEEE 등 신뢰도 높음 |
| **확신도 >80%** | Verification | 반증 증거 적극 탐색 필요 |
| **모순 발견** | Verification | 교차 검증으로 진실 파악 |
| **구현 방법 필요** | Technical | GitHub, Stack Overflow 등 |
| **비교 필요** | Comparative | "A vs B", "comparison", "benchmark" |

### 키워드 조합 패턴

**일반 패턴:**
```
[주제] + [관점] + [시간] + [제약]

예:
- "quantum computing" + "error correction" + "2026" + "practical"
- "AI safety" + "alignment" + "recent" + "DeepMind"
```

**Academic 패턴:**
```
"site:arxiv.org" + [주제] + [연도]

예:
- "site:arxiv.org quantum supremacy 2025"
- "site:nature.com CRISPR off-target effects"
```

**Verification 패턴:**
```
[가설] + ["criticism" | "counterexample" | "limitations" | "fails when"]

예:
- "quantum computing criticism"
- "AI alignment counterexample"
- "fusion energy limitations"
```

---

## 품질 체크리스트

### Phase 1 (Divergent)
- [ ] 최소 10개 이상 생성했는가?
- [ ] 3가지 전략 (Web/Academic/Verification) 모두 포함?
- [ ] 다양한 각도 (긍정/부정/중립) 포함?

### Phase 2 (Convergent)
- [ ] 각 쿼리의 정보 가치 평가했는가?
- [ ] 다양성 확보했는가? (같은 소스 반복 X)
- [ ] 3-5개 선택했는가?

### Phase 3 (Deduplication)
- [ ] search_history.json 확인했는가?
- [ ] 모두 중복이면 전략 변경했는가?
- [ ] 최종 1개 이상 쿼리 확보했는가?

---

## 자주 하는 실수

### ❌ 잘못된 예

1. **Phase 1에서 필터링**
   ```
   "이 쿼리는 별로일 것 같아" → 제외
   → Phase 1은 판단 보류! 일단 생성
   ```

2. **같은 각도 반복**
   ```
   10개 모두 "quantum computing applications"
   → 다양한 각도 필요: applications, limitations, history, future
   ```

3. **중복 체크 생략**
   ```
   Phase 2 결과를 바로 실행
   → Phase 3 중복 체크 필수!
   ```

4. **모두 중복 시 포기**
   ```
   "모두 중복이네, 같은 쿼리 다시 실행"
   → 전략 변경 필수!
   ```

### ✅ 올바른 예

1. **Phase 1: 양 우선**
   ```
   좋은지 나쁜지 모르겠지만 일단 10개 생성
   ```

2. **Phase 2: 다양성 확보**
   ```
   Web 2개 + Academic 2개 + Verification 1개
   ```

3. **Phase 3: 철저한 중복 체크**
   ```
   5개 중 2개 중복 발견 → 3개 실행
   ```

4. **전략 변경**
   ```
   모두 중복 → arxiv에서 github로 변경
   ```

---

**PLAN 완료 → EXECUTE 단계로 진행**
