#!/usr/bin/env python3
"""
Test hook to check current session_id
"""

import json
import sys

try:
    hook_input = json.load(sys.stdin)
    session_id = hook_input.get("session_id", "UNKNOWN")

    # Write to debug file
    with open(".research/.current_session_id.txt", 'w') as f:
        f.write(f"Current session_id: {session_id}\n")

    print(f"Session ID: {session_id[:16]}...")
except Exception as e:
    print(f"Error: {e}")

sys.exit(0)
