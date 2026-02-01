#!/bin/bash
# 🎯 Rabbit-Hole Report Generator
# Usage: ./rh-report.sh [session_path]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
RESEARCH_DIR="$PROJECT_ROOT/.research"

SESSION_PATH="${1:-$RESEARCH_DIR/current}"

if [ ! -d "$SESSION_PATH" ] && [ ! -L "$SESSION_PATH" ]; then
  echo "❌ Session not found: $SESSION_PATH"
  exit 1
fi

echo "📝 Generating report for: $SESSION_PATH"
echo ""

claude -p --dangerously-skip-permissions "/rh-report"
