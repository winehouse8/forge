---
name: rh-report
description: 토끼굴 탐험 결과를 종합하여 원래 질문에 대한 최종 답변을 생성합니다.
argument-hint: (인자 없음)
allowed-tools: Read, Glob
---

# 🎯 rh-report: 연구 결과 종합 보고서

연구 세션의 모든 자료를 읽고, 원래 질문에 대한 종합적인 답변을 도출합니다.

---

## 1단계: 데이터 로드

### 필수 파일 읽기

```
Read .research/current/holes.json
  → question: 원래 질문
  → iteration: 수행된 iteration 수
  → explored: 탐색 완료된 holes

Read .research/current/summary.md
  → Claims 테이블 (전체 주장 목록)
  → Open Gaps (아직 모르는 것)

Glob .research/current/claims/*.md → 모든 claim 파일 읽기
Glob .research/current/evidence/*.md → 모든 evidence 파일 읽기
```

---

## 2단계: 자료 구조 이해

### holes.json 구조
```json
{
  "question": "원래 연구 질문",
  "iteration": 13,
  "pending": [],
  "explored": [
    {"id": "hole_1", "result": "claims 1-3"},
    ...
  ]
}
```

### claim 파일 구조 (claims/claim_{N}.md)
```markdown
# Claim {N}: {제목}

## Statement
주장 문장
단, [조건] (QUALIFIES된 경우)

## Strength
0.8 (strong)  ← 신뢰도 지표

## Evidence
- ev_3: 지지 증거 요약
- ev_7: 지지 증거 요약

## Rebuttals
- ev_12: 반박 증거 요약
```

**Strength 해석:**
- **> 0.8 (strong)**: 높은 신뢰도, 다수 출처 확인
- **0.4-0.8 (uncertain)**: 중간 신뢰도, 추가 검증 필요
- **≤ 0.4 (weak)**: 낮은 신뢰도, 회의적 접근 필요

### evidence 파일 구조 (evidence/ev_{N}.md)
```markdown
# Evidence {N}

## Source
- URL: https://...
- Type: paper | official_doc | blog
- Authority: 0.8

## Summary
핵심 내용 요약

## Quotes
> 원문 인용

## Related Claims
- claim_4: SUPPORTS
- claim_7: REBUTS
```

**Authority 해석:**
- **0.8-1.0**: 논문, 공식 문서 (1차 출처)
- **0.4-0.7**: 블로그, 리뷰 (2차 출처)
- **< 0.4**: 출처 불명 (낮은 신뢰)

---

## 3단계: 비판적 분석 (Extended Thinking 필수)

### 3.1 Claims 분류

```
Strong Claims (신뢰 가능):
  - claim_1: ...
  - claim_4: ...

Uncertain Claims (추가 검증 필요):
  - claim_7: ...

Weak Claims (회의적 접근):
  - claim_12: ...

Qualified Claims (조건부):
  - claim_3: "X는 효과적이다. 단, Y 환경에서만"
```

### 3.2 Evidence 교차 검증

```
일치하는 증거 (Convergent):
  - ev_3, ev_7, ev_11 → 모두 claim_4 지지

충돌하는 증거 (Divergent):
  - ev_5 ↔ ev_9 → claim_7에 대해 상반된 입장

미검증 영역 (Gaps):
  - Open Gap 1: ...
  - Open Gap 2: ...
```

### 3.3 사고 도구 적용

| 도구 | 적용 |
|------|------|
| **오컴의 면도날** | 복잡한 설명보다 단순한 설명 우선 |
| **베이지안 추론** | evidence 누적에 따른 확신도 계산 |
| **반증 가능성** | Rebuttals 적극 고려 |
| **변증법적 사고** | 충돌 증거 → 통합 결론 |

---

## 4단계: 종합 결론 도출

### 추론 과정 (반드시 명시)

```
1. 원래 질문 재확인:
   "{question}"

2. 핵심 발견 나열:
   - Strong claim들 중심
   - Qualified 조건 포함

3. 증거 기반 논증:
   - 각 발견의 evidence 연결
   - Authority 높은 출처 우선

4. 반론 고려:
   - Rebuttals 검토
   - Weak claims의 한계 인정

5. 최종 결론:
   - 질문에 대한 직접적 답변
   - 확신도 명시
```

---

## 5단계: 보고서 출력

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 연구 결과 보고서
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 원래 질문
"{question}"

## 연구 규모
- Iterations: {N}
- Claims: {N}개 (strong {N}, uncertain {N}, weak {N})
- Evidence: {N}개

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 종합 결론

[질문에 대한 직접적이고 명확한 답변]

**확신도: 0.XX**
- ✓✓ (0.85+): 다수 신뢰 출처 일치
- ✓ (0.70-0.84): 신뢰 출처 확인
- ~ (0.50-0.69): 추정
- ? (<0.50): 불확실

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 핵심 발견 (Strong Claims)

1. **{claim 제목}** (strength: 0.9)
   - {statement}
   - 근거: ev_3 (논문), ev_7 (공식문서)

2. **{claim 제목}** (strength: 0.85)
   - {statement}
   - 근거: ev_11 (논문)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 조건부 발견 (Qualified Claims)

1. **{claim 제목}**
   - {statement}
   - **단, {조건1}, {조건2}**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 불확실한 영역

1. **{uncertain claim}**
   - 현재 상태: {요약}
   - 추가 검증 필요: {이유}

2. **{open gap}**
   - 아직 탐색되지 않음

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 반론 및 한계

- {rebuttal 1}: {내용}
- {한계점}: {내용}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 추론 과정

[위 결론에 도달한 논리적 과정 설명]

1. {전제 1} + {전제 2} → {중간 결론}
2. {중간 결론} + {추가 증거} → {최종 결론}
3. {반론 고려} → {결론 조정}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 참고 출처 (Authority 순)

1. [논문/공식문서] {제목} - {URL}
2. [논문/공식문서] {제목} - {URL}
3. [블로그/리뷰] {제목} - {URL}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 핵심 원칙

1. **질문 중심**: 모든 분석은 원래 질문에 답하기 위함
2. **증거 기반**: 주장은 반드시 evidence와 연결
3. **신뢰도 명시**: 모든 claim의 strength 표시
4. **반론 포함**: Rebuttals를 무시하지 않음
5. **한계 인정**: 불확실한 영역 솔직히 표시
6. **추론 투명성**: 결론에 도달한 과정 명시
