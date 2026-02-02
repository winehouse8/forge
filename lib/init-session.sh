#!/bin/bash
# Pathfinder 세션 초기화 - 새 연구 세션 생성 (v2)

set -e

QUESTION="$1"
[ -z "$QUESTION" ] && { echo "Usage: init-session.sh \"question\""; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

SESSION_ID="research_$(date +%Y%m%d_%H%M%S)"

mkdir -p ".research/sessions/${SESSION_ID}/observations"
mkdir -p ".research/sessions/${SESSION_ID}/hypotheses"
echo "${SESSION_ID}" > ".research/sessions/${SESSION_ID}/.session_id"
ln -sfn "sessions/${SESSION_ID}" .research/current
echo "${SESSION_ID}" > ".research/.rh_active"

[ ! -d ".research/current" ] && { echo "Error: Session creation failed"; exit 1; }

cat > ".research/sessions/${SESSION_ID}/cognigraph.json" << EOF
{
  "question": "${QUESTION}",
  "iteration": 0,
  "observations": {},
  "hypotheses": {},
  "edges": [],
  "lens_index": 0,
  "unexplored": [],
  "health": {
    "last_check": 0,
    "issues": []
  }
}
EOF

echo "New session: ${SESSION_ID}"
