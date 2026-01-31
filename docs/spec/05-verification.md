# 검증 시스템 (4계층)

**문서:** 05-verification.md
**최종 수정일:** 2026-01-31
**관련 파일:** `.claude/skills/deep-research/SKILL.md:95-117`, `config.json:45-68`

---

## 목차
- [검증 시스템 개요](#검증-시스템-개요)
- [Layer 1: Source Grounding](#layer-1-source-grounding)
- [Layer 2: Cross-Validation](#layer-2-cross-validation)
- [Layer 3: Self-Consistency](#layer-3-self-consistency)
- [Layer 4: Confidence Tagging](#layer-4-confidence-tagging)
- [신뢰도 점수 시스템](#신뢰도-점수-시스템)

---

## 검증 시스템 개요

### 목적

**Hallucination 완전 방지** - LLM이 근거 없는 주장을 생성하지 못하도록 4단계 검증

### 4계층 구조

```
원시 정보 (WebSearch/Fetch 결과)
         ↓
┌─────────────────────────────────────────┐
│ Layer 1: Source Grounding               │
│ → 모든 주장에 출처 필수                  │
│ → 출처 없으면 [?] 태그                  │
└─────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│ Layer 2: Cross-Validation                │
│ → 2-3개 독립 소스 교차 확인              │
│ → 신뢰도 점수 계산                       │
└─────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│ Layer 3: Self-Consistency                │
│ → 다른 각도에서 재검토                   │
│ → 내부 모순 탐지                         │
└─────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│ Layer 4: Confidence Tagging              │
│ → ✓✓ / ✓ / ~ / ? / ⚠ 태그 부여         │
│ → 최종 신뢰도 표시                       │
└─────────────────────────────────────────┘
         ↓
검증된 사실 (findings.md에 저장)
```

---

## Layer 1: Source Grounding

### 규칙

**모든 사실적 주장은 반드시 출처를 명시해야 합니다.**

**파일:** `.claude/skills/deep-research/SKILL.md:98-100`

```markdown
**Layer 1: Source Grounding**
- 소스 없는 주장 → [?] 태그
- "모른다"고 표현 가능
```

### 적용 예시

#### ✅ 올바른 예

```markdown
GPT-4는 2023년 3월 14일 출시되었다 (openai.com)
```

#### ❌ 잘못된 예

```markdown
GPT-4는 2023년 3월 14일 출시되었다
```
→ 출처 없음 → [?] 태그 필수

### 출처 형식

| 형식 | 예시 | 사용 시점 |
|------|------|-----------|
| **도메인만** | `(openai.com)` | 일반적인 경우 |
| **전체 URL** | `(https://openai.com/blog/gpt-4)` | 정확한 출처 필요 시 |
| **복수 출처** | `(openai.com, techcrunch.com)` | 교차 검증됨 |
| **논문** | `(arxiv.org/abs/2103.xxxxx)` | 학술적 주장 |

### "모른다" 표현

**출처를 찾을 수 없을 때:**

```markdown
? GPT-5의 출시 시기는 불명확하다
  (공식 발표 없음, 검색 결과 없음)
```

**중요:** 추측하지 않고 명확히 "모른다"고 표현하는 것이 hallucination 방지의 핵심

---

## Layer 2: Cross-Validation

### 규칙

**단일 소스는 신뢰하지 않습니다. 2-3개 독립 소스에서 교차 확인합니다.**

**파일:** `.claude/skills/deep-research/SKILL.md:102-106`

```markdown
**Layer 2: Cross-Validation**
- 단일 소스: 신뢰도 0.6
- 2개 소스 일치: 신뢰도 0.8
- 3개+ 소스 일치: 신뢰도 0.95
- 모순 발견: ⚠ 플래그
```

**설정:** `config.json:45-50`

```json
"verification": {
  "require_sources": true,
  "min_source_count": 2,
  "cross_validation": true
}
```

### 신뢰도 계산

**공식:**

```python
def calculate_confidence(sources):
    if len(sources) == 0:
        return 0.0

    if len(sources) == 1:
        base_score = 0.6
    elif len(sources) == 2:
        base_score = 0.8
    else:  # 3+
        base_score = 0.95

    # 소스 신뢰도 가중치 적용
    weighted_score = base_score * average_source_credibility(sources)

    return weighted_score
```

### 예시

#### 단일 소스 (신뢰도 0.6)

```markdown
✓ GPT-4는 175B 파라미터를 사용한다 (techcrunch.com)
  신뢰도: 0.6 × 0.85 (techcrunch 신뢰도) = 0.51
```

#### 2개 소스 일치 (신뢰도 0.8)

```markdown
✓ GPT-4는 Transformer 아키텍처 기반이다
  소스: openai.com, arxiv.org
  신뢰도: 0.8 × ((0.98 + 0.95) / 2) = 0.77
```

#### 3개+ 소스 일치 (신뢰도 0.95)

```markdown
✓✓ GPT-4는 2023년 3월 14일 출시되었다
  소스: openai.com, techcrunch.com, theverge.com
  신뢰도: 0.95 × ((0.98 + 0.85 + 0.80) / 3) = 0.83
```

#### 모순 발견 (⚠ 플래그)

```markdown
⚠ GPT-4의 파라미터 수에 대한 모순
  주장 A: 175B (techcrunch.com)
  주장 B: 220B (forbes.com)
  주장 C: 비공개 (openai.com)

  → 추가 조사 필요
```

---

## Layer 3: Self-Consistency

### 규칙

**중요한 결론은 다른 각도에서 재검토하여 내부 모순을 탐지합니다.**

**파일:** `.claude/skills/deep-research/SKILL.md:108-109`

```markdown
**Layer 3: Self-Consistency**
- 중요 결론은 다른 각도에서 재검토
```

### 적용 방법

**1. 다각도 검증**

```markdown
주장: "양자 컴퓨터는 RSA 암호화를 위협한다"

검증 1 (기술적 각도):
- Shor's algorithm이 RSA를 다항 시간에 해독 가능 (arxiv.org)
- ✓ 기술적으로 가능

검증 2 (실용성 각도):
- 현재 양자 컴퓨터는 50-100 qubit 수준 (nature.com)
- RSA 해독에는 최소 4096 qubit 필요 (ieee.org)
- ? 실용화까지 10년+ 소요

검증 3 (대응책 각도):
- 양자 내성 암호화(Post-Quantum Cryptography) 개발 중 (nist.gov)
- ✓ 대응책 존재

종합:
✓ 기술적으로는 위협이지만, 현재 즉각적 위험은 아님
  실용화까지 시간이 있으며 대응책도 개발 중
```

**2. 시간축 검증**

```markdown
주장: "GPT 시리즈는 계속 발전했다"

GPT-1 (2018): 117M 파라미터 (openai.com)
GPT-2 (2019): 1.5B 파라미터 (openai.com)
GPT-3 (2020): 175B 파라미터 (arxiv.org)
GPT-4 (2023): 비공개 (openai.com)

→ ✓ 일관된 발전 패턴 확인
→ ✓ 내부 모순 없음
```

**3. 논리 일관성 검증**

```markdown
주장 A: "LLM은 추론 능력이 없다"
주장 B: "GPT-4는 수학 문제를 풀 수 있다"

→ ⚠ 모순 가능성
→ 추가 조사: "추론"의 정의 명확화 필요
```

---

## Layer 4: Confidence Tagging

### 규칙

**모든 사실에 신뢰도 태그를 부여하여 명확성을 확보합니다.**

**파일:** `.claude/skills/deep-research/SKILL.md:111-116`

```markdown
**Layer 4: Confidence Tagging**
- ✓✓ VERIFIED (다수 신뢰 소스)
- ✓ HIGH (단일 신뢰 소스)
- ~ LIKELY (추정)
- ? UNCERTAIN (불확실)
- ⚠ CONTRADICTED (모순)
```

**설정:** `config.json:61-67`

```json
"confidence_tags": {
  "verified": "✓✓",
  "high": "✓",
  "likely": "~",
  "uncertain": "?",
  "contradicted": "⚠"
}
```

### 태그 부여 기준

| 태그 | 의미 | 조건 | 신뢰도 범위 |
|------|------|------|-------------|
| **✓✓** | VERIFIED | 3개+ 고신뢰 소스 일치 | 0.85 - 1.00 |
| **✓** | HIGH | 1-2개 고신뢰 소스 | 0.70 - 0.84 |
| **~** | LIKELY | 추정, 전문가 의견 | 0.50 - 0.69 |
| **?** | UNCERTAIN | 출처 없음 또는 불확실 | 0.00 - 0.49 |
| **⚠** | CONTRADICTED | 소스 간 모순 | N/A |

### 사용 예시

#### ✓✓ VERIFIED (검증됨)

```markdown
✓✓ Transformer 아키텍처는 2017년 "Attention Is All You Need" 논문에서 제안되었다
   소스: arxiv.org/abs/1706.03762, nature.com, acm.org
   신뢰도: 0.96
```

**조건:**
- 3개 이상 독립 소스
- 모든 소스의 평균 신뢰도 > 0.80
- 모순 없음

#### ✓ HIGH (높은 신뢰도)

```markdown
✓ GPT-4의 학습 비용은 약 $100M으로 추정된다
   소스: techcrunch.com
   신뢰도: 0.72
```

**조건:**
- 1-2개 소스
- 소스 신뢰도 > 0.70
- 명백한 모순 없음

#### ~ LIKELY (가능성 높음)

```markdown
~ 양자 컴퓨터는 2030년까지 실용화될 것으로 예상된다
   소스: forbes.com (전문가 예측)
   신뢰도: 0.55
```

**조건:**
- 전문가 의견, 예측, 추정
- 확정적 증거 부족
- 신뢰도 중간

#### ? UNCERTAIN (불확실)

```markdown
? GPT-5의 출시 시기는 불명확하다
   (공식 발표 없음, 검색 결과 없음)
   신뢰도: 0.30
```

**조건:**
- 출처 없음
- 정보 부족
- 확인 불가

#### ⚠ CONTRADICTED (모순)

```markdown
⚠ "GPT-4는 AGI를 달성했다"는 주장에 대한 논란
   지지: wired.com, fortune.com (일부 전문가)
   반대: nature.com, science.org (대다수 전문가)

   → 현재로서는 합의 없음
   → 추가 조사 필요
```

**조건:**
- 소스 간 명백한 모순
- 상충하는 주장 존재
- 합의 부족

---

## 신뢰도 점수 시스템

### 소스별 신뢰도 점수

**설정:** `config.json:50-59`

```json
"credibility_scores": {
  "arxiv.org": 0.95,
  "nature.com": 0.98,
  "ieee.org": 0.95,
  "acm.org": 0.95,
  "github.com": 0.70,
  "medium.com": 0.50,
  "wikipedia.org": 0.75,
  "default": 0.30
}
```

### 점수 부여 기준

| 카테고리 | 점수 범위 | 소스 예시 |
|----------|----------|----------|
| **학술 논문** | 0.95 - 0.98 | arxiv, nature, ieee, acm |
| **공식 문서** | 0.90 - 0.95 | openai.com, github.com/official |
| **기술 뉴스** | 0.75 - 0.85 | techcrunch, theverge, wired |
| **일반 뉴스** | 0.60 - 0.75 | forbes, bloomberg |
| **위키백과** | 0.70 - 0.80 | wikipedia.org (교차 확인 필수) |
| **블로그/미디엄** | 0.40 - 0.60 | medium.com, 개인 블로그 |
| **알 수 없음** | 0.30 | 미등록 도메인 |

### 신뢰도 조정 규칙

**1. 최신성 가중치**

```python
age_weight = {
    "< 1년": 1.0,
    "1-3년": 0.9,
    "3-5년": 0.8,
    "> 5년": 0.7
}

adjusted_score = base_score × age_weight
```

**2. 인용 수 가중치 (학술 논문)**

```python
if citation_count > 1000:
    citation_boost = 1.1
elif citation_count > 100:
    citation_boost = 1.05
else:
    citation_boost = 1.0

adjusted_score = base_score × citation_boost
```

**3. 저자 신뢰도**

```python
if author in ["known_experts"]:
    author_boost = 1.1
else:
    author_boost = 1.0

adjusted_score = base_score × author_boost
```

### 종합 신뢰도 계산

**최종 공식:**

```python
def final_confidence(claim):
    # 1. 소스 수 기반 베이스 점수
    if len(claim.sources) >= 3:
        base = 0.95
    elif len(claim.sources) == 2:
        base = 0.80
    elif len(claim.sources) == 1:
        base = 0.60
    else:
        base = 0.30

    # 2. 소스 신뢰도 평균
    avg_credibility = sum(s.credibility for s in claim.sources) / len(claim.sources)

    # 3. 모순 페널티
    if claim.has_contradiction:
        contradiction_penalty = 0.5
    else:
        contradiction_penalty = 1.0

    # 4. 최종 점수
    final = base × avg_credibility × contradiction_penalty

    # 5. 태그 부여
    if final >= 0.85:
        return "✓✓", final
    elif final >= 0.70:
        return "✓", final
    elif final >= 0.50:
        return "~", final
    elif claim.has_contradiction:
        return "⚠", final
    else:
        return "?", final
```

---

## 검증 워크플로우

### 단계별 실행

```
1. 정보 수집 (EXECUTE 단계)
   ↓
2. Source Grounding
   - 각 주장에 출처 태그
   - 출처 없으면 [?]
   ↓
3. Cross-Validation
   - 2-3개 소스 교차 확인
   - 신뢰도 점수 계산
   ↓
4. Self-Consistency
   - 다각도 검증
   - 내부 모순 탐지
   ↓
5. Confidence Tagging
   - 최종 태그 부여 (✓✓/✓/~/? /⚠)
   - findings.md에 저장
```

### 예시: 완전한 검증 과정

**원시 정보 (WebSearch 결과):**

```
검색: "GPT-4 release date"

결과:
- openai.com: "March 14, 2023"
- techcrunch.com: "March 14, 2023"
- theverge.com: "Released on March 14"
```

**Layer 1: Source Grounding**

```markdown
GPT-4는 2023년 3월 14일 출시되었다
소스: openai.com, techcrunch.com, theverge.com
```

**Layer 2: Cross-Validation**

```python
sources = [
    {"domain": "openai.com", "credibility": 0.98},
    {"domain": "techcrunch.com", "credibility": 0.85},
    {"domain": "theverge.com", "credibility": 0.80}
]

source_count = 3  # → base_score = 0.95
avg_credibility = (0.98 + 0.85 + 0.80) / 3 = 0.88

confidence = 0.95 × 0.88 = 0.84
```

**Layer 3: Self-Consistency**

```markdown
교차 확인:
- 모든 소스가 동일한 날짜 제시
- 공식 블로그(openai.com)와 뉴스 매체 일치
- 모순 없음 ✓
```

**Layer 4: Confidence Tagging**

```markdown
최종 신뢰도: 0.84
태그: ✓✓ (verified, 3+ 소스)

출력:
✓✓ GPT-4는 2023년 3월 14일 출시되었다
   소스: openai.com, techcrunch.com, theverge.com
   신뢰도: 0.84
```

---

## 모순 처리

### 모순 탐지

**시나리오:**

```
주장: GPT-4의 파라미터 수

소스 A (techcrunch.com): 175B
소스 B (forbes.com): 220B
소스 C (openai.com): 비공개
```

**처리:**

```markdown
⚠ GPT-4의 파라미터 수에 대한 정보는 모순됨

   주장 A: 175B 파라미터 (techcrunch.com, 신뢰도: 0.85)
   주장 B: 220B 파라미터 (forbes.com, 신뢰도: 0.70)
   주장 C: 공식적으로 비공개 (openai.com, 신뢰도: 0.98)

   분석:
   - openai.com(공식)이 비공개라고 명시
   - 뉴스 매체의 추정치는 불일치

   결론:
   ✓ GPT-4의 파라미터 수는 공식적으로 비공개이다 (openai.com)
   ~ 일부 추정치는 175B-220B 범위 (비공식)
```

### 모순 해결 전략

| 전략 | 적용 시점 | 방법 |
|------|----------|------|
| **공식 소스 우선** | 공식 발표 vs 추정 | 공식 소스 신뢰 |
| **최신 정보 우선** | 시간에 따라 변경 | 최신 날짜 우선 |
| **다수결** | 여러 소스 분산 | 다수 의견 채택 |
| **보류** | 해결 불가 | 양측 모두 표시 |

---

## 검증 체크리스트

### VERIFY 단계에서 확인할 사항

- [ ] 모든 주장에 출처가 명시되어 있는가?
- [ ] 출처 없는 주장은 [?] 태그가 있는가?
- [ ] 중요 주장은 2개 이상 소스로 교차 확인했는가?
- [ ] 각 소스의 신뢰도 점수를 확인했는가?
- [ ] 소스 간 모순을 확인했는가?
- [ ] 다른 각도에서 재검토했는가?
- [ ] 최종 신뢰도 태그(✓✓/✓/~/? /⚠)를 부여했는가?
- [ ] findings.md에 태그와 함께 저장했는가?

---

**다음:** [06-loop-drift.md](./06-loop-drift.md) - Loop Drift 방지 메커니즘
