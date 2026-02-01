#!/bin/bash
# Pathfinder 프롬프트 생성 - 질문 + research-cycle.md 결합

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
RESEARCH_DIR="$PROJECT_ROOT/.research"
PROMPTS_DIR="$PROJECT_ROOT/prompts"

QUESTION=$(python3 -c "import json; data=json.load(open('$RESEARCH_DIR/current/holes.json')); print(data.get('question', 'N/A'))" 2>/dev/null || echo "N/A")

cat << HEADER
# 현재 연구 질문

**질문:** $QUESTION

**세션:** .research/current/

---

HEADER

cat "$PROMPTS_DIR/research-cycle.md"
