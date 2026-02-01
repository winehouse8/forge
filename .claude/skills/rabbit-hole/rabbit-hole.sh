#!/bin/bash
# 🐰 Rabbit-Hole - Deep Research Agent
# Usage: ./rabbit-hole.sh "질문" [max_iterations]
#        ./rabbit-hole.sh --resume

set -e

# Ctrl+C로 완전 종료
trap 'echo ""; echo "🛑 중단됨. --resume으로 재개 가능"; exit 130' INT

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
RESEARCH_DIR="$PROJECT_ROOT/.research"
MAX_ITERATIONS=50

# ═══════════════════════════════════════════════════════════════
# Parse arguments
# ═══════════════════════════════════════════════════════════════
QUESTION=""
RESUME=false
QUESTION_PARTS=()

while [[ $# -gt 0 ]]; do
  case $1 in
    --resume|-r) RESUME=true; shift ;;
    --max|-m) MAX_ITERATIONS="$2"; shift 2 ;;
    /rh|/rabbit-hole) shift ;;
    *)
      if [[ "$1" =~ ^[0-9]+$ ]]; then
        MAX_ITERATIONS="$1"
      else
        QUESTION_PARTS+=("$1")
      fi
      shift ;;
  esac
done

if [ ${#QUESTION_PARTS[@]} -gt 0 ]; then
  QUESTION="${QUESTION_PARTS[*]}"
fi

# ═══════════════════════════════════════════════════════════════
# Initialize or Resume
# ═══════════════════════════════════════════════════════════════
if [ "$RESUME" = true ]; then
  if [ ! -L "$RESEARCH_DIR/current" ]; then
    echo "❌ No session to resume"
    exit 1
  fi
  QUESTION=$(jq -r '.question' "$RESEARCH_DIR/current/holes.json" 2>/dev/null)
  echo "🔄 Resuming: $QUESTION"
elif [ -n "$QUESTION" ]; then
  # New session
  TIMESTAMP=$(date +%Y%m%d_%H%M%S)
  SESSION_DIR="$RESEARCH_DIR/sessions/research_$TIMESTAMP"
  mkdir -p "$SESSION_DIR/claims" "$SESSION_DIR/evidence"

  echo "{\"question\": \"$QUESTION\", \"pending\": [], \"explored\": [], \"next_id\": 1, \"iteration\": 0}" > "$SESSION_DIR/holes.json"
  echo "# Research: $QUESTION" > "$SESSION_DIR/summary.md"

  ln -sfn "sessions/research_$TIMESTAMP" "$RESEARCH_DIR/current"
  echo "✅ New session: research_$TIMESTAMP"
else
  echo "Usage: ./rabbit-hole.sh \"질문\" [max]"
  echo "       ./rabbit-hole.sh --resume"
  exit 1
fi

echo "📁 $RESEARCH_DIR/current"
echo ""

# ═══════════════════════════════════════════════════════════════
# Main Loop
# ═══════════════════════════════════════════════════════════════
LAST_ITER=-1
STALL_COUNT=0

for i in $(seq 1 $MAX_ITERATIONS); do
  # 현재 상태 읽기
  ITER=$(jq -r '.iteration // 0' "$RESEARCH_DIR/current/holes.json" 2>/dev/null || echo 0)
  PENDING=$(jq -r '.pending | length' "$RESEARCH_DIR/current/holes.json" 2>/dev/null || echo 0)
  STATUS=$(jq -r '.status // "running"' "$RESEARCH_DIR/current/holes.json" 2>/dev/null || echo "running")
  SATURATION=$(jq -r '.saturation.confirmed // false' "$RESEARCH_DIR/current/holes.json" 2>/dev/null || echo "false")

  # 완료 체크 (3가지 조건)
  if [ "$STATUS" = "COMPLETE" ]; then
    echo ""
    echo "🎉 Research complete! (status: COMPLETE)"
    exit 0
  fi

  if [ "$SATURATION" = "true" ]; then
    echo ""
    echo "🎉 Research complete! (saturation confirmed)"
    exit 0
  fi

  if [ "$ITER" -ge 50 ] && [ "$PENDING" -eq 0 ]; then
    echo ""
    echo "🎉 Research complete! iterations: $ITER"
    exit 0
  fi

  # iteration 정체 감지 (Claude가 iteration++ 안 하면)
  if [ "$ITER" -eq "$LAST_ITER" ]; then
    STALL_COUNT=$((STALL_COUNT + 1))
    if [ "$STALL_COUNT" -ge 3 ]; then
      echo ""
      echo "⚠️ Iteration stuck at $ITER for 3 loops. Check SKILL.md compliance."
      echo "   Claude may not be incrementing iteration in holes.json"
      exit 1
    fi
  else
    STALL_COUNT=0
  fi
  LAST_ITER=$ITER

  # 배너
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "🐰 Iteration $i/$MAX_ITERATIONS (current: $ITER, pending: $PENDING)"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

  # Claude 실행 (holes.json에서 상태 읽음)
  claude --dangerously-skip-permissions "/rh" || true

  echo ""
  sleep 1
done

echo "⚠️ Max iterations reached. Use --resume to continue."
