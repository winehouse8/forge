#!/usr/bin/env python3
"""
Stop Hook: Ralph Loop 구현 - 사용자만 탐험을 멈출 수 있습니다!

SKILL.md 철칙:
  - 오직 state["status"] = "stopped_by_user"일 때만 종료 허용
  - 절대 자동 종료 금지: max_iter, criteria_met 등 모두 금지
  - 의문점이 하나라도 남았으면 무조건 계속!

안전장치만 허용:
  - Budget 초과 (비용 폭발 방지)
  - Loop drift (무한 루프 방지)
"""

import json
import sys
import os

STATE_FILE = ".research/state.json"  # Legacy (backward compatibility)
CURRENT_SESSION_STATE = ".research/current/state.json"  # Session-based (new)
MAX_ITERATIONS = 100
BUDGET_LIMIT = 10.0


def load_state():
    """
    Load state from current session (if exists), fallback to legacy path.
    Priority: .research/current/state.json > .research/state.json
    """
    # Try session-based state first (new multi-session architecture)
    try:
        with open(CURRENT_SESSION_STATE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        pass

    # Fallback to legacy state file (backward compatibility)
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def check_completion_criteria(state):
    """
    Objective, verifiable completion criteria check
    Returns: (all_met: bool, unmet_criteria: list)
    """
    # Backward compatibility: verification 필드가 없으면 기본 criteria 생성
    verification = state.get("verification", {})
    criteria = verification.get("completion_criteria", [])

    # 기본 criteria가 없으면 자동 생성 (backward compatibility)
    if not criteria:
        # state 정보를 바탕으로 자동 평가
        question_field = state.get("question", {})
        if isinstance(question_field, dict):
            decomposed_questions = question_field.get("decomposed", [])
        else:
            decomposed_questions = []  # New structure: question is string

        total_searches = state.get("metrics", {}).get("total_searches", 0)
        contradictions = state.get("contradictions_found", [])

        # Auto-generated criteria
        criteria = [
            {
                "criterion": "Sub-questions explored",
                "met": total_searches >= len(decomposed_questions) * 2  # 각 질문당 최소 2회 검색
            },
            {
                "criterion": "Sufficient searches performed",
                "met": total_searches >= 10  # 최소 10회 검색
            },
            {
                "criterion": "Contradictions acknowledged",
                "met": len(contradictions) >= 0  # 모순 발견 여부 (0개도 OK)
            }
        ]

    unmet = [c for c in criteria if not c.get('met', False)]
    all_met = len(unmet) == 0

    return all_met, unmet


def main():
    # Hook 입력 읽기 (stdin)
    try:
        hook_input = json.load(sys.stdin)
    except:
        hook_input = {}

    state = load_state()

    # 0. 상태 파일이 없으면 연구 세션이 아니므로 종료 허용
    if state is None:
        output = {
            "decision": "approve",  # Fixed: "allow" → "approve"
            "reason": "No active research session"
        }
        print(json.dumps(output))
        sys.exit(0)

    # Support both old and new state.json structures
    iteration_field = state.get("iteration", 0)
    if isinstance(iteration_field, dict):
        # Old structure: {"iteration": {"current": 5, "max": 100}}
        iteration = iteration_field.get("current", 0)
        max_iter = iteration_field.get("max", MAX_ITERATIONS)
    else:
        # New structure (session-based): {"iteration": 7}
        iteration = iteration_field
        max_iter = MAX_ITERATIONS

    status = state.get("status", "initialized")
    budget = state.get("metrics", {}).get("cost_estimate_usd", 0.0)

    # ═══════════════════════════════════════════════════════════════
    # 🔍 rabbit-hole 세션 여부 확인 (세션별 격리)
    # ═══════════════════════════════════════════════════════════════
    # 💡 세션별 격리: .research/.rh_{session_id} 마커 파일 존재 여부
    #
    # 작동 원리:
    # 1. /rh 명령 실행 → ToolUse hook 트리거
    # 2. ToolUse hook: .research/.rh_{session_id} 마커 파일 생성
    # 3. Stop hook: 현재 session_id의 마커 파일 존재 확인
    #    - 있으면 → 현재 세션의 rabbit-hole → Ralph Loop
    #    - 없으면 → 다른 세션 또는 일반 작업 → 정상 종료
    #
    # 세션 격리:
    # Terminal 1: /rh 실행 → .rh_abc123 생성 → Ralph Loop ON
    # Terminal 2: 일반 질문 → .rh_xyz789 없음 → 정상 종료 OK
    # ═══════════════════════════════════════════════════════════════

    current_session_id = hook_input.get("session_id", "")
    marker_file = f".research/.rh_{current_session_id}"

    if not os.path.exists(marker_file):
        # 현재 세션의 rabbit-hole 마커 없음 → 정상 종료 허용
        output = {
            "decision": "approve",
            "reason": f"Not a rabbit-hole session (no marker for {current_session_id[:8]}...)"
        }
        print(json.dumps(output))
        sys.exit(0)

    # ═══════════════════════════════════════════════════════════════
    # 🐰 Ralph Loop 철칙: 사용자만 탐험을 멈출 수 있습니다!
    # ═══════════════════════════════════════════════════════════════
    # SKILL.md 명세 (rabbit-hole 스킬 전용):
    #   - 오직 state["status"] = "stopped_by_user"일 때만 종료 허용
    #   - 절대 자동 종료 금지: max_iter, criteria_met 등 모두 금지
    #   - 의문점이 하나라도 남았으면 무조건 계속!
    # ═══════════════════════════════════════════════════════════════

    should_approve_termination = False
    reason = ""

    # 1. Budget 초과 (안전장치)
    if budget >= BUDGET_LIMIT:
        should_approve_termination = True
        reason = f"🚫 Budget limit (${BUDGET_LIMIT}) exceeded: ${budget:.2f}"

    # 2. status가 "running"이 아니면 종료 허용 (사용자가 중단했거나 세션 종료)
    elif status != "running":
        should_approve_termination = True
        reason = f"Research session not active (status: {status})"

    # 3. Loop drift 안전장치 (무한 루프 방지)
    elif iteration > 10 and state.get("loop_drift", {}).get("consecutive_same_action", 0) > 5:
        should_approve_termination = True
        reason = "⚠️ Loop drift detected, forcing stop"

    # ═══════════════════════════════════════════════════════════════
    # 결정: approve (종료 허용) vs block (종료 차단, Ralph Loop 계속)
    # ═══════════════════════════════════════════════════════════════
    if should_approve_termination:
        # 종료 허용: 마커 파일 정리 + exit code 0
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
    else:
        # 종료 차단: JSON + exit 0 (Ralph Loop 무한 탐험!)
        # 공식 문서: "Claude Code only processes JSON on exit 0"
        output = {
            "decision": "block",
            "reason": f"🐰 Iteration {iteration} | Ralph Loop 활성화: 사용자가 중단할 때까지 무한 탐험!"
        }
        print(json.dumps(output))
        sys.exit(0)  # ✅ exit 0 필수! (JSON 파싱을 위해)


if __name__ == "__main__":
    main()
