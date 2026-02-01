#!/bin/bash
# Pathfinder 세션 초기화 - 새 연구 세션 생성

set -e

QUESTION="$1"
[ -z "$QUESTION" ] && { echo "Usage: init-session.sh \"question\""; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

SESSION_ID="research_$(date +%Y%m%d_%H%M%S)"

mkdir -p ".research/sessions/${SESSION_ID}/claims"
mkdir -p ".research/sessions/${SESSION_ID}/evidence"
echo "${SESSION_ID}" > ".research/sessions/${SESSION_ID}/.session_id"
ln -sfn "sessions/${SESSION_ID}" .research/current
echo "${SESSION_ID}" > ".research/.rh_active"

[ ! -d ".research/current" ] && { echo "Error: Session creation failed"; exit 1; }

cat > ".research/sessions/${SESSION_ID}/holes.json" << EOF
{
  "question": "${QUESTION}",
  "pending": [],
  "explored": [],
  "next_id": 1,
  "iteration": 0
}
EOF

cat > ".research/sessions/${SESSION_ID}/summary.md" << EOF
# 연구: ${QUESTION}

## 질문
${QUESTION}

## Claims
| ID | 내용 | 상태 | 강도 | 증거 |
|----|------|------|------|------|
| - | (없음) | - | - | - |

## Pending Holes
| ID | 타입 | 질문 | 관심도 |
|----|------|------|--------|
| - | (SPAWN 대기) | - | - |

## 미탐색 영역
- 전체 주제 탐색 필요

---
iteration 0 | claims: 0 | evidence: 0 | explored: 0
EOF

echo "New session: ${SESSION_ID}"
