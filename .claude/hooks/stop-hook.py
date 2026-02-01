#!/usr/bin/env python3
"""
Stop Hook: Rabbit-Hole Multi-Session Ralph Loop

사용자만 탐험을 멈출 수 있습니다!
- 여러 터미널에서 동시 /rh 실행 가능
- 각 세션이 독립적으로 Ralph Loop 실행
- UUID 기반 세션 격리 (session_mapping.json)

안전장치:
  - Max iterations (무한 루프 방지)
  - 사용자 중단 (Ctrl+C)
"""

import json
import sys
import os
import fcntl

# Session mapping (UUID → session directory)
SESSION_MAPPING_FILE = ".research/session_mapping.json"
MAPPING_LOCK_FILE = ".research/.mapping.lock"

MAX_ITERATIONS = 100


def find_unmapped_session(existing_mapping):
    """
    Find the newest session directory that hasn't been mapped to a UUID yet.
    Returns session path like "sessions/research_20260201_183250" or None.
    """
    sessions_dir = ".research/sessions"

    if not os.path.exists(sessions_dir):
        return None

    try:
        # Get all session directories, sorted by name (newest first due to timestamp)
        all_sessions = sorted(os.listdir(sessions_dir), reverse=True)
    except OSError:
        return None

    # Get set of already mapped session paths
    mapped_sessions = set(existing_mapping.values())

    # Find first unmapped session
    for session_name in all_sessions:
        session_path = f"sessions/{session_name}"
        if session_path not in mapped_sessions:
            # Verify it's actually a directory
            full_path = os.path.join(".research", session_path)
            if os.path.isdir(full_path):
                return session_path

    return None


def ensure_session_mapping(session_id):
    """
    Ensure UUID is mapped to a session directory.
    Uses file locking to prevent race conditions when multiple sessions start simultaneously.

    Returns: session path like "sessions/research_20260201_183250"
    """
    # Handle empty session_id
    if not session_id:
        # Fallback to current symlink
        try:
            return os.readlink(".research/current")
        except:
            return "sessions/unknown"

    # Try to acquire lock (with timeout for safety)
    try:
        lock = open(MAPPING_LOCK_FILE, 'w')
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
    except:
        # If locking fails, fallback to current symlink (best effort)
        try:
            return os.readlink(".research/current")
        except:
            return "sessions/unknown"

    try:
        # Load existing mapping
        mapping = {}
        if os.path.exists(SESSION_MAPPING_FILE):
            try:
                with open(SESSION_MAPPING_FILE, 'r') as f:
                    mapping = json.load(f)
            except (json.JSONDecodeError, IOError):
                # Corrupted mapping file - start fresh
                mapping = {}

        # Check if already mapped
        if session_id in mapping:
            result = mapping[session_id]
            # Verify the mapped path still exists
            full_path = os.path.join(".research", result)
            if os.path.exists(full_path):
                return result
            else:
                # Mapped session was deleted - remove from mapping
                del mapping[session_id]

        # Find unmapped session
        unmapped = find_unmapped_session(mapping)

        if unmapped:
            session_path = unmapped
        else:
            # No unmapped sessions - fallback to current symlink
            try:
                session_path = os.readlink(".research/current")
            except:
                session_path = "sessions/unknown"

        # Save mapping
        mapping[session_id] = session_path
        try:
            with open(SESSION_MAPPING_FILE, 'w') as f:
                json.dump(mapping, f, indent=2)
        except IOError:
            pass  # Failed to save, but continue with the mapping

        return session_path

    finally:
        # Always release lock
        try:
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
            lock.close()
        except:
            pass


def build_continue_prompt(holes_data):
    """Build the prompt to continue rabbit-hole exploration"""
    iteration = holes_data.get("iteration", 0)
    pending = holes_data.get("pending", [])

    prompt = f"""🐰 Iteration {iteration + 1} 시작

pending: {len(pending)}개

**SPAWN부터 시작:**
1. SPAWN: pending < 3이면 holes 생성
2. SELECT: interest 높은 hole 선택
3. EXPLORE: WebSearch
4. SAVE: evidence → claim → 출력"""

    return prompt


def cleanup_and_approve(marker_file, reason):
    """마커 파일 정리 후 종료 허용"""
    try:
        if os.path.exists(marker_file):
            os.remove(marker_file)
    except:
        pass

    output = {
        "decision": "approve",
        "reason": reason
    }
    print(json.dumps(output))
    sys.exit(0)


def handle_rabbit_hole(session_id, marker_file):
    """
    🐰 Rabbit-Hole Ralph Loop
    holes.json 기반으로 다음 iteration 자동 실행
    Multi-session 지원: UUID를 세션 디렉토리에 매핑하여 각 세션 독립적으로 실행
    """
    # Get session directory for this UUID
    session_path = ensure_session_mapping(session_id)
    holes_file = os.path.join(".research", session_path, "holes.json")

    # Load holes.json from session-specific directory
    try:
        with open(holes_file, 'r') as f:
            holes_data = json.load(f)
    except FileNotFoundError:
        cleanup_and_approve(marker_file, f"No holes.json in {session_path}")
        return
    except json.JSONDecodeError:
        cleanup_and_approve(marker_file, f"Corrupted holes.json in {session_path}")
        return

    iteration = holes_data.get("iteration", 0)
    pending = holes_data.get("pending", [])

    # ═══════════════════════════════════════════════════════════════
    # 안전장치 체크
    # ═══════════════════════════════════════════════════════════════
    should_stop = False
    reason = ""

    # 1. Max iterations
    if iteration >= MAX_ITERATIONS:
        should_stop = True
        reason = f"🚫 Max iterations ({MAX_ITERATIONS}) reached"

    # 2. Pending holes 없고 더 이상 탐색할 게 없음 (50 iteration 넘으면)
    # 참고: pending 없어도 SPAWN에서 새로 생성하므로 보통은 계속됨
    elif iteration >= 50 and len(pending) == 0:
        should_stop = True
        reason = "🏁 50+ iterations with no pending holes"

    if should_stop:
        cleanup_and_approve(marker_file, reason)
        return

    # ═══════════════════════════════════════════════════════════════
    # 🐰 Ralph Loop: 종료 차단 + 다음 iteration 지시
    # ═══════════════════════════════════════════════════════════════
    continue_prompt = build_continue_prompt(holes_data)

    output = {
        "decision": "block",
        "reason": f"🐰 Iteration {iteration} 완료 | Ralph Loop 계속!",
        "stopReason": continue_prompt
    }
    print(json.dumps(output))
    sys.exit(0)


def main():
    # Hook 입력 읽기 (stdin)
    try:
        hook_input = json.load(sys.stdin)
    except:
        hook_input = {}

    current_session_id = hook_input.get("session_id", "")
    marker_file = f".research/.rh_{current_session_id}"

    # rabbit-hole 세션 여부 확인
    is_rabbit_hole = os.path.exists(marker_file)

    if is_rabbit_hole:
        handle_rabbit_hole(current_session_id, marker_file)
    else:
        # Rabbit-hole 세션 아니면 그냥 통과
        output = {
            "decision": "approve",
            "reason": "Not a rabbit-hole session"
        }
        print(json.dumps(output))
        sys.exit(0)


if __name__ == "__main__":
    main()
