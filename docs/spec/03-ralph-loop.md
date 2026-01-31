# Ralph Loop 패턴

**문서:** 03-ralph-loop.md
**최종 수정일:** 2026-01-31
**관련 파일:** `.claude/hooks/stop-hook.py`, `.claude/skills/deep-research/SKILL.md:201-265`

---

## 목차
- [Ralph Loop란](#ralph-loop란)
- [구현 메커니즘](#구현-메커니즘)
- [종료 조건](#종료-조건)
- [자기 재귀 호출](#자기-재귀-호출)
- [검증 결과](#검증-결과)

---

## Ralph Loop란

### 정의

**Ralph Loop**는 LLM의 주관적 "완료" 판단을 무시하고, **객관적 조건만**으로 종료를 제어하는 패턴입니다.

### 문제점: LLM의 조기 종료

**기존 문제:**
```
질문: "양자 컴퓨팅에 대해 조사해줘"

LLM 내부 판단:
- Iteration 1: "기본 정보 수집 완료"
- Iteration 2: "주요 논문 몇 개 찾음"
- Iteration 3: "충분히 답변 가능" ← 주관적 판단
→ "완료되었습니다" 출력
→ 세션 종료
```

**문제:**
- ❌ LLM이 "충분하다"고 느끼면 종료
- ❌ 사용자가 원하는 깊이까지 탐색 안 함
- ❌ 95% 확신도에서도 반증 탐색 중단

---

### 해결책: Ralph Loop

**객관적 제어:**
```
질문: "양자 컴퓨팅에 대해 조사해줘"

종료 조건:
- iteration >= 100 (최대 횟수)
- status == "completed" (사용자가 명시적으로 설정)
- status == "stopped_by_user" (q 키)
- budget_exceeded (예산 초과)

→ 위 조건 만족 전까지 **무조건 계속**
→ LLM의 "완료" 판단 무시
```

---

## 구현 메커니즘

### 1. Stop Hook (종료 차단)

**파일:** `.claude/hooks/stop-hook.py:23-83`

```python
def main():
    state = load_state()

    # 상태 파일 없음 → 연구 세션 아님
    if state is None:
        sys.exit(0)  # 종료 허용

    status = state.get("status", "initialized")

    # status가 "running"이 아니면 종료 허용
    if status != "running":
        sys.exit(0)

    # status="running" → 종료 차단
    output = {
        "decision": "block",
        "reason": "🔬 Research in progress..."
    }
    print(json.dumps(output))
    sys.exit(1)  # Non-zero exit code = 종료 차단
```

**동작 원리:**

1. **Claude Code 종료 시도**
   ```
   사용자: [Ctrl+C] 또는 LLM: "완료되었습니다"
   ```

2. **Stop Hook 실행**
   ```bash
   # .claude/settings.json에 정의됨
   "hooks": {
     "Stop": [{
       "hooks": [{
         "type": "command",
         "command": "python3 .claude/hooks/stop-hook.py"
       }]
     }]
   }
   ```

3. **Exit Code 확인**
   - `exit 0`: 종료 허용
   - `exit 1`: 종료 차단 (Ralph Loop 유지)

4. **결과**
   - 차단된 경우: Claude Code 계속 실행
   - 메인 스킬이 자기 재귀 호출
   - 새로운 iteration 시작

---

### 2. 자기 재귀 호출

**파일:** `.claude/skills/deep-research/SKILL.md:201-265`

```markdown
## 9. LOOP - 다음 Iteration 자동 시작 (Ralph Loop)

### Step 1: 종료 조건 체크

state.json을 읽어서 다음을 확인:
- status = state["status"]
- current = state["iteration"]["current"]
- max_iter = state["iteration"]["max"]
- budget = state["metrics"]["cost_estimate_usd"]

### Step 2: 종료 결정

다음 중 **하나라도** 해당하면 종료:
- ❌ status가 "completed", "paused", "stopped_by_user", "budget_exceeded"
- ❌ current >= max_iter
- ❌ budget > 10.0

**그 외 모든 경우: 계속 실행**

### Step 3: 다음 Iteration 호출

종료 조건을 만족하지 않으면:
→ Skill(skill="deep-research", args="")
```

**실제 구현:**

```
[Iteration N 완료]

스킬 내부 로직:
1. state.json 읽기
2. status 확인: "running"
3. iteration 확인: 5 / 100
4. budget 확인: $0.85 / $10.00
5. 종료 조건 불만족 → 계속 실행

출력:
"다음 iteration을 시작합니다..."

도구 호출:
Skill(skill="deep-research", args="")
    ↓
새로운 컨텍스트로 Iteration N+1 시작
```

---

## 종료 조건

### 종료 허용 조건 (OR 조건)

| 조건 | 설명 | 확인 위치 |
|------|------|----------|
| `status="completed"` | 연구 완료 | Stop Hook, 메인 스킬 |
| `status="paused"` | 일시정지 (s 키) | Stop Hook |
| `status="stopped_by_user"` | 사용자 중단 (q 키) | Stop Hook |
| `status="budget_exceeded"` | 예산 초과 | Stop Hook |
| `iteration >= max` | 최대 횟수 도달 | 메인 스킬 |
| `budget > limit` | 예산 초과 | 메인 스킬 |

**하나라도 만족 → 종료 허용**

---

### 종료 차단 조건

| 조건 | 설명 | 결과 |
|------|------|------|
| `status="running"` | 연구 진행 중 | Stop Hook이 exit 1 반환 |
| `status="initialized"` | 아직 시작 안 함 | 종료 허용 (연구 세션 아님) |
| 파일 없음 | `.research/state.json` 없음 | 종료 허용 (일반 세션) |

---

### 종료 흐름도

```
Claude Code 종료 시도
       ↓
Stop Hook 실행
       ↓
state.json 읽기
       ↓
   파일 있음?
   ┌─No─→ exit 0 (일반 세션, 종료 허용)
   └─Yes─→ status 확인
              ↓
        status="running"?
        ┌─No─→ exit 0 (종료 허용)
        └─Yes─→ exit 1 (종료 차단)
                   ↓
            Claude Code 계속 실행
                   ↓
            메인 스킬 재귀 호출
                   ↓
            새 iteration 시작
```

---

## 자기 재귀 호출

### Skill Tool 사용

**메커니즘:**

```
Iteration N:
    [9단계 사이클 실행]
           ↓
    9. LOOP 단계
           ↓
    종료 조건 체크
           ↓
    Skill("deep-research", "")  ← 자기 자신을 호출
           ↓
Iteration N+1:
    새로운 컨텍스트로 시작
    (이전 대화 히스토리 없음)
           ↓
    1. LOAD 단계
    → state.json에서 이전 상태 로드
    → 이전 iteration의 결과 확인
           ↓
    [9단계 사이클 다시 실행]
```

---

### 컨텍스트 격리

**각 iteration은 독립적:**

| 항목 | Iteration N | Iteration N+1 |
|------|------------|--------------|
| 대화 히스토리 | ✅ 있음 | ❌ 없음 (새 컨텍스트) |
| state.json | ✅ 읽기/쓰기 | ✅ 읽기/쓰기 |
| findings.md | ✅ 누적 | ✅ 계속 누적 |
| 메모리 | 32K tokens | 초기화 (0부터 시작) |

**장점:**
- 메모리 누적 방지 (컨텍스트 폭발 없음)
- 각 iteration 독립 실행
- state.json을 통한 상태 전달

---

## 검증 결과

### Stop Hook 테스트

| 테스트 케이스 | 예상 | 실제 | 상태 |
|--------------|------|------|------|
| 파일 없음 | Exit 0 | Exit 0 | ✅ Pass |
| status="initialized" | Exit 0 | Exit 0 | ✅ Pass |
| status="running" | Exit 1 | Exit 1 | ✅ Pass |
| status="completed" | Exit 0 | Exit 0 | ✅ Pass |
| status="paused" | Exit 0 | Exit 0 | ✅ Pass |

---

### Ralph Loop 동작 확인

**실제 연구 로그:**

```
Iteration 1:
  - 검색 실행
  - findings.md 업데이트
  - Skill("deep-research") 호출
  ✅ 자동으로 Iteration 2 시작

Iteration 2:
  - 이전 발견 확인
  - 새로운 검색 실행
  - Skill("deep-research") 호출
  ✅ 자동으로 Iteration 3 시작

Iteration 3:
  - 계속...
```

**결과:**
- ✅ 3회 연속 자동 iteration 실행 성공
- ✅ 사용자 개입 없이 자동 진행
- ✅ Stop Hook이 종료 차단

---

## 디버깅

### Stop Hook 디버깅

**테스트 명령:**

```bash
# 1. 상태 파일 생성
cat > .research/state.json << EOF
{
  "status": "running",
  "iteration": {"current": 5, "max": 100}
}
EOF

# 2. Hook 실행
echo '{}' | python3 .claude/hooks/stop-hook.py
echo "Exit code: $?"

# 예상: Exit code 1 (차단)
```

---

### 무한 루프 방지

**안전장치:**

```python
# stop-hook.py:60-65
elif hook_input.get("stop_hook_active", False):
    # Loop drift 탐지
    if iteration > 10 and consecutive_same > 5:
        should_stop = True
        reason = "Loop drift detected"
```

**동작:**
- 10회 이상 iteration 실행
- 동일한 행동 5회 반복
- → 강제 종료

---

## 모범 사례

### ✅ 올바른 사용

```python
# 스킬 내부 (LOOP 단계)
if status == "running" and iteration < max_iter:
    # 계속 실행
    Skill("deep-research", "")
else:
    # 종료
    print("연구 완료")
```

---

### ❌ 잘못된 사용

```python
# 절대 금지!
if confidence > 0.95:
    print("충분히 조사했습니다. 완료.")
    # ← LLM 주관 판단으로 종료 시도
```

**문제:**
- Ralph Loop 패턴 위반
- 조기 종료 발생
- 사용자가 원하는 깊이까지 탐색 안 함

---

**다음:** [04-research-cycle.md](./04-research-cycle.md) - 9단계 연구 사이클 상세
