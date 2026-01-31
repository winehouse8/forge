# 아키텍처

**문서:** 02-architecture.md
**최종 수정일:** 2026-01-31
**관련 파일:** `research.sh`, `.claude/hooks/stop-hook.py`, `.claude/skills/deep-research/SKILL.md`

---

## 목차
- [이중 루프 아키텍처](#이중-루프-아키텍처)
- [컴포넌트 구조](#컴포넌트-구조)
- [데이터 흐름](#데이터-흐름)
- [도구 사용 정책](#도구-사용-정책)

---

## 이중 루프 아키텍처

### 개요

Pathfinder는 **외부 루프**와 **내부 루프** 두 계층으로 구성됩니다.

```
┌────────────────────────────────────────────────────┐
│  External Loop (Bash - research.sh)                │
│  ┌──────────────────────────────────────────────┐  │
│  │  while iteration < max:                      │  │
│  │    check_loop_drift()                        │  │
│  │    check_budget()                            │  │
│  │    claude /deep-research ───────┐            │  │
│  │    check_user_input()           │            │  │
│  │    iteration++                  │            │  │
│  └─────────────────────────────────┼────────────┘  │
└────────────────────────────────────┼───────────────┘
                                     ↓
┌────────────────────────────────────────────────────┐
│  Stop Hook (Python - stop-hook.py)                 │
│  ┌──────────────────────────────────────────────┐  │
│  │  if state.json not exists:                   │  │
│  │      exit 0  # 일반 세션                      │  │
│  │  if status != "running":                     │  │
│  │      exit 0  # 연구 비활성                    │  │
│  │  else:                                       │  │
│  │      exit 1  # 종료 차단 (Ralph Loop)        │  │
│  └──────────────────────────────────────────────┘  │
└────────────────────────────────────┬───────────────┘
                                     ↓
┌────────────────────────────────────────────────────┐
│  Internal Loop (Claude Code - deep-research)       │
│  ┌──────────────────────────────────────────────┐  │
│  │  1. LOAD    - Read .research/*.json          │  │
│  │  2. REFLECT - Extended Thinking              │  │
│  │  3. PLAN    - Generate 3-5 queries           │  │
│  │  4. EXECUTE - Parallel WebSearch/Fetch       │  │
│  │  5. VERIFY  - 4-layer validation             │  │
│  │  6. SYNTHESIZE - Update knowledge graph      │  │
│  │  7. SAVE    - Write all state files          │  │
│  │  8. OUTPUT  - Display progress               │  │
│  │  9. LOOP    - Check termination:             │  │
│  │              if should_continue:              │  │
│  │                  Skill("deep-research")  ←───┘  │
│  └──────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────┘
```

---

### 외부 루프 (research.sh)

**역할:**
- Iteration 횟수 제어
- Loop drift 탐지
- 예산 감시
- 사용자 인터럽트 처리 (q/s 키)

**파일:** `research.sh:117-204`

**핵심 로직:**
```bash
while [ $iteration -lt $MAX_ITERATIONS ]; do
    # Iteration 카운터 업데이트
    jq --argjson i "$((iteration + 1))" \
        '.iteration.current = $i | .status = "running"' \
        "$STATE_FILE" > tmp.json && mv tmp.json "$STATE_FILE"

    # 안전 체크들
    check_loop_drift || true
    check_budget || break
    check_progress

    # Claude Code 스킬 실행
    claude /deep-research "Continue research iteration #$((iteration + 1))"

    # 상태 파일 체크
    status=$(jq -r '.status' "$STATE_FILE")
    if [ "$status" = "completed" ] || [ "$status" = "paused" ]; then
        break
    fi

    # 사용자 인터럽트 체크
    read -t 1 -n 1 input 2>/dev/null
    case "$input" in
        q|Q) jq '.status = "stopped_by_user"' "$STATE_FILE" && break ;;
        s|S) jq '.status = "paused"' "$STATE_FILE" && break ;;
    esac

    ((iteration++))
done
```

---

### Stop Hook (stop-hook.py)

**역할:**
- Ralph Loop 패턴 강제
- Claude Code 종료 차단 (status="running"일 때만)

**파일:** `.claude/hooks/stop-hook.py:23-83`

**핵심 로직:**
```python
def main():
    state = load_state()

    # 0. 상태 파일이 없으면 일반 세션 → 종료 허용
    if state is None:
        print(json.dumps({"decision": "allow", "reason": "No active research session"}))
        sys.exit(0)

    status = state.get("status", "initialized")

    # 1. status가 "running"이 아니면 종료 허용
    if status != "running":
        sys.exit(0)

    # 2. status="running"일 때만 종료 차단
    print(json.dumps({"decision": "block", "reason": "Research in progress..."}))
    sys.exit(1)  # Non-zero exit code blocks termination
```

**동작 원리:**
1. Claude Code가 세션 종료를 시도
2. `.claude/settings.json`의 Stop Hook 실행
3. Stop Hook이 `.research/state.json` 읽기
4. `status="running"` 확인 → exit code 1 반환
5. Claude Code 종료 차단 (Ralph Loop 유지)
6. 메인 스킬이 Skill tool로 자신을 재귀 호출
7. 새로운 iteration 시작

---

### 내부 루프 (deep-research skill)

**역할:**
- 연구 로직 실행 (9단계 사이클)
- 자기 재귀 호출 (무한 루프)
- 상태 관리

**파일:** `.claude/skills/deep-research/SKILL.md:1-265`

**핵심 로직:**
```markdown
## 9. LOOP - 다음 Iteration 자동 시작

state.json을 읽어서 다음을 확인:
- status = state["status"]
- current = state["iteration"]["current"]
- max_iter = state["iteration"]["max"]
- budget = state["metrics"]["cost_estimate_usd"]

종료 조건을 만족하지 않으면:
→ Skill(skill="deep-research", args="")
```

**자기 재귀 호출:**
- Skill tool을 사용하여 자신을 호출
- 새로운 컨텍스트로 실행 (이전 대화 히스토리 없음)
- state.json에서 이전 상태 로드

---

## 컴포넌트 구조

### 파일 시스템

```
forge/
├── research.sh                 # 외부 루프 스크립트 (218 lines)
├── config.json                 # 연구 설정 (87 lines)
│
├── .claude/
│   ├── settings.json           # Claude Code 설정
│   │
│   ├── hooks/
│   │   └── stop-hook.py        # Ralph Loop enforcer (88 lines)
│   │
│   └── skills/
│       ├── deep-research/
│       │   ├── SKILL.md        # 메인 스킬 (265 lines)
│       │   └── references/
│       │       └── thinking_tools.md
│       │
│       ├── dr/SKILL.md         # 단축 명령 (7 lines)
│       ├── research-status/SKILL.md    # 상태 확인 (53 lines)
│       ├── research-resume/SKILL.md    # 재개 (44 lines)
│       └── research-report/SKILL.md    # 보고서 (147 lines)
│
└── .research/                  # 연구 상태 (실행 중 생성)
    ├── state.json
    ├── findings.md
    ├── hypotheses.md
    ├── sources.md
    ├── knowledge_graph.json
    ├── reflexion.json
    ├── search_history.json
    ├── iteration_logs/
    └── papers/
```

---

### 컴포넌트 역할

| 컴포넌트 | 파일 | 역할 | 실행 시점 |
|----------|------|------|----------|
| **외부 루프** | research.sh | Iteration 제어, 안전 체크 | 사용자 실행 시 |
| **Stop Hook** | stop-hook.py | Ralph Loop 강제 | Claude 종료 시도 시 |
| **메인 스킬** | deep-research/SKILL.md | 연구 로직, 자기 재귀 | 각 iteration |
| **보조 스킬** | dr, status, resume, report | 편의 기능 | 사용자 호출 시 |
| **설정** | config.json | 연구 파라미터 | 스킬 로드 시 |
| **상태** | .research/*.json | 상태 저장 | 각 iteration |

---

## 데이터 흐름

### Iteration 시작 시

```
┌─────────────────────┐
│  research.sh        │
│  iteration++        │
│  status="running"   │
│  → state.json 저장  │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│  claude /deep-research
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│  SKILL: 1. LOAD     │
│  → state.json 읽기  │
│  → search_history   │
│  → reflexion        │
└──────────┬──────────┘
           ↓
     [연구 사이클 실행]
```

---

### Iteration 종료 시

```
     [연구 사이클 완료]
           ↓
┌─────────────────────┐
│  SKILL: 7. SAVE     │
│  → state.json 업데이트
│  → findings.md 추가 │
│  → iteration_logs/  │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│  SKILL: 9. LOOP     │
│  종료 조건 체크     │
└──────────┬──────────┘
           ↓
    종료 조건 만족?
    ┌───Yes──→ 종료
    └───No───→ Skill("deep-research")
                     ↓
              새 iteration 시작
```

---

### 종료 시도 시

```
┌─────────────────────┐
│  Claude Code        │
│  세션 종료 시도     │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│  Stop Hook 실행     │
│  → state.json 읽기  │
└──────────┬──────────┘
           ↓
    status == "running"?
    ┌───Yes──→ exit 1 (차단)
    │               ↓
    │         종료 취소, 계속 실행
    │
    └───No───→ exit 0 (허용)
                    ↓
              세션 정상 종료
```

---

## 도구 사용 정책

### 허용된 도구

파일: `.claude/skills/deep-research/SKILL.md:5`

```yaml
allowed-tools: WebSearch, WebFetch, Read, Write, Edit, Bash, Glob, Grep, Skill
```

| 도구 | 용도 | 제한 |
|------|------|------|
| WebSearch | 웹 검색 | 무제한 |
| WebFetch | URL 콘텐츠 추출 | 무제한 |
| Read | 파일 읽기 | `.research/`, config.json |
| Write | 파일 쓰기 | `.research/` 전용 |
| Edit | 파일 수정 | `.research/` 전용 |
| Bash | 외부 명령 | PDF 다운로드, jq |
| Glob | 파일 검색 | 무제한 |
| Grep | 내용 검색 | 무제한 |
| Skill | 자기 재귀 | deep-research만 |

### 금지된 도구

- ❌ Task (서브에이전트 제거됨)
- ❌ 기타 Skill 호출 (deep-research 외)

---

### 권한 정책

파일: `.claude/settings.json:21-39`

```json
"permissions": {
  "allow": [
    "Read(.research/**)",
    "Write(.research/**)",
    "Edit(.research/**)",
    "Bash(curl -L -o .research/papers/*.pdf *)",
    "Bash(jq * .research/*.json)",
    "WebFetch",
    "WebSearch"
  ],
  "deny": [
    "Bash(rm -rf .research)",
    "Edit(.git/**)",
    "Read(.env)",
    "Write(.env)"
  ],
  "ask": [
    "Bash(git push *)",
    "Bash(rm *)"
  ]
}
```

**보안 원칙:**
- ✅ `.research/` 읽기/쓰기/수정 허용
- ❌ `.research/` 삭제 금지
- ❌ `.git/`, `.env` 접근 금지
- ⚠️ `git push`, `rm` 사용자 확인 필요

---

## 성능 고려사항

### 병렬 처리

**병렬 검색:**
```
단일 응답에 3개 WebSearch 호출
→ 총 시간 = max(검색1, 검색2, 검색3)
→ 약 30초 (병렬) vs 90초 (순차)
```

**병렬 WebFetch:**
```
유망한 URL 3개 동시 추출
→ 총 시간 = max(fetch1, fetch2, fetch3)
→ 약 20초 (병렬) vs 60초 (순차)
```

---

### 메모리 관리

**컨텍스트 크기:**
- 각 iteration은 새로운 컨텍스트로 실행
- 이전 대화 히스토리 없음
- state.json에서 필요한 정보만 로드

**컴팩션:**
```json
"memory": {
  "compaction_threshold": 0.8,
  "compaction_interval": 5
}
```

- 80% 도달 시 컴팩션 필요
- 5 iterations마다 자동 실행

---

## 확장성

### 수평 확장 (불가)

- ❌ 동시 연구 세션 불가 (`.research/` 공유)
- 해결: 별도 디렉토리에서 실행

### 수직 확장 (가능)

- ✅ max_iterations 증가 (100 → 1000)
- ✅ 예산 증가 ($10 → $100)
- ✅ 병렬 검색 증가 (3 → 5)

---

**다음:** [03-ralph-loop.md](./03-ralph-loop.md) - Ralph Loop 패턴 상세
