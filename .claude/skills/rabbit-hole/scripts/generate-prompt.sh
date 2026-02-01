#!/bin/bash
# 🐰 Rabbit-Hole 프롬프트 생성기
# Usage: ./generate-prompt.sh
# 현재 세션의 질문과 SKILL.md를 결합하여 프롬프트 출력

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(cd "$SKILL_DIR/../../.." && pwd)"
RESEARCH_DIR="$PROJECT_ROOT/.research"

# 현재 질문 가져오기
QUESTION=$(jq -r '.question // "연구 질문이 설정되지 않았습니다"' "$RESEARCH_DIR/current/holes.json" 2>/dev/null)

# 프롬프트 출력
cat << HEADER
# 🐰 현재 연구 질문

**질문:** $QUESTION

**세션 디렉토리:** .research/current/

---

HEADER

# SKILL.md 내용 추가
cat "$SKILL_DIR/SKILL.md"
