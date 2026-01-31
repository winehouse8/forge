# Convergent Thinking (수렴적 사고)

**목적:** 흩어진 정보를 모아 하나의 이해로 통합

**언제:**
- 검색 결과 분석 시 (이해 정리)
- 가설 평가 시 (살릴 것/버릴 것)
- 구멍 완료 시 (핵심 이해 도출)

---

## 철학

```
여러 정보 수집 완료
→ 흩어진 조각들
→ 하나의 그림으로 (수렴)
→ 핵심 이해 도출
```

**핵심:** 질 > 양. 정보 통합, 본질 파악.

---

## 4가지 수렴 도구

### 1. 오컴의 면도날 (Occam's Razor)

**단순한 설명 우선**

**원칙:**
```
복잡한 설명 vs 단순한 설명
→ 단순한 쪽 선택
→ "필요 이상으로 복잡하게 하지 말라"
```

**예시:**

```markdown
주제: "Majorana 페르미온"

수집된 정보:
- Majorana는 Bogoliubov 준입자
- BdG Hamiltonian의 고유상태
- 자기 자신이 반입자
- γ† = γ (생성 = 소멸 연산자)

복잡한 설명:
  "Majorana는 Bogoliubov-de Gennes Hamiltonian의
   대각화 과정에서 나타나는 준입자로..."

단순한 설명:
  "자기 자신 = 반입자인 특수 입자"

→ 단순한 설명 채택
→ 복잡한 건 나중에 필요하면
```

**적용:**

```python
def simplest_explanation(explanations):
    """가장 단순한 설명 선택"""

    scores = []
    for exp in explanations:
        # 단순성 평가
        simplicity = (
            1.0 / len(exp.split())  # 단어 수 적을수록
            + 1.0 / exp.count('and')  # 조건 적을수록
            + (1.0 if no_jargon(exp) else 0.5)  # 전문용어 적을수록
        )
        scores.append(simplicity)

    return explanations[argmax(scores)]
```

---

### 2. 베이지안 추론 (Bayesian Reasoning)

**증거로 확률 업데이트**

**공식:**
```
P(가설|증거) = P(증거|가설) * P(가설) / P(증거)

사후 확률 = (우도 * 사전 확률) / 정규화
```

**실전 적용 (간소화):**

```markdown
가설: "Majorana가 토폴로지 큐비트 핵심"

사전 확률 (prior):
  - 처음: 모름 → 0.50 (중립)

증거 1 (Nature 논문):
  - "Majorana for topological qubits"
  - 신뢰도: 0.90 (peer-reviewed)
  → 사후: 0.50 → 0.70 (+0.20)

증거 2 (Science 논문):
  - "topological computing with Majorana"
  - 신뢰도: 0.90
  - 독립 소스 → 추가 +0.15
  → 사후: 0.70 → 0.85

증거 3 (Microsoft 블로그):
  - "our qubit uses Majorana"
  - 신뢰도: 0.70 (공식 but 블로그)
  → 사후: 0.85 → 0.90 (+0.05)

최종 확률: 0.90 (높은 확신)
```

**간소화 규칙:**

| 증거 유형 | 신뢰도 | 업데이트 |
|----------|--------|----------|
| Peer-reviewed | 0.9 | +0.20 |
| 공식 발표 | 0.8 | +0.15 |
| Preprint | 0.7 | +0.10 |
| 뉴스 (전문) | 0.7 | +0.10 |
| 블로그 | 0.5 | +0.05 |

**독립 소스 보너스:** 2번째 소스부터 +0.05 추가

---

### 3. 반증 가능성 (Falsifiability)

**반증할 수 없는 것은 버리기**

**원칙:**
```
가설이 검증 가능한가?
반증할 수 있는가?

YES → 과학적 가설
NO → 버림
```

**예시:**

```markdown
가설 A: "양자 컴퓨터는 2030년 실용화"
  반증 가능:
  - 2030년 되면 확인 가능 ✓
  - 실용화 기준 명확 필요
  → 검증 가능 (좋은 가설)

가설 B: "양자 컴퓨터는 언젠가 실용화"
  반증 가능:
  - 언젠가 = 언제? ❌
  - 반증 불가능
  → 나쁜 가설 (버림)

가설 C: "오류율 1% 이하면 실용화"
  반증 가능:
  - 측정 가능한 기준 ✓
  - 실험으로 검증 가능 ✓
  → 좋은 가설
```

**적용:**

```python
def is_falsifiable(hypothesis):
    """반증 가능성 체크"""

    # 1. 측정 가능한 기준 있나?
    has_measurable_criteria = check_measurable(hypothesis)

    # 2. 시간 제한 있나?
    has_time_bound = check_time_bound(hypothesis)

    # 3. 명확한 조건 있나?
    has_clear_conditions = check_conditions(hypothesis)

    # 최소 2개 만족해야
    score = sum([
        has_measurable_criteria,
        has_time_bound,
        has_clear_conditions
    ])

    return score >= 2
```

---

### 4. 변증법적 사고 (Dialectical Thinking)

**정-반-합으로 통합**

**프로세스:**
```
Thesis (정): 첫 번째 주장
  ↓
Antithesis (반): 대립 주장
  ↓
Synthesis (합): 통합된 이해
```

**예시:**

