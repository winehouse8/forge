#!/bin/bash
# Rabbit-Hole 세션 초기화 스크립트
# 새 연구 세션을 생성하고 초기 파일들을 준비합니다.

set -e  # 에러 시 즉시 종료

QUESTION="$1"

if [ -z "$QUESTION" ]; then
    echo "❌ Error: Research question required"
    echo "Usage: init.sh \"your research question\""
    exit 1
fi

# 프로젝트 루트 찾기 (Git 루트 또는 현재 디렉토리)
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$REPO_ROOT"

# 세션 ID 생성
SESSION_ID="research_$(date +%Y%m%d_%H%M%S)"

# 세션 디렉토리 생성 (프로젝트 루트 기준)
mkdir -p ".research/sessions/${SESSION_ID}/claims"
mkdir -p ".research/sessions/${SESSION_ID}/evidence"

# .session_id 파일 생성 (직접 경로)
echo "${SESSION_ID}" > ".research/sessions/${SESSION_ID}/.session_id"

# current symlink 생성
ln -sfn "sessions/${SESSION_ID}" .research/current

# 검증
if [ ! -d ".research/current" ]; then
    echo "❌ Error: Session directory creation failed"
    exit 1
fi

# holes.json 초기화
cat > ".research/sessions/${SESSION_ID}/holes.json" << EOF
{
  "question": "${QUESTION}",
  "pending": [],
  "explored": [],
  "next_id": 1,
  "iteration": 0
}
EOF

# summary.md 초기화
cat > ".research/sessions/${SESSION_ID}/summary.md" << EOF
# Research: ${QUESTION}

## Claims
| ID | Statement | Status | Strength | Evidence |
|----|-----------|--------|----------|----------|
| - | (아직 없음) | - | - | - |

## Pending Holes
| ID | Type | Question | Interest |
|----|------|----------|----------|
| - | (SPAWN 대기) | - | - |

## Open Gaps
- 전체 주제 탐색 필요

---
iteration 0 | claims: 0 | evidence: 0 | explored: 0
EOF

echo "✓ Session created: ${SESSION_ID}"
echo "✓ Directory: .research/sessions/${SESSION_ID}/"
echo "✓ Files: holes.json, summary.md"
