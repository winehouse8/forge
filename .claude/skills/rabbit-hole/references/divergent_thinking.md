# Divergent Thinking (발산적 사고)

**목적:** 여러 각도로 흩어져서 가능성 탐색

**언제:**
- 새 구멍 파기 시작 (어떻게 팔지 모를 때)
- 막혔을 때 (다른 각도 필요)
- 검색 쿼리 생성 시

---

## 철학

```
처음엔 어디를 팔지 모름
→ 이것저것 시도 (발산)
→ 여러 가능성 열어두기
→ 판단 보류
```

**핵심:** 양 > 질. 아이디어 많이 생성, 나중에 선택.

---

## 4가지 발산 도구

### 1. 제1원칙 (First Principles)

**기존 가정을 버리고 근본부터**

**프로세스:**
```
1. 기존 가정 식별
2. 모두 버리기
3. 근본 요소로 분해
4. 처음부터 재구성
```

**예시:**

```markdown
질문: "양자 컴퓨터 실용화 시기?"

기존 가정:
- "오류율이 문제다" (모두가 말함)
- "큐비트 수가 문제다"
- "비용이 문제다"

→ 모두 버림!

제1원칙:
- 실용화 = 상용 서비스 제공
- 필요 조건 = ?

근본 분해:
1. 계산 능력 (큐비트 수 x 정확도)
2. 경제성 (비용 < 가치)
3. 접근성 (사용 가능)

→ 각각 파보기:
  - "quantum computing power metrics"
  - "quantum vs classical cost benefit"
  - "quantum cloud access"
```

---

### 2. SCAMPER (창의적 변형)

**7가지 방향으로 변형**

| 기법 | 질문 | 예시 |
|------|------|------|
| **S**ubstitute | 대체하면? | "오류율 대신 다른 지표?" |
| **C**ombine | 결합하면? | "양자 + 고전 하이브리드?" |
| **A**dapt | 적용하면? | "다른 분야 방법 가져오기?" |
| **M**odify | 수정하면? | "큐비트 구조 바꾸기?" |
| **P**ut to use | 다른 용도? | "다른 문제에 쓰기?" |
| **E**liminate | 제거하면? | "오류 수정 안 하면?" |
| **R**everse | 반대로? | "고전이 양자 시뮬?" |

**예시:**

```markdown
주제: "표면 코드"

Substitute: "표면 대신 다른 구조?"
  → "topological vs surface code"

Combine: "표면 코드 + 다른 기술?"
  → "surface code hybrid approaches"

Adapt: "다른 분야 오류 수정 방법?"
  → "error correction computer science quantum"

Modify: "표면 코드 변형?"
  → "surface code variants improvements"

→ 4개 검색 쿼리 생성
```

---

### 3. Matrix of Thought (다중 경로)

**3개 병렬 경로로 탐색**

**프로세스:**
```
Path A: [첫 번째 각도]
Path B: [두 번째 각도]
Path C: [세 번째 각도]

각 경로 독립 탐색
→ 나중에 교차 검증
```

**예시:**

```markdown
주제: "Majorana 페르미온"

Path A: 이론적 이해
  - "Majorana fermion theory"
  - "Majorana mathematical formulation"
  → 근본 원리 파악

Path B: 실험적 검증
  - "Majorana zero modes experiment"
  - "Majorana experimental evidence"
  → 실제 존재 확인

Path C: 응용
  - "Majorana topological qubit"
  - "Majorana quantum computing"
  → 어디에 쓰나

→ 6개 검색 쿼리 (3 경로 x 2)
```

---

### 4. TRIZ (모순 해결)

**40가지 발명 원리 (일부)**

**주요 원리:**

1. **분할 (Segmentation)**
   - 문제를 부분으로 나누기
   - 예: "양자 실용화" → "오류율", "비용", "응용"

2. **역발상 (Inversion)**
   - 반대로 생각
   - 예: "오류 줄이기" → "오류 활용하기"

