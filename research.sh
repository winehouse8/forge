#!/bin/bash
#==============================================================================
# research.sh - 무한루프 리서치 컨트롤러
#==============================================================================

# 설정
MAX_ITERATIONS=${1:-100}
RESEARCH_DIR=".research"
STATE_FILE="$RESEARCH_DIR/state.json"
COMPLETION_PROMISE="<promise>RESEARCH_COMPLETE</promise>"
BUDGET_LIMIT_USD=10.0

#==============================================================================
# 초기화
#==============================================================================
init_research() {
    mkdir -p "$RESEARCH_DIR/iteration_logs"
    mkdir -p "$RESEARCH_DIR/papers"

    if [ ! -f "$STATE_FILE" ]; then
        cat > "$STATE_FILE" << EOF
{
  "version": "4.0",
  "session_id": "research_$(date +%Y%m%d_%H%M%S)",
  "question": {
    "original": "",
    "decomposed": []
  },
  "iteration": {
    "current": 0,
    "max": $MAX_ITERATIONS,
    "last_compaction": 0
  },
  "status": "initialized",
  "hypotheses": [],
  "knowledge_summary": {
    "confirmed_facts": 0,
    "uncertain_claims": 0,
    "contradictions": 0
  },
  "search_history": [],
  "loop_drift": {
    "consecutive_same_action": 0,
    "last_action_hash": ""
  },
  "metrics": {
    "total_searches": 0,
    "successful_searches": 0,
    "token_usage_estimate": 0,
    "cost_estimate_usd": 0.0
  }
}
EOF
    fi

    # 다른 파일들 초기화
    [ ! -f "$RESEARCH_DIR/findings.md" ] && printf "# Research Findings\n\n---\n" > "$RESEARCH_DIR/findings.md"
    [ ! -f "$RESEARCH_DIR/hypotheses.md" ] && printf "# Hypothesis History\n\n---\n" > "$RESEARCH_DIR/hypotheses.md"
    [ ! -f "$RESEARCH_DIR/sources.md" ] && printf "# Sources & References\n\n---\n" > "$RESEARCH_DIR/sources.md"
    [ ! -f "$RESEARCH_DIR/reflexion.json" ] && echo '{"memories":[],"aggregated_lessons":{}}' > "$RESEARCH_DIR/reflexion.json"
    [ ! -f "$RESEARCH_DIR/knowledge_graph.json" ] && echo '{"nodes":[],"edges":[],"temporal_markers":{}}' > "$RESEARCH_DIR/knowledge_graph.json"
    [ ! -f "$RESEARCH_DIR/search_history.json" ] && echo '{"queries":[]}' > "$RESEARCH_DIR/search_history.json"
}

#==============================================================================
# Loop Drift 탐지
#==============================================================================
check_loop_drift() {
    local consecutive=$(jq -r '.loop_drift.consecutive_same_action // 0' "$STATE_FILE")
    local threshold=3

    if [ "$consecutive" -ge "$threshold" ]; then
        echo "⚠️  Loop Drift detected! ($consecutive consecutive same actions)"
        echo "   Forcing strategy change..."
        jq '.loop_drift.consecutive_same_action = 0 | .status = "strategy_change_required"' \
            "$STATE_FILE" > tmp.json && mv tmp.json "$STATE_FILE"
        return 1
    fi
    return 0
}

#==============================================================================
# 예산 체크
#==============================================================================
check_budget() {
    local spent=$(jq -r '.metrics.cost_estimate_usd // 0' "$STATE_FILE")
    local threshold=$(echo "$BUDGET_LIMIT_USD * 0.8" | bc)

    if (( $(echo "$spent > $threshold" | bc -l) )); then
        echo "⚠️  Budget warning: \$$spent / \$$BUDGET_LIMIT_USD (80% reached)"
    fi

    if (( $(echo "$spent > $BUDGET_LIMIT_USD" | bc -l) )); then
        echo "🛑  Budget exceeded! Stopping research."
        jq '.status = "budget_exceeded"' "$STATE_FILE" > tmp.json && mv tmp.json "$STATE_FILE"
        return 1
    fi
    return 0
}

