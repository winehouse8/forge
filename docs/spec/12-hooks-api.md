# Hooks API 명세

**문서:** 12-hooks-api.md
**최종 수정일:** 2026-01-31
**관련 파일:** `.claude/hooks/stop-hook.py`, `.claude/settings.json`

---

## 목차
- [Hooks 개요](#hooks-개요)
- [Stop Hook API](#stop-hook-api)
- [Stop Hook 구현](#stop-hook-구현)
- [입출력 스펙](#입출력-스펙)
- [에러 처리](#에러-처리)

---

## Hooks 개요

### 지원되는 Hook 유형

**파일:** `.claude/settings.json:11-20`

| Hook | 트리거 시점 | 용도 |
|------|-----------|------|
| **Stop** | Claude Code 종료 시도 시 | Ralph Loop 구현 (종료 차단) |

---

### Hook 설정

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude/hooks/stop-hook.py"
          }
        ]
      }
    ]
  }
}
```

---

## Stop Hook API

### 목적

**Ralph Loop 패턴 구현** - LLM의 주관적 "완료" 판단을 무시하고 객관적 조건만으로 종료 제어

**상세:** [03-ralph-loop.md](./03-ralph-loop.md)

---

### 실행 흐름

```
1. Claude Code 종료 시도
   (사용자 Ctrl+C 또는 LLM "완료" 출력)
         ↓
2. Stop Hook 실행
   python3 .claude/hooks/stop-hook.py
         ↓
3. stdin으로 JSON 입력 받기
   echo '{}' | python3 .claude/hooks/stop-hook.py
         ↓
4. .research/state.json 읽기
         ↓
5. status 확인
   - "running" → exit 1 (차단)
   - 기타 → exit 0 (허용)
         ↓
6. Claude Code 동작
   - exit 0: 종료 진행
   - exit 1: 종료 취소, 계속 실행
```

---

### Exit Code 의미

| Exit Code | 의미 | Claude Code 동작 |
|-----------|------|------------------|
| **0** | 종료 허용 | 세션 종료 |
| **1** | 종료 차단 | 계속 실행 (Ralph Loop) |
| **기타** | 에러 | 기본 동작 (종료) |

---

## Stop Hook 구현

### 파일 구조

**파일:** `.claude/hooks/stop-hook.py`

**라인:** 88줄

**의존성:**
- Python 3.7+
- 표준 라이브러리만 사용 (`json`, `sys`, `pathlib`)

---

### 전체 코드

```python
#!/usr/bin/env python3
"""
Stop Hook for Pathfinder Deep Research

Ralph Loop 패턴 구현:
- status="running"일 때만 종료 차단
- 그 외 모든 경우 종료 허용
"""

import json
import sys
from pathlib import Path

STATE_FILE = Path(".research/state.json")


def load_state():
    """
    state.json 로드

    Returns:
        dict | None: 상태 객체 또는 None (파일 없음)
    """
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None


def main():
    """
    Stop Hook 메인 로직

    Exit codes:
        0: 종료 허용
        1: 종료 차단 (Ralph Loop)
    """
    # stdin으로 hook 입력 받기 (현재 미사용)
    try:
        hook_input = json.loads(sys.stdin.read())
    except:
        hook_input = {}

    # state.json 로드
    state = load_state()

    # 0. 상태 파일이 없으면 일반 세션 → 종료 허용
    if state is None:
        output = {
            "decision": "allow",
            "reason": "No active research session"
        }
        print(json.dumps(output))
        sys.exit(0)

    # 1. status 확인
    status = state.get("status", "initialized")

    # 2. status != "running" → 종료 허용
    if status != "running":
        should_stop = True
        reason = f"Research session not active (status: {status})"
        sys.exit(0)

    # 3. Loop drift 탐지 (선택적)
    if hook_input.get("stop_hook_active", False):
        iteration = hook_input.get("iteration", 0)
        consecutive_same = hook_input.get("consecutive_same", 0)

        # 10회 이상 iteration + 5회 이상 같은 행동 반복
        if iteration > 10 and consecutive_same > 5:
            should_stop = True
            reason = "Loop drift detected"
            output = {
                "decision": "allow",
                "reason": reason
            }
            print(json.dumps(output))
            sys.exit(0)

    # 4. status="running" → 종료 차단 (Ralph Loop)
    output = {
        "decision": "block",
        "reason": "🔬 Research in progress..."
    }
    print(json.dumps(output))
    sys.exit(1)  # Non-zero exit code blocks termination


if __name__ == "__main__":
    main()
```

---

### 핵심 로직

**1. 상태 파일 확인**

```python
state = load_state()
if state is None:
    # 일반 Claude Code 세션 → 종료 허용
    sys.exit(0)
```

**2. status 확인**

```python
status = state.get("status", "initialized")

if status != "running":
    # 연구 비활성 → 종료 허용
    sys.exit(0)
else:
    # 연구 진행 중 → 종료 차단
    sys.exit(1)
