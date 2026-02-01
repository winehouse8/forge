#!/bin/bash
# Rabbit-Hole 세션 정리 스크립트
# 오래된 세션, 빈 세션, 테스트 세션 정리

set -e

# 프로젝트 루트 찾기 (Git 루트 또는 현재 디렉토리)
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$REPO_ROOT"

SESSIONS_DIR=".research/sessions"
DRY_RUN="${1:-false}"  # 기본값: 실제 삭제

if [ ! -d "$SESSIONS_DIR" ]; then
    echo "ℹ️  No sessions directory found"
    exit 0
fi

echo "🧹 Rabbit-Hole Session Cleanup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 현재 세션 확인
CURRENT_SESSION=""
if [ -L ".research/current" ]; then
    CURRENT_SESSION=$(readlink .research/current | sed 's/sessions\///')
    echo "📌 Current session: $CURRENT_SESSION (보호됨)"
    echo ""
fi

# 정리 대상 찾기
EMPTY_SESSIONS=()
TEST_SESSIONS=()
OLD_SESSIONS=()

cd "$SESSIONS_DIR"

for session in */; do
    session=${session%/}  # 마지막 / 제거

    # 현재 세션은 건너뛰기
    if [ "$session" = "$CURRENT_SESSION" ]; then
        continue
    fi

    # 테스트 세션 확인
    if [[ "$session" == *"test"* ]]; then
        TEST_SESSIONS+=("$session")
        continue
    fi

    # 빈 세션 확인 (holes.json 없거나 iteration=0)
    if [ ! -f "$session/holes.json" ]; then
        EMPTY_SESSIONS+=("$session")
        continue
    fi

    iteration=$(grep -o '"iteration": [0-9]*' "$session/holes.json" | grep -o '[0-9]*' || echo "0")
    if [ "$iteration" = "0" ]; then
        EMPTY_SESSIONS+=("$session")
        continue
    fi

    # 7일 이상 오래된 세션 확인
    if [[ "$OSTYPE" == "darwin"* ]]; then
        session_time=$(stat -f %m "$session" 2>/dev/null || echo 0)
    else
        session_time=$(stat -c %Y "$session" 2>/dev/null || echo 0)
    fi
    current_time=$(date +%s)
    age_days=$(( (current_time - session_time) / 86400 ))

    if [ "$age_days" -gt 7 ]; then
        OLD_SESSIONS+=("$session")
    fi
done

cd - > /dev/null

# 결과 출력
total_count=$((${#EMPTY_SESSIONS[@]} + ${#TEST_SESSIONS[@]} + ${#OLD_SESSIONS[@]}))

if [ "$total_count" -eq 0 ]; then
    echo "✨ No sessions to clean up"
    exit 0
fi

echo "🗑️  Found $total_count sessions to clean:"
echo ""

if [ ${#EMPTY_SESSIONS[@]} -gt 0 ]; then
    echo "📭 Empty sessions (${#EMPTY_SESSIONS[@]}):"
    for session in "${EMPTY_SESSIONS[@]}"; do
        echo "   - $session"
    done
    echo ""
fi

if [ ${#TEST_SESSIONS[@]} -gt 0 ]; then
    echo "🧪 Test sessions (${#TEST_SESSIONS[@]}):"
    for session in "${TEST_SESSIONS[@]}"; do
        echo "   - $session"
    done
    echo ""
fi

if [ ${#OLD_SESSIONS[@]} -gt 0 ]; then
    echo "📅 Old sessions (${#OLD_SESSIONS[@]}, >7 days):"
    for session in "${OLD_SESSIONS[@]}"; do
        echo "   - $session"
    done
    echo ""
fi

# Dry run 체크
if [ "$DRY_RUN" = "true" ] || [ "$DRY_RUN" = "--dry-run" ]; then
    echo "ℹ️  Dry run mode - nothing deleted"
    echo "   Run without --dry-run to actually delete"
    exit 0
fi

# 실제 삭제
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🗑️  Deleting sessions..."
echo ""

deleted_count=0

for session in "${EMPTY_SESSIONS[@]}" "${TEST_SESSIONS[@]}" "${OLD_SESSIONS[@]}"; do
    rm -rf "$SESSIONS_DIR/$session"
    echo "   ✓ Deleted: $session"
    ((deleted_count++))
done

echo ""
echo "✅ Cleanup complete: $deleted_count sessions deleted"

# 레거시 파일 정리
echo ""
echo "🧹 Cleaning up legacy files..."
cd .research

legacy_cleaned=0

# 레거시 session_mapping.json 제거
if [ -f "session_mapping.json" ]; then
    rm -f "session_mapping.json"
    echo "   ✓ Removed: session_mapping.json"
    ((legacy_cleaned++))
fi

# 레거시 .mapping.lock 제거
if [ -f ".mapping.lock" ]; then
    rm -f ".mapping.lock"
    echo "   ✓ Removed: .mapping.lock"
    ((legacy_cleaned++))
fi

# 레거시 .rh_{uuid} 마커 제거 (새 .rh_active만 유지)
for marker in .rh_*; do
    if [ -f "$marker" ] && [ "$marker" != ".rh_active" ]; then
        rm -f "$marker"
        echo "   ✓ Removed legacy marker: $marker"
        ((legacy_cleaned++))
    fi
done

if [ "$legacy_cleaned" -gt 0 ]; then
    echo "✅ Removed $legacy_cleaned legacy files"
else
    echo "✨ No legacy files found"
fi
