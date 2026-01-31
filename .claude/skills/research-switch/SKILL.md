---
name: research-switch
description: 다른 연구 세션으로 전환합니다. 현재 연구를 일시 중단하고 다른 연구를 재개할 때 사용합니다.
argument-hint: <session_id>
allowed-tools: Bash, Read, Write
---

# Research Switch Skill

다른 연구 세션으로 전환합니다.

## 인수 처리

세션 ID가 필요합니다:
- `$ARGUMENTS`에서 세션 ID 추출
- 세션 ID가 없으면 에러 출력 및 세션 목록 표시

## 실행

```python
from session_manager import SessionManager
import sys

sm = SessionManager()

# Get session ID from arguments
session_id = "$ARGUMENTS".strip()

if not session_id:
    print("❌ Error: Session ID required")
    print("\nUsage: /research-switch <session_id>")
    print("\nAvailable sessions:")

    sessions = sm.list_sessions()
    for session in sessions:
        print(f"  - {session['id']}")
        print(f"    Question: {session['question']}")
        print(f"    Status: {session['status']} | Iteration: {session.get('iteration', 0)}")
        print()

    sys.exit(1)

# Switch to session
try:
    sm.switch_session(session_id)

    # Get session info
    session = sm.index["sessions"][session_id]

    print(f"✓ Switched to session: {session_id}")
    print(f"\n📝 Question: {session['question']}")
    print(f"📊 Status: {session['status']}")
    print(f"🔄 Iteration: {session.get('iteration', 0)}")
    print(f"\n→ Continue research with: /research-resume")

except ValueError as e:
    print(f"❌ Error: {e}")
    print("\nUse /research-list to see available sessions")
    sys.exit(1)
```