```

---

## 입출력 스펙

### 입력 (stdin)

**형식:** JSON

**예시:**

```json
{}
```

**현재 버전에서는 입력을 사용하지 않음.** 향후 확장 가능성을 위해 JSON 파싱만 수행.

**확장 예시 (Loop Drift 탐지):**

```json
{
  "stop_hook_active": true,
  "iteration": 15,
  "consecutive_same": 6
}
```

---

### 출력 (stdout)

**형식:** JSON

**필드:**

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `decision` | string | ✅ | "allow" 또는 "block" |
| `reason` | string | ❌ | 결정 이유 (사용자에게 표시) |

**예시 1: 종료 허용**

```json
{
  "decision": "allow",
  "reason": "No active research session"
}
```

**예시 2: 종료 차단**

```json
{
  "decision": "block",
  "reason": "🔬 Research in progress..."
}
```

---

### Exit Code

| 상황 | Exit Code | decision | 동작 |
|------|-----------|----------|------|
| 파일 없음 | 0 | "allow" | 종료 |
| status != "running" | 0 | "allow" | 종료 |
| status = "running" | 1 | "block" | 계속 |
| Loop drift 탐지 | 0 | "allow" | 종료 |

---

## 에러 처리

### FileNotFoundError

```python
try:
    with open(STATE_FILE, 'r') as f:
        return json.load(f)
except FileNotFoundError:
    # 일반 세션 → 종료 허용
    return None
```

**동작:** 에러를 예외로 처리하지 않고 None 반환 → exit 0

---

### JSONDecodeError

```python
except json.JSONDecodeError:
    # state.json 손상 → 종료 허용
    return None
```

**동작:** 손상된 파일은 연구 세션 아님으로 간주 → exit 0

---

### stdin 파싱 실패

```python
try:
    hook_input = json.loads(sys.stdin.read())
except:
    # 파싱 실패 → 빈 객체 사용
    hook_input = {}
```

**동작:** 에러 무시, 빈 객체로 계속 진행

---

## 테스트

### 단위 테스트

**관련:** [09-testing.md](./09-testing.md) > "Stop Hook 테스트"

**테스트 케이스:**

| TC | 상태 | 예상 Exit Code |
|----|------|----------------|
| TC-SH-001 | 파일 없음 | 0 |
| TC-SH-002 | status="initialized" | 0 |
| TC-SH-003 | status="running" | 1 |
| TC-SH-004 | status="paused" | 0 |
| TC-SH-005 | status="completed" | 0 |
| TC-SH-006 | Loop drift | 0 |

---

### 수동 테스트

```bash
# Test 1: 파일 없음
rm -f .research/state.json
echo '{}' | python3 .claude/hooks/stop-hook.py
echo "Exit code: $?"
# Expected: 0

# Test 2: status=running
cat > .research/state.json << 'EOF'
{"status": "running", "iteration": {"current": 5, "max": 100}}
EOF
echo '{}' | python3 .claude/hooks/stop-hook.py
echo "Exit code: $?"
# Expected: 1

# Test 3: status=paused
cat > .research/state.json << 'EOF'
{"status": "paused", "iteration": {"current": 10, "max": 100}}
EOF
echo '{}' | python3 .claude/hooks/stop-hook.py
echo "Exit code: $?"
# Expected: 0
```

---

## Hook 개발 가이드

### 새 Hook 추가

**1. Python 스크립트 생성**

```bash
cat > .claude/hooks/my-hook.py << 'EOF'
#!/usr/bin/env python3
import json
import sys

def main():
    # Hook 입력 받기
    hook_input = json.loads(sys.stdin.read())

    # 로직 실행
    # ...

    # 결과 출력
    output = {"decision": "allow", "reason": "..."}
    print(json.dumps(output))

    # Exit code 반환
    sys.exit(0)  # or 1

if __name__ == "__main__":
    main()
EOF

chmod +x .claude/hooks/my-hook.py
```

**2. settings.json에 등록**

```json
{
  "hooks": {
    "MyEvent": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude/hooks/my-hook.py"
          }
        ]
      }
    ]
  }
}
```

---

### Hook 규칙

1. **stdin에서 JSON 입력 받기**
   ```python
   hook_input = json.loads(sys.stdin.read())
   ```

2. **stdout으로 JSON 출력**
   ```python
   output = {"decision": "allow", "reason": "..."}
   print(json.dumps(output))
   ```

3. **Exit code로 결정 전달**
   - 0: 허용
   - 1: 차단

4. **에러 처리**
   - 모든 예외 처리
   - 에러 시 기본 동작 (허용)

---

## 버전 히스토리

| 버전 | 날짜 | 변경 사항 |
|------|------|----------|
| 4.0 | 2026-01-31 | state.json 없을 때 None 반환 (이전: 기본 객체) |
| 3.0 | 2026-01-30 | Loop drift 탐지 추가 |
| 2.0 | 2026-01-29 | Ralph Loop 패턴 구현 |
| 1.0 | 2026-01-28 | 초기 버전 |

---

## 참고 자료

- **Ralph Loop 패턴:** [03-ralph-loop.md](./03-ralph-loop.md)
- **테스트:** [09-testing.md](./09-testing.md)
- **아키텍처:** [02-architecture.md](./02-architecture.md)

---

**완료:** 모든 스펙 문서 작성 완료
