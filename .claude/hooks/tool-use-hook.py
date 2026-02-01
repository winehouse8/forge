#!/usr/bin/env python3
"""
ToolUse Hook: rabbit-hole 세션 ID 저장 (세션별 격리)

rabbit-hole 또는 rh skill이 호출될 때 현재 session_id를 저장하여
Stop hook이 해당 세션에만 Ralph Loop를 적용할 수 있도록 함
"""

import json
import sys
from pathlib import Path


def main():
    # Hook 입력 읽기 (stdin)
    try:
        hook_input = json.load(sys.stdin)
    except:
        # JSON 파싱 실패 → 허용
        sys.exit(0)

    tool_name = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input", {})
    session_id = hook_input.get("session_id", "")

    # Skill 도구 확인 (tool_name = "Skill")
    # rabbit-hole 또는 rh skill 호출 감지
    is_rabbit_hole_tool = False
    if tool_name == "Skill":
        skill = tool_input.get("skill", "")  # ✅ 'skill' 필드가 맞음!
        is_rabbit_hole_tool = skill in ["rabbit-hole", "rh"]

    if is_rabbit_hole_tool and session_id:
        # .research/.rh_{session_id} 마커 파일 생성
        research_dir = Path(".research")
        research_dir.mkdir(parents=True, exist_ok=True)

        marker_file = research_dir / f".rh_{session_id}"
        marker_file.touch()

    # 도구 실행은 항상 허용
    output = {
        "decision": "approve"
    }
    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()
