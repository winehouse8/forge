#!/usr/bin/env python3
"""
Stop Hook: 리서치 루프 계속 여부 결정
Exit code 0 + JSON으로 decision 반환
"""

import json
import sys
import os

STATE_FILE = ".research/state.json"
MAX_ITERATIONS = 100


def load_state():
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"iteration": {"current": 0, "max": MAX_ITERATIONS}, "status": "initialized"}


def main():
    # Hook 입력 읽기 (stdin)
    try:
        hook_input = json.load(sys.stdin)
    except:
        hook_input = {}

    state = load_state()
    iteration = state.get("iteration", {}).get("current", 0)
    max_iter = state.get("iteration", {}).get("max", MAX_ITERATIONS)
    status = state.get("status", "running")

    # 종료 조건 체크
    should_stop = False
    reason = ""

    # 1. 상태가 완료/정지인 경우
    if status in ["completed", "paused", "stopped_by_user", "budget_exceeded"]:
        should_stop = True
        reason = f"Research {status}"

    # 2. 최대 반복 도달
    elif iteration >= max_iter:
        should_stop = True
        reason = f"Maximum iterations ({max_iter}) reached"

    # 3. stop_hook_active 체크 (무한 루프 방지)
    elif hook_input.get("stop_hook_active", False):
        # 이미 Stop Hook으로 계속 중
        # 추가 안전장치: 연속 10회 이상이면 강제 종료
        if iteration > 10 and state.get("loop_drift", {}).get("consecutive_same_action", 0) > 5:
            should_stop = True
            reason = "Loop drift detected, forcing stop"

    # 결정 출력
    if should_stop:
        output = {
            "decision": "allow",  # 종료 허용
            "reason": reason
        }
    else:
        output = {
            "decision": "block",  # 계속 강제
            "reason": f"Iteration {iteration}/{max_iter} - Continue research. Check .research/state.json for current progress."
        }

    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()
