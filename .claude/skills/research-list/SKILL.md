---
name: research-list
description: 모든 연구 세션 목록을 표시합니다. 각 세션의 진행 상태, iteration 수, 마지막 접근 시간을 확인할 수 있습니다.
allowed-tools: Bash, Read
---

# Research List Skill

모든 연구 세션을 조회합니다.

## 실행

```python
from session_manager import SessionManager

sm = SessionManager()

# 모든 세션 조회
sessions = sm.list_sessions()
current = sm.get_current_session()

print("\n📋 Research Sessions")
print("=" * 80)

if not sessions:
    print("No research sessions found.")
    print("\nStart a new research with: /dr [your question]")
else:
    for session in sessions:
        # Current session marker
        marker = "→" if current and session["id"] == current["id"] else " "

        print(f"{marker} {session['id']}")
        print(f"  📝 Question: {session['question']}")
        print(f"  📊 Status: {session['status']} | Iteration: {session.get('iteration', 0)}")
        print(f"  🕒 Last accessed: {session['last_accessed'][:19]}")
        print()

    print(f"\nTotal: {len(sessions)} session(s)")

    if current:
        print(f"\n→ Current: {current['id']}")
        print(f"  Use /research-switch <session_id> to switch")
    else:
        print("\nNo active session. Use /research-switch <session_id> to activate")
```
