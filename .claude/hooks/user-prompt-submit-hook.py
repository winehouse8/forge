#!/usr/bin/env python3
"""
UserPromptSubmit Hook: rabbit-hole 세션 ID 저장

사용자가 /rh 또는 /rabbit-hole 명령을 입력하면
현재 세션의 session_id를 저장하여 stop-hook이
Ralph Loop를 적용할 수 있도록 함
"""

import json
import sys
import os
from pathlib import Path


def main():
    # Hook 입력 읽기 (stdin)
    try:
        hook_input = json.load(sys.stdin)
    except:
        # JSON 파싱 실패 → 허용
        sys.exit(0)

    prompt = hook_input.get("prompt", "").strip()
    session_id = hook_input.get("session_id", "")

    # /rh 또는 /rabbit-hole 명령 감지
    is_rabbit_hole_command = (
        prompt.startswith("/rh ") or
        prompt.startswith("/rh") and len(prompt) == 3 or
        prompt.startswith("/rabbit-hole ")
    )

    if is_rabbit_hole_command and session_id:
        # .research/current/.session_id 파일에 저장
        session_id_file = Path(".research/current/.session_id")
        session_id_file.parent.mkdir(parents=True, exist_ok=True)

        with open(session_id_file, 'w') as f:
            f.write(session_id)

        print(f"✓ rabbit-hole 세션 ID 저장됨: {session_id[:8]}...")

    # 프롬프트는 항상 허용
    sys.exit(0)


if __name__ == "__main__":
    main()