3. **중개자 (Mediator)**
   - 중간 매체 사용
   - 예: "직접 양자" → "클라우드 양자"

4. **선행 조치 (Prior Action)**
   - 미리 준비
   - 예: "오류 발생 후 수정" → "오류 방지 설계"

**예시:**

```markdown
모순: "큐비트 수 늘리기 vs 오류율 낮추기"
(큐비트 많으면 오류 증가)

TRIZ 원리 적용:

분할:
  - "큐비트 모듈화"
  - "sector별 독립 운영"
  → "modular quantum architecture"

중개자:
  - "오류 수정 레이어 추가"
  - "소프트웨어로 보정"
  → "quantum error correction layer"

→ 2개 검색 쿼리
```

---

## 검색 쿼리 생성

### 발산 프로세스

```
1. 구멍 선택: "Majorana 페르미온"

2. 제1원칙: Majorana = ?
   → "Majorana fermion what is"

3. SCAMPER:
   - Compare: "Majorana vs Dirac"
   - Adapt: "Majorana condensed matter"

4. Matrix of Thought:
   - Path A: "Majorana theory"
   - Path B: "Majorana experiment"
   - Path C: "Majorana quantum"

5. TRIZ:
   - 모순 해결: "Majorana implementation challenges"

→ 후보 쿼리: 8개

6. 중복 제거 (deduplicate_search.py):
   → 최종 쿼리: 5개
```

---

## 자주 하는 실수

### ❌ 잘못된 예

1. **너무 일찍 판단**
   ```
   "이 쿼리는 별로일 것 같아" → 제외
   → 발산 단계에서는 판단 보류!
   ```

2. **한 가지 각도만**
   ```
   모두 이론적 접근만
   → 다양한 각도 필요!
   ```

3. **너무 적게 생성**
   ```
   후보 3개만 생성
   → 최소 5-10개 필요!
   ```

### ✅ 올바른 예

1. **판단 보류**
   ```
   좋은지 나쁜지 모르겠지만 일단 추가
   → 나중에 선택
   ```

2. **다양한 각도**
   ```
   이론 + 실험 + 응용 + 비교 + ...
   ```

3. **양 우선**
   ```
   일단 10개 생성
   → 나중에 5개 선택
   ```

---

## 코드 예시

```python
def divergent_search_queries(hole_topic, context):
    """
    발산적 사고로 검색 쿼리 생성
    """
    queries = []

    # 1. 제1원칙
    fundamental = first_principles(hole_topic)
    queries.extend(fundamental)

    # 2. SCAMPER
    scamper_queries = [
        f"{hole_topic} substitute alternative",
        f"{hole_topic} combine hybrid",
        f"{hole_topic} vs comparison"
    ]
    queries.extend(scamper_queries)

    # 3. Matrix of Thought
    matrix = [
        f"{hole_topic} theory fundamentals",
        f"{hole_topic} experiment practical",
        f"{hole_topic} application use cases"
    ]
    queries.extend(matrix)

    # 4. TRIZ (if contradiction exists)
    if context.has_contradiction:
        triz_query = f"{hole_topic} challenges solutions"
        queries.append(triz_query)

    return queries  # 8-12개
```

---

## 발산 체크리스트

### 시작 전
- [ ] 어느 각도를 팔지 정하지 않았는가?
- [ ] 열린 마음으로 시작하는가?

### 과정 중
- [ ] 최소 5-10개 후보 생성했는가?
- [ ] 3가지 이상 다른 각도 시도했는가?
- [ ] 판단을 보류하고 있는가?

### 완료 후
- [ ] 다양한 쿼리가 생성되었는가?
- [ ] 예상 밖의 각도도 포함되었는가?
- [ ] 수렴 단계로 넘길 준비가 되었는가?

---

**발산하세요! 많이 시도하고, 나중에 선택하기!** 🌟
