#!/usr/bin/env python3
"""
Stop Hook: Ralph Loop 구현 - 사용자만 탐험을 멈출 수 있습니다!

지원 스킬:
  - rabbit-hole: holes.json 기반
  - deep-research: state.json 기반 (legacy)

SKILL.md 철칙:
  - 오직 사용자가 중단할 때만 종료 허용
  - 절대 자동 종료 금지
  - 탐색할 것이 남았으면 무조건 계속!

안전장치만 허용:
  - Budget 초과 (비용 폭발 방지)
  - Max iterations (무한 루프 방지)
"""

import json
import sys
import os

# Rabbit-Hole paths
HOLES_FILE = ".research/current/holes.json"

# Deep-Research paths (legacy)
STATE_FILE = ".research/state.json"
CURRENT_SESSION_STATE = ".research/current/state.json"

MAX_ITERATIONS = 100
BUDGET_LIMIT = 10.0


def load_holes():
    """Load rabbit-hole session state from holes.json"""
    try:
        with open(HOLES_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def load_state():
    """
    Load state from current session (if exists), fallback to legacy path.
    Priority: .research/current/state.json > .research/state.json
    """
    try:
        with open(CURRENT_SESSION_STATE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        pass

    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def get_next_hole_info(holes_data):
    """Get information about the next hole to explore"""
    pending = holes_data.get("pending", [])
    if not pending:
        return None, "No pending holes"

    # Sort by interest: high > medium > low
    interest_order = {"high": 0, "medium": 1, "low": 2}
    sorted_holes = sorted(pending, key=lambda h: interest_order.get(h.get("interest", "low"), 2))

    next_hole = sorted_holes[0]
    return next_hole, f"Next: [{next_hole['type']}] {next_hole['question'][:50]}..."


def build_continue_prompt(holes_data):
    """Build the prompt to continue rabbit-hole exploration"""
    iteration = holes_data.get("iteration", 0)
    pending = holes_data.get("pending", [])

    prompt = f"""🐰 Iteration {iteration + 1} 시작

pending: {len(pending)}개

**SPAWN부터 시작:**
1. SPAWN: pending < 3이면 holes 생성
2. SELECT: interest 높은 hole 선택
3. EXPLORE: WebSearch
4. SAVE: evidence → claim → 출력"""

    return prompt


def main():
    # Hook 입력 읽기 (stdin)
    try:
        hook_input = json.load(sys.stdin)
    except:
        hook_input = {}

    current_session_id = hook_input.get("session_id", "")
    marker_file = f".research/.rh_{current_session_id}"

    # ═══════════════════════════════════════════════════════════════
    # 🔍 rabbit-hole 세션 여부 확인 (세션별 격리)
    # ═══════════════════════════════════════════════════════════════
    is_rabbit_hole = os.path.exists(marker_file)

    if is_rabbit_hole:
        handle_rabbit_hole(current_session_id, marker_file)
    else:
        handle_deep_research(current_session_id)


def handle_rabbit_hole(session_id, marker_file):
    """
    🐰 Rabbit-Hole Ralph Loop
    holes.json 기반으로 다음 iteration 자동 실행
    """
    holes_data = load_holes()

    # holes.json 없으면 세션 종료
    if holes_data is None:
        cleanup_and_approve(marker_file, "No holes.json found")
        return

    iteration = holes_data.get("iteration", 0)
    pending = holes_data.get("pending", [])

    # ═══════════════════════════════════════════════════════════════
    # 안전장치 체크
    # ═══════════════════════════════════════════════════════════════
    should_stop = False
    reason = ""

    # 1. Max iterations
    if iteration >= MAX_ITERATIONS:
        should_stop = True
        reason = f"🚫 Max iterations ({MAX_ITERATIONS}) reached"

    # 2. Pending holes 없고 더 이상 탐색할 게 없음 (100 iteration 넘으면)
    # 참고: pending 없어도 SPAWN에서 새로 생성하므로 보통은 계속됨
    elif iteration >= 50 and len(pending) == 0:
        should_stop = True
        reason = "🏁 50+ iterations with no pending holes"

    if should_stop:
        cleanup_and_approve(marker_file, reason)
        return

    # ═══════════════════════════════════════════════════════════════
    # 🐰 Ralph Loop: 종료 차단 + 다음 iteration 지시
    # ═══════════════════════════════════════════════════════════════
    continue_prompt = build_continue_prompt(holes_data)

    output = {
        "decision": "block",
        "reason": f"🐰 Iteration {iteration} 완료 | Ralph Loop 계속!",
        "stopReason": continue_prompt
    }
    print(json.dumps(output))
    sys.exit(0)


def handle_deep_research(session_id):
    """
    Deep-Research Ralph Loop (legacy)
    state.json 기반
    """
    state = load_state()

    # 상태 파일 없으면 연구 세션 아님
    if state is None:
        output = {
            "decision": "approve",
            "reason": "No active research session"
        }
        print(json.dumps(output))
        sys.exit(0)

    # Support both old and new state.json structures
    iteration_field = state.get("iteration", 0)
    if isinstance(iteration_field, dict):
        iteration = iteration_field.get("current", 0)
    else:
        iteration = iteration_field

    status = state.get("status", "initialized")
    budget = state.get("metrics", {}).get("cost_estimate_usd", 0.0)

    should_approve = False
    reason = ""

    # 안전장치
    if budget >= BUDGET_LIMIT:
        should_approve = True
        reason = f"🚫 Budget limit (${BUDGET_LIMIT}) exceeded"
    elif status != "running":
        should_approve = True
        reason = f"Session not active (status: {status})"
    elif iteration >= MAX_ITERATIONS:
        should_approve = True
        reason = f"🚫 Max iterations ({MAX_ITERATIONS}) reached"

    if should_approve:
        output = {"decision": "approve", "reason": reason}
    else:
        output = {
            "decision": "block",
            "reason": f"🔬 Iteration {iteration} | Deep Research 계속!"
        }

    print(json.dumps(output))
    sys.exit(0)


def cleanup_and_approve(marker_file, reason):
    """마커 파일 정리 후 종료 허용"""
    try:
        if os.path.exists(marker_file):
            os.remove(marker_file)
    except:
        pass

    output = {
        "decision": "approve",
        "reason": reason
    }
    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()
