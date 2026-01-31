#!/usr/bin/env python3
"""
Stop Hook: Objective Criteria 기반 리서치 루프 제어
Research Report 권장사항: Deterministic verification over probabilistic iteration count
"""

import json
import sys
import os

STATE_FILE = ".research/state.json"
MAX_ITERATIONS = 100
BUDGET_LIMIT = 10.0


def load_state():
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
        decomposed_questions = state.get("question", {}).get("decomposed", [])
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
            "decision": "allow",
            "reason": "No active research session"
        }
        print(json.dumps(output))
        sys.exit(0)

    iteration = state.get("iteration", {}).get("current", 0)
    max_iter = state.get("iteration", {}).get("max", MAX_ITERATIONS)
    status = state.get("status", "initialized")
    budget = state.get("metrics", {}).get("cost_estimate_usd", 0.0)

    # === OBJECTIVE CRITERIA CHECK (New!) ===
    criteria_met, unmet_criteria = check_completion_criteria(state)

    # 종료 조건 체크 (우선순위 순서)
    should_stop = False
    reason = ""

    # 1. Budget 초과 (최우선)
    if budget >= BUDGET_LIMIT:
        should_stop = True
        reason = f"🚫 Budget limit (${BUDGET_LIMIT}) exceeded: ${budget:.2f}"

    # 2. status가 "running"이 아니면 종료 허용
    elif status != "running":
        should_stop = True
        reason = f"Research session not active (status: {status})"

    # 3. Max iterations 도달
    elif iteration >= max_iter:
        should_stop = True
        reason = f"Maximum iterations ({max_iter}) reached"

    # 4. Objective Criteria 충족 (New!)
    elif criteria_met:
        should_stop = True
        reason = f"✅ All completion criteria met (deterministic verification)"

    # 5. Loop drift 안전장치
    elif hook_input.get("stop_hook_active", False):
        if iteration > 10 and state.get("loop_drift", {}).get("consecutive_same_action", 0) > 5:
            should_stop = True
            reason = "⚠️ Loop drift detected, forcing stop"

    # 결정 출력 및 exit code 결정
    if should_stop:
        # 종료 허용: exit code 0
        output = {
            "decision": "allow",
            "reason": reason
        }
        print(json.dumps(output))
        sys.exit(0)
    else:
        # 종료 차단: exit code 1 (Ralph Loop 패턴)
        # Unmet criteria를 명확히 알려줌 (Deterministic feedback)
        if unmet_criteria:
            unmet_list = [c['criterion'] for c in unmet_criteria]
            focus = unmet_list[0] if unmet_list else "Continue research"
            output = {
                "decision": "block",
                "reason": f"🔬 Iteration {iteration}/{max_iter} | Unmet: {', '.join(unmet_list[:2])} | Focus: {focus}"
            }
        else:
            output = {
                "decision": "block",
                "reason": f"🔬 Iteration {iteration}/{max_iter} in progress. Research continues."
            }

        print(json.dumps(output))
        sys.exit(1)  # Non-zero exit code blocks termination


if __name__ == "__main__":
    main()