```markdown
주제: "양자 실용화 시기"

Thesis (정): "2030년 가능"
  증거:
  - IBM 로드맵: 2030년 목표
  - 기술 발전 빠름
  - 낙관적 전망

Antithesis (반): "2040년 이후"
  증거:
  - Nature 논문: 10-20년 소요
  - 오류율 개선 느림
  - 보수적 전망

Synthesis (합): "2035년 부분 실용화"
  통합:
  - 도메인별 차등 실용화
  - 신약 개발 등 일부 먼저 (2030년대 초)
  - 범용 실용화는 늦음 (2040년대)
  - 현실적 절충안
```

**적용:**

```python
def dialectical_synthesis(claims):
    """변증법적 통합"""

    # Thesis: 첫 주장
    thesis = claims[0]

    # Antithesis: 대립 찾기
    antithesis = find_contradicting(claims, thesis)

    if antithesis:
        # Synthesis: 통합
        synthesis = integrate(thesis, antithesis)
        return synthesis
    else:
        # 대립 없으면 thesis 그대로
        return thesis
```

---

## 수렴 프로세스

### 예시: "Majorana 페르미온" 이해

```markdown
수집된 정보 (검색 결과 4개):

1. Nature: "Majorana = quasi-particle, self-antiparticle"
2. Science: "Kitaev chain model"
3. MIT: "topological quantum computing"
4. Microsoft: "our topological qubit uses Majorana"

---

Step 1: 오컴의 면도날 (단순 설명)

복잡: "Majorana는 Bogoliubov 변환의..."
단순: "자기 자신 = 반입자"

→ 단순 설명 채택

---

Step 2: 베이지안 업데이트

사전: 0.50 (모름)

Nature (0.9): → 0.70
Science (0.9): → 0.85 (독립 소스)
MIT (0.8): → 0.90
Microsoft (0.7): → 0.92

최종: "Majorana가 토폴로지 큐비트 핵심" (확률 0.92)

---

Step 3: 반증 가능성

가설: "Majorana가 토폴로지 큐비트 핵심"

반증 조건:
- 토폴로지 큐비트가 Majorana 없이 구현된다면 반증
- 측정 가능 ✓

→ 반증 가능 (좋은 가설)

---

Step 4: 변증법

Thesis: "Majorana가 핵심"
Antithesis: "구현 어려움" (실험적 도전)
Synthesis: "이론적으로 핵심이지만 실용화는 도전적"

---

최종 이해:

"Majorana 페르미온은 자기 자신이 반입자인 준입자.
 Kitaev chain으로 모델링되며,
 토폴로지 양자 컴퓨팅의 이론적 핵심 요소.
 Microsoft 등이 구현 시도 중이나 실험적 도전 과제 있음."

이해도: 75%
확신도: 0.92
```

---

## 자주 하는 실수

### ❌ 잘못된 예

1. **복잡한 설명 선호**
   ```
   "더 전문적으로 보이려고 복잡하게"
   → 오컴의 면도날 위반!
   ```

2. **증거 무시**
   ```
   사전 확률 0.50 → 증거 3개 → 여전히 0.50
   → 베이지안 업데이트 안 함!
   ```

3. **모순 무시**
   ```
   Thesis: "2030년"
   Antithesis: "2040년"
   → "평균 2035년" (단순 평균)
   → 변증법적 통합 안 함!
   ```

### ✅ 올바른 예

1. **단순 명료**
   ```
   핵심만 추출
   "자기 자신 = 반입자"
   ```

2. **증거로 업데이트**
   ```
   증거 있을 때마다 확률 조정
   0.50 → 0.70 → 0.85 → 0.92
   ```

3. **대립 통합**
   ```
   양쪽 고려
   → 현실적 절충안
   ```

---

## 수렴 체크리스트

### 시작 전
- [ ] 수집된 정보가 충분한가?
- [ ] 서로 다른 관점이 있는가?

### 과정 중
- [ ] 가장 단순한 설명을 찾았는가?
- [ ] 증거로 확률을 업데이트했는가?
- [ ] 반증 가능성을 확인했는가?
- [ ] 대립되는 관점을 통합했는가?

### 완료 후
- [ ] 핵심 이해가 명확한가?
- [ ] 확신도가 적절한가? (0.7-0.9)
- [ ] 다음 단계가 보이는가?

---

## 코드 예시

```python
def converge_understanding(search_results, context):
    """
    수렴적 사고로 이해 도출
    """

    # 1. 오컴의 면도날: 단순 설명
    simple_explanation = simplest_explanation(search_results)

    # 2. 베이지안: 확률 업데이트
    confidence = bayesian_update(
        prior=0.50,
        evidences=search_results
    )

    # 3. 반증 가능성: 가설 검증
    is_falsifiable_claim = check_falsifiability(simple_explanation)

    # 4. 변증법: 대립 통합
    thesis, antithesis = find_contradictions(search_results)
    if antithesis:
        final_understanding = dialectical_synthesis(thesis, antithesis)
    else:
        final_understanding = simple_explanation

    return {
        "understanding": final_understanding,
        "confidence": confidence,
        "falsifiable": is_falsifiable_claim,
        "quality": "high" if confidence > 0.7 else "medium"
    }
```

---

**수렴하세요! 흩어진 조각을 하나의 그림으로!** 🎯
