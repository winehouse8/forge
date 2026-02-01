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

echo ""
echo "📁 상세 내용: $RESEARCH_DIR/current/"
echo "   ├── summary.md      (지식 맵)"
echo "   ├── claims/         (주장들)"
echo "   └── evidence/       (근거들)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
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
  CLAIMS_COUNT=$(ls -1 "$RESEARCH_DIR/current/claims/" 2>/dev/null | wc -l | tr -d ' ')
  EVIDENCE_COUNT=$(ls -1 "$RESEARCH_DIR/current/evidence/" 2>/dev/null | wc -l | tr -d ' ')

  if [ "$STATUS" = "COMPLETE" ] || [ "$SATURATION" = "true" ] || ([ "$ITER" -ge 50 ] && [ "$PENDING" -eq 0 ]); then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🎉 Research Complete!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📊 최종 결과:"
    echo "   • Iterations: $ITER"
    echo "   • Claims: $CLAIMS_COUNT"
    echo "   • Evidence: $EVIDENCE_COUNT"
    echo ""
    echo "📁 결과 확인:"
    echo "   cat $RESEARCH_DIR/current/summary.md"
    echo ""
    echo "📝 보고서 생성:"
    echo "   ./rh-report.sh"
    echo ""
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
  CLAIMS_COUNT=$(ls -1 "$RESEARCH_DIR/current/claims/" 2>/dev/null | wc -l | tr -d ' ')
  EVIDENCE_COUNT=$(ls -1 "$RESEARCH_DIR/current/evidence/" 2>/dev/null | wc -l | tr -d ' ')

  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "🐰 Iteration $i/$MAX_ITERATIONS"
  echo "   📊 iter: $ITER | pending: $PENDING | claims: $CLAIMS_COUNT | evidence: $EVIDENCE_COUNT"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""

  # Claude 실행 (--print로 완료 후 종료, 출력 캡처)
  echo "⏳ 연구 중..."
  OUTPUT=$(claude --dangerously-skip-permissions --print "/rh" 2>&1) || true

  # 출력에서 주요 정보만 추출 (선택적)
  # echo "$OUTPUT"  # 전체 출력 보려면 주석 해제

  # 완료 신호 감지 (Ralph 패턴)
  if [[ "$OUTPUT" == *"<complete>DONE</complete>"* ]]; then
    FINAL_CLAIMS=$(ls -1 "$RESEARCH_DIR/current/claims/" 2>/dev/null | wc -l | tr -d ' ')
    FINAL_EVIDENCE=$(ls -1 "$RESEARCH_DIR/current/evidence/" 2>/dev/null | wc -l | tr -d ' ')
    FINAL_ITER=$(jq -r '.iteration // 0' "$RESEARCH_DIR/current/holes.json" 2>/dev/null || echo 0)

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🎉 Research Complete!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📊 최종 결과:"
    echo "   • Iterations: $FINAL_ITER"
    echo "   • Claims: $FINAL_CLAIMS"
    echo "   • Evidence: $FINAL_EVIDENCE"
    echo ""
    echo "📁 결과 확인:"
    echo "   cat $RESEARCH_DIR/current/summary.md"
    echo ""
    echo "📝 보고서 생성:"
    echo "   ./rh-report.sh"
    echo ""
    exit 0
  fi

  # 간단한 상태 업데이트
  NEW_ITER=$(jq -r '.iteration // 0' "$RESEARCH_DIR/current/holes.json" 2>/dev/null || echo 0)
  NEW_CLAIMS=$(ls -1 "$RESEARCH_DIR/current/claims/" 2>/dev/null | wc -l | tr -d ' ')

  echo "✅ Iteration $i 완료 (iter: $ITER→$NEW_ITER, claims: $CLAIMS_COUNT→$NEW_CLAIMS)"
  echo ""
  sleep 2
done

echo "⚠️ Max iterations reached. Use --resume to continue."
