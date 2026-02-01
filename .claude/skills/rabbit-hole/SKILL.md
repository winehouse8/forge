---
name: rabbit-hole
description: "Rabbit-Hole Research Framework v4. 4단계 사이클 + Stop Hook 자동 반복."
argument-hint: [research question]
allowed-tools: WebSearch, WebFetch, Read, Write, Edit, Bash, Glob, Grep
---

# 🐰 Rabbit-Hole v4

## 핵심 규칙 (3개)

```
1. INIT: 인자 있으면 새 세션, 없으면 기존 세션 로드
2. 사이클: SPAWN → SELECT → EXPLORE → SAVE (4단계 반복)
3. 반복: Stop Hook이 SAVE 후 자동으로 SPAWN부터 재시작
```

---

## 사이클

```
┌──────────────────────────────────────┐
│  SPAWN → SELECT → EXPLORE → SAVE    │
│    ↑                          ↓     │
│    └────── Stop Hook ─────────┘     │
└──────────────────────────────────────┘
```

---

## INIT (첫 회만)

### 인자 있으면 (새 세션)

```bash
mkdir -p .research/sessions && \
SESSION_ID="research_$(date +%Y%m%d_%H%M%S)" && \
mkdir -p ".research/sessions/${SESSION_ID}/claims" && \
mkdir -p ".research/sessions/${SESSION_ID}/evidence" && \
ln -sfn "sessions/${SESSION_ID}" .research/current && \
echo "${SESSION_ID}" > .research/current/.session_id
```

Write `.research/current/holes.json`:
```json
{
  "question": "{$ARGUMENTS}",
  "pending": [],
  "explored": [],
  "next_id": 1,
  "iteration": 0
}
```

### 인자 없으면 (이어하기)

Read `.research/current/holes.json` → 상태 확인 후 SPAWN으로

---

## 1. SPAWN

```
holes.json 읽기 → pending < 3이면 holes 생성 → 아니면 통과
```

### 생성 규칙

**pending < 3일 때만 실행:**

Extended Thinking으로 **6개** hole 생성:

| 상황 | 생성 전략 |
|------|----------|
| claim 없음 | explore 6개 (정의, 범위, 비교, 사례, 한계, 적용) |
| claim 있음 | coverage 2 + verify 2 + falsify 2 |

각 hole:
```json
{
  "id": "hole_{next_id}",
  "type": "explore|verify|trace",
  "question": "구체적 질문",
  "interest": "high|medium|low"
}
```

Write holes.json (pending에 추가, next_id 증가)

---

## 2. SELECT

```
holes.json에서 interest 높은 hole 선택
```

우선순위: high > medium > low

선택한 hole을 "current_hole"로 기억

---

## 3. EXPLORE

### 검색

WebSearch로 2-3개 쿼리:
- explore: 넓게
- verify: 반증 ("X fails", "X limitations")
- trace: 원문 ("X original paper")

### 판단

각 결과에 대해:

| 판단 | 조건 | 행동 |
|------|------|------|
| NEW | 새 정보 | claim 생성 |
| SUPPORTS | 기존 claim 지지 | claim 강화 |
| REBUTS | 기존 claim 반박 | claim 약화 |
| SKIP | 중복 또는 Authority < 0.3 | 무시 |

Authority 기준:
- 논문/공식문서: 0.8-1.0
- 블로그/리뷰: 0.4-0.7
- 출처불명: < 0.3 (SKIP)

---

## 4. SAVE

### 순서

1. **Evidence 저장**: `.research/current/evidence/ev_{N}.md`
2. **Claim 생성/갱신**: `.research/current/claims/claim_{N}.md`
3. **holes.json 갱신**: pending → explored, iteration++
4. **상태 출력**:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🐰 Iteration {N}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🕳️ 탐색: {hole.question}

📥 발견:
  - [NEW/SUPPORTS/REBUTS] ...

📋 현재 답:
  - strong: ...
  - uncertain: ...
  - 모름: ...

⏳ pending holes: {N}개
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Claim Strength 계산

```
+0.3 per 1차 출처
+0.1 per 2차 출처
-0.3 per rebuttal
→ clamp(0.0, 1.0)

> 0.8: strong
> 0.4: uncertain
≤ 0.4: weak
```

---

## 자동 반복 (Stop Hook)

SAVE 완료 후:
1. Claude 응답 종료 시도
2. Stop Hook 트리거
3. holes.json 확인
4. `decision: block` + `stopReason: "SPAWN부터 시작"`
5. Claude가 SPAWN 실행

**종료 조건:**
- iteration ≥ 100
- 사용자 Ctrl+C

---

## 파일 구조

```
.research/current/
├── holes.json          ← 상태 관리
├── claims/claim_{N}.md ← 주장
└── evidence/ev_{N}.md  ← 근거
```

---

## 한 장 요약

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  🐰 RABBIT-HOLE v4                          ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃  INIT (첫 회) → [SPAWN→SELECT→EXPLORE→SAVE] ┃
┃                    ↑                  ↓     ┃
┃                    └── Stop Hook ─────┘     ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃  SPAWN: pending < 3 → 6 holes               ┃
┃  SELECT: interest 높은 hole                 ┃
┃  EXPLORE: WebSearch → NEW/SUPPORTS/REBUTS   ┃
┃  SAVE: evidence → claim → 출력              ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```