#==============================================================================
# 진행 상황 체크
#==============================================================================
check_progress() {
    local iteration=$(jq -r '.iteration.current' "$STATE_FILE")
    local interval=5

    if [ $((iteration % interval)) -eq 0 ] && [ "$iteration" -gt 0 ]; then
        local confirmed=$(jq -r '.knowledge_summary.confirmed_facts // 0' "$STATE_FILE")
        echo "📊 Progress check at iteration $iteration: $confirmed confirmed facts"
    fi
}

#==============================================================================
# 메인 루프
#==============================================================================
run_research() {
    local question="$1"
    local iteration=0

    # 질문 설정 (첫 실행 시)
    if [ -n "$question" ]; then
        jq --arg q "$question" '.question.original = $q | .status = "running"' \
            "$STATE_FILE" > tmp.json && mv tmp.json "$STATE_FILE"
    fi

    echo ""
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║           🔬 Deep Research Session Started                     ║"
    echo "╠═══════════════════════════════════════════════════════════════╣"
    echo "║  Max iterations: $MAX_ITERATIONS"
    echo "║  Budget limit: \$$BUDGET_LIMIT_USD"
    echo "║  Press 'q' to quit, 's' to pause"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo ""

    while [ $iteration -lt $MAX_ITERATIONS ]; do
        # Iteration 카운터 업데이트
        jq --argjson i "$((iteration + 1))" \
            '.iteration.current = $i | .status = "running"' \
            "$STATE_FILE" > tmp.json && mv tmp.json "$STATE_FILE"

        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "🔬 Research Iteration #$((iteration + 1)) / $MAX_ITERATIONS"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

        # 안전 체크들
        check_loop_drift || true
        check_budget || break
        check_progress

        # Claude Code 스킬 실행 (새로운 컨텍스트)
        output=$(claude /deep-research "Continue research iteration #$((iteration + 1))" 2>&1)

        echo "$output"

        # Completion Promise 체크
        if echo "$output" | grep -q "$COMPLETION_PROMISE"; then
            echo ""
            echo "✅ Research completed successfully!"
            jq '.status = "completed"' "$STATE_FILE" > tmp.json && mv tmp.json "$STATE_FILE"
            break
        fi

        # 상태 파일 체크
        status=$(jq -r '.status' "$STATE_FILE")
        if [ "$status" = "completed" ] || [ "$status" = "paused" ]; then
            echo "Research $status at iteration $((iteration + 1))"
            break
        fi

        # 사용자 인터럽트 체크 (논블로킹)
        read -t 1 -n 1 input 2>/dev/null || true
        case "$input" in
            q|Q)
                jq '.status = "stopped_by_user"' "$STATE_FILE" > tmp.json && mv tmp.json "$STATE_FILE"
                echo ""
                echo "🛑 Research stopped by user"
                break
                ;;
            s|S)
                jq '.status = "paused"' "$STATE_FILE" > tmp.json && mv tmp.json "$STATE_FILE"
                echo ""
                echo "⏸️  Research paused. Run './research.sh' to resume."
                break
                ;;
        esac

        ((iteration++))
    done

    # 최종 보고서
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║           📊 Research Session Complete                         ║"
    echo "╠═══════════════════════════════════════════════════════════════╣"
    echo "║  📄 Final Report: RESEARCH_REPORT.md"
    echo "║  📁 Research Data: $RESEARCH_DIR/"
    echo "║  📈 Iterations: $((iteration + 1))"
    cost=$(jq -r '.metrics.cost_estimate_usd // 0' "$STATE_FILE")
    echo "║  💰 Estimated Cost: \$$cost"
    echo "╚═══════════════════════════════════════════════════════════════╝"
}

#==============================================================================
# 실행
#==============================================================================
init_research

if [ -n "$2" ]; then
    # 새 질문으로 시작
    run_research "$2"
else
    # 기존 세션 계속 또는 재개
    run_research ""
fi
