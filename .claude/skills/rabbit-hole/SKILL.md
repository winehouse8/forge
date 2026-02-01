---
name: rabbit-hole
description: "Rabbit-Hole Research Framework v5. 외부 스크립트 기반 무한 루프."
argument-hint: [research question]
allowed-tools: WebSearch, WebFetch, Read, Write, Edit, Bash, Glob, Grep
---

# 🐰 Rabbit-Hole v5

> **실행 방법:** 터미널에서 `./rabbit-hole.sh "질문"` 실행
> 이 문서는 각 iteration에서 Claude가 수행할 작업을 정의합니다.

---

## 핵심 규칙

```
1. 한 번 호출 = 한 iteration (SPAWN→SELECT→EXPLORE→SAVE)
2. 외부 스크립트(rabbit-hole.sh)가 반복 호출
3. 모든 상태는 .research/current/에 저장
```

---

## 사이클 (1회 실행)

```
┌────────────────────────────────────────────┐
│  SPAWN → SELECT → EXPLORE → SAVE → 종료   │
│                                            │
│  (rabbit-hole.sh가 다시 호출)              │
└────────────────────────────────────────────┘
```

---

## 시작: 상태 로드 (필수)

**⚠️ 질문 요청 금지 - 항상 파일에서 읽기**

```
1. Read .research/current/holes.json
   → question, iteration, pending 확인
2. Read .research/current/summary.md
   → 지식 맵 확인
3. SPAWN 진행 (질문 요청 절대 금지)
```

**holes.json 없으면:** 에러 출력 후 종료
```
❌ No session found. Run: ./rabbit-hole.sh "질문"
```

---

## 1. SPAWN

```
pending < 3이면 holes 생성 → 아니면 통과
```

### 생성 규칙

| 상황 | 생성 전략 |
|------|----------|
| claim 없음 | explore 6개 (정의, 범위, 비교, 사례, 한계, 적용) |
| claim 있음 | **coverage 2 + verify 2 + trace 2** |

**Hole 타입:**
- **coverage**: 아직 다루지 않은 영역 탐색
- **verify**: 기존 claim의 반증/한계 검색
- **trace**: 원문/데이터/스펙 추적

각 hole:
```json
{
  "id": "hole_{next_id}",
  "type": "explore|verify|trace",
  "question": "구체적 질문",
  "target_claim": "claim_N (verify/trace일 경우)",
  "interest": "high|medium|low"
}
```

Write holes.json (pending에 추가, next_id 증가)

---

## 2. SELECT

```
pending에서 interest 높은 hole 선택
```

우선순위: high > medium > low

선택한 hole을 "current_hole"로 기억

---

## 3. EXPLORE

### 컨텍스트 로드 규칙

| hole.type | 로드할 파일 |
|-----------|------------|
| explore | summary.md만 |
| verify | summary.md + target claim + **해당 claim의 evidence들** |
| trace | summary.md + target claim + **해당 claim의 evidence들** |

**Evidence 찾기:**
claim 파일 내 `Evidence:` 섹션에서 ev_N 참조 확인 → 해당 파일들 로드

### 검색

WebSearch로 2-3개 쿼리:
- **explore**: 넓게 탐색
- **verify**: 반증/한계 ("X fails", "X limitations", "X problems")
- **trace**: 원문/출처 ("X original paper", "X official spec", "X dataset")

### 판단

각 결과를 **기존 Claims와 비교**:

| 판단 | 조건 | 행동 |
|------|------|------|
| **NEW** | 새 정보 | claim 생성 |
| **SUPPORTS** | 기존 claim 지지 | claim 강화 (+0.1~0.3) |
| **REBUTS** | 기존 claim 반박 | claim 약화 (-0.3) |
| **QUALIFIES** | 뒤집지 않지만 조건 추가 | claim에 "단, ~" 추가 |
| **SKIP** | 중복 또는 Authority < 0.3 | 무시 |

**Authority 기준:**
- 논문/공식문서/스펙: 0.8-1.0
- 블로그/리뷰: 0.4-0.7
- 출처불명: < 0.3 (SKIP)

---

## 4. SAVE

### 순서

1. **Evidence 저장**: `.research/current/evidence/ev_{N}.md` (N = holes.json의 next_id 사용 후 증가)
2. **Claim 생성/갱신**: `.research/current/claims/claim_{N}.md`
3. **Summary 갱신**: `.research/current/summary.md`
4. **holes.json 갱신**: pending → explored, iteration++
5. **상태 출력**:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🐰 Iteration {N}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🕳️ 탐색: {hole.question}

📥 발견:
  - [NEW/SUPPORTS/REBUTS/QUALIFIES] ...

📋 현재 상태:
  - strong: ...
  - uncertain: ...
  - 모름: ...

⏳ pending: {N}개
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Evidence 파일 포맷

```markdown
# Evidence {N}

## Source
- URL: https://...
- Type: paper | official_doc | blog | review
- Authority: 0.8

## Summary
핵심 내용 요약 (3-5줄)

## Quotes
> 원문 인용 (있으면)

## Related Claims
- claim_4: SUPPORTS
- claim_7: REBUTS
```

### Claim 파일 포맷

```markdown
# Claim {N}: {제목}

## Statement
주장 문장 (1-2줄)

단, [조건1], [조건2] (QUALIFIES된 경우)

## Strength
0.7 (uncertain)

## Evidence
- ev_3: 출처 요약
- ev_7: 출처 요약

## Rebuttals
- ev_12: 반박 내용 요약
```

### Claim Strength 계산

```
+0.3 per 1차 출처 (논문/공식문서)
+0.1 per 2차 출처 (블로그/리뷰)
-0.3 per rebuttal
→ clamp(0.0, 1.0)

> 0.8: strong
> 0.4: uncertain
≤ 0.4: weak
```

### QUALIFIES 처리

claim에 조건 추가:
```markdown
## Statement
기존 주장 문장

단, [조건1], [조건2]
```

### Summary.md 갱신 규칙

**Claims 테이블:**
- status별 정렬 (strong → uncertain → weak)
- Statement는 1줄 요약 (조건 포함)
- Evidence는 개수만

**Pending Holes:**
- interest 높은 순 상위 5개

**Open Gaps:**
- 아직 claim 없는 핵심 영역

**Footer:**
- iteration, claims 수, evidence 수, explored 수

**목표: 200줄 이내**

---

## 완료 조건

iteration ≥ 50 AND pending = 0일 때:
```
<complete>DONE</complete>
```

---

## 파일 구조

```
.research/
├── current -> sessions/research_YYYYMMDD_HHMMSS/
└── sessions/
    └── research_YYYYMMDD_HHMMSS/
        ├── summary.md
        ├── holes.json
        ├── claims/claim_{N}.md
        └── evidence/ev_{N}.md
```

---

## 한 장 요약

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  🐰 RABBIT-HOLE v5                          ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃  1회 호출 = 1 iteration                     ┃
┃                                             ┃
┃  SPAWN: pending<3 → 6 holes 생성            ┃
┃    • explore 6 (초기)                       ┃
┃    • coverage 2 + verify 2 + trace 2        ┃
┃                                             ┃
┃  SELECT: interest 높은 hole 선택            ┃
┃                                             ┃
┃  EXPLORE: 타입별 컨텍스트 로드              ┃
┃    • explore → summary.md                   ┃
┃    • verify/trace → + claim + evidence      ┃
┃                                             ┃
┃  판정: NEW/SUPPORTS/REBUTS/QUALIFIES/SKIP   ┃
┃                                             ┃
┃  SAVE: ev → claim → summary → holes → 출력 ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```
