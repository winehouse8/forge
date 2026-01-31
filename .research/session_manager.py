#!/usr/bin/env python3
"""
Session Manager: Multi-session research management
Prevents data loss when starting new research while another is in progress

Usage:
    from session_manager import SessionManager

    sm = SessionManager()

    # Find similar sessions (automatic)
    similar = sm.find_similar_sessions("양자 컴퓨팅 최신 동향")

    # Create new session (auto-called if no similar found)
    session_id = sm.create_session("양자 컴퓨팅 최신 동향")

    # List all sessions
    sessions = sm.list_sessions()

    # Switch session
    sm.switch_session(session_id)

    # Get current session
    current = sm.get_current_session()
"""

import json
import os
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import re

# Try to import embedding functions
try:
    from deduplicate_search import get_embedding, cosine_similarity
    EMBEDDING_AVAILABLE = True
except ImportError:
    EMBEDDING_AVAILABLE = False
    print("⚠️  Warning: deduplicate_search not available. Similarity search disabled.", file=__import__('sys').stderr)


SESSIONS_DIR = ".research/sessions"
CURRENT_LINK = ".research/current"
SESSION_INDEX = ".research/sessions/index.json"


class SessionManager:
    """Manage multiple research sessions to prevent data loss."""

    def __init__(self):
        self._ensure_dirs()
        self.index = self._load_index()

    def _ensure_dirs(self):
        """Ensure session directories exist."""
        os.makedirs(SESSIONS_DIR, exist_ok=True)

    def _load_index(self) -> Dict:
        """Load session index."""
        try:
            with open(SESSION_INDEX, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "version": "1.0",
                "sessions": {},
                "current_session": None,
                "last_updated": datetime.now().isoformat()
            }

    def _save_index(self):
        """Save session index."""
        self.index["last_updated"] = datetime.now().isoformat()
        with open(SESSION_INDEX, 'w') as f:
            json.dump(self.index, f, indent=2)

    def _generate_session_id(self, question: str) -> str:
        """
        Generate session ID from timestamp and question.

        Format: research_YYYYMMDD_HHMMSS_slug
        Example: research_20260201_143022_quantum_computing
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create slug from question (first 3 words, cleaned)
        words = re.findall(r'\w+', question.lower())[:3]
        slug = '_'.join(words) if words else 'research'

        return f"research_{timestamp}_{slug}"

    def create_session(
        self,
        question: str,
        session_id: Optional[str] = None,
        auto_switch: bool = True
    ) -> str:
        """
        Create a new research session.

        Args:
            question: Research question
            session_id: Custom session ID (auto-generated if None)
            auto_switch: Automatically switch to new session

        Returns:
            Session ID
        """
        # Generate session ID if not provided
        if session_id is None:
            session_id = self._generate_session_id(question)

        # Check if session already exists
        if session_id in self.index["sessions"]:
            raise ValueError(f"Session already exists: {session_id}")

        # Create session directory
        session_dir = os.path.join(SESSIONS_DIR, session_id)
        os.makedirs(session_dir, exist_ok=True)
        os.makedirs(os.path.join(session_dir, "archival"), exist_ok=True)

        # Initialize session metadata
        self.index["sessions"][session_id] = {
            "question": question,
            "created_at": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat(),
            "status": "initialized",
            "iteration": 0,
            "directory": session_dir
        }

        # Auto-switch to new session
        if auto_switch:
            self.switch_session(session_id)

        self._save_index()

        return session_id

    def switch_session(self, session_id: str):
        """
        Switch to a different session.

        Args:
            session_id: Target session ID
        """
        if session_id not in self.index["sessions"]:
            raise ValueError(f"Session not found: {session_id}")

        session_dir = os.path.join(SESSIONS_DIR, session_id)

        # Remove old symlink if exists
        if os.path.islink(CURRENT_LINK) or os.path.exists(CURRENT_LINK):
            os.remove(CURRENT_LINK)

        # Create new symlink to session directory
        os.symlink(session_dir, CURRENT_LINK, target_is_directory=True)

        # Update current session
        self.index["current_session"] = session_id
        self.index["sessions"][session_id]["last_accessed"] = datetime.now().isoformat()

        self._save_index()

    def get_current_session(self) -> Optional[Dict]:
        """
        Get current active session.

        Returns:
            Session metadata or None if no active session
        """
        current_id = self.index.get("current_session")
        if not current_id:
            return None

        session = self.index["sessions"].get(current_id)
        if session:
            session["id"] = current_id

        return session

    def list_sessions(self, status_filter: Optional[str] = None) -> List[Dict]:
        """
        List all sessions.

        Args:
            status_filter: Filter by status (initialized, running, paused, completed)

        Returns:
            List of session metadata
        """
        sessions = []

        for session_id, metadata in self.index["sessions"].items():
            if status_filter and metadata.get("status") != status_filter:
                continue

            session_info = metadata.copy()
            session_info["id"] = session_id
            sessions.append(session_info)

        # Sort by last accessed (most recent first)
        sessions.sort(key=lambda s: s.get("last_accessed", ""), reverse=True)

        return sessions

    def delete_session(self, session_id: str, confirm: bool = False):
        """
        Delete a session and its data.

        Args:
            session_id: Session ID to delete
            confirm: Safety confirmation (must be True)
        """
        if not confirm:
            raise ValueError("Must confirm deletion with confirm=True")

        if session_id not in self.index["sessions"]:
            raise ValueError(f"Session not found: {session_id}")

        # Cannot delete current session
        if self.index.get("current_session") == session_id:
            raise ValueError("Cannot delete current session. Switch to another session first.")

        # Delete session directory
        session_dir = os.path.join(SESSIONS_DIR, session_id)
        if os.path.exists(session_dir):
            shutil.rmtree(session_dir)

        # Remove from index
        del self.index["sessions"][session_id]

        self._save_index()

    def update_session_status(self, session_id: str, status: str, iteration: Optional[int] = None):
        """
        Update session status.

        Args:
            session_id: Session ID
            status: New status (running, paused, completed, etc.)
            iteration: Current iteration number
        """
        if session_id not in self.index["sessions"]:
            raise ValueError(f"Session not found: {session_id}")

        self.index["sessions"][session_id]["status"] = status
        self.index["sessions"][session_id]["last_accessed"] = datetime.now().isoformat()

        if iteration is not None:
            self.index["sessions"][session_id]["iteration"] = iteration

        self._save_index()

    def get_session_path(self, session_id: Optional[str] = None) -> str:
        """
        Get absolute path to session directory.

        Args:
            session_id: Session ID (uses current if None)

        Returns:
            Absolute path to session directory
        """
        if session_id is None:
            session_id = self.index.get("current_session")
            if not session_id:
                raise ValueError("No current session active")

        if session_id not in self.index["sessions"]:
            raise ValueError(f"Session not found: {session_id}")

        return os.path.abspath(os.path.join(SESSIONS_DIR, session_id))

    def find_similar_sessions(
        self,
        question: str,
        threshold: float = 0.8,
        exact_threshold: float = 0.95
    ) -> Tuple[List[Dict], str]:
        """
        Find sessions with similar questions using embedding similarity.

        Args:
            question: Research question to compare
            threshold: Minimum similarity for "similar" (default: 0.8)
            exact_threshold: Minimum similarity for "exact match" (default: 0.95)

        Returns:
            (similar_sessions, match_type)
            - similar_sessions: List of similar session metadata with similarity scores
            - match_type: "exact" (>0.95), "similar" (>0.8), or "none"
        """
        if not EMBEDDING_AVAILABLE:
            # Fallback: simple string matching
            similar = []
            for session_id, metadata in self.index["sessions"].items():
                if question.lower() == metadata["question"].lower():
                    similar.append({
                        "id": session_id,
                        "question": metadata["question"],
                        "similarity": 1.0,
                        "iteration": metadata.get("iteration", 0),
                        "status": metadata.get("status", "unknown")
                    })

            match_type = "exact" if similar else "none"
            return similar, match_type

        # Get embedding for new question
        question_emb = get_embedding(question)
        if question_emb is None:
            return [], "none"

        similar_sessions = []

        # Compare with all existing sessions
        for session_id, metadata in self.index["sessions"].items():
            past_question = metadata["question"]

            # Get or compute embedding for past question
            if "question_embedding" not in metadata:
                past_emb = get_embedding(past_question)
                if past_emb:
                    metadata["question_embedding"] = past_emb
                    self._save_index()  # Save embedding for future use
            else:
                past_emb = metadata["question_embedding"]

            if past_emb is None:
                continue

            # Calculate similarity
            similarity = cosine_similarity(question_emb, past_emb)

            if similarity >= threshold:
                similar_sessions.append({
                    "id": session_id,
                    "question": past_question,
                    "similarity": round(similarity, 3),
                    "iteration": metadata.get("iteration", 0),
                    "status": metadata.get("status", "unknown"),
                    "last_accessed": metadata.get("last_accessed", "")
                })

        # Sort by similarity (highest first)
        similar_sessions.sort(key=lambda s: s["similarity"], reverse=True)

        # Determine match type
        if similar_sessions and similar_sessions[0]["similarity"] >= exact_threshold:
            match_type = "exact"
        elif similar_sessions:
            match_type = "similar"
        else:
            match_type = "none"

        return similar_sessions, match_type


def main():
    """CLI interface for testing."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python session_manager.py <command>")
        print("Commands:")
        print("  create <question>     - Create new session")
        print("  list                  - List all sessions")
        print("  switch <session_id>   - Switch to session")
        print("  current               - Show current session")
        print("  delete <session_id>   - Delete session")
        sys.exit(1)

    sm = SessionManager()
    command = sys.argv[1]

    if command == "create" and len(sys.argv) >= 3:
        question = " ".join(sys.argv[2:])
        session_id = sm.create_session(question)
        print(f"✓ Created session: {session_id}")
        print(f"  Question: {question}")

    elif command == "list":
        sessions = sm.list_sessions()
        current = sm.get_current_session()

        print(f"\n📋 Research Sessions ({len(sessions)} total)")
        print("=" * 80)

        for session in sessions:
            marker = "→" if current and session["id"] == current["id"] else " "
            print(f"{marker} {session['id']}")
            print(f"  Question: {session['question']}")
            print(f"  Status: {session['status']} | Iteration: {session.get('iteration', 0)}")
            print(f"  Last accessed: {session['last_accessed']}")
            print()

    elif command == "switch" and len(sys.argv) >= 3:
        session_id = sys.argv[2]
        sm.switch_session(session_id)
        print(f"✓ Switched to session: {session_id}")

    elif command == "current":
        current = sm.get_current_session()
        if current:
            print(f"\n→ Current Session: {current['id']}")
            print(f"  Question: {current['question']}")
            print(f"  Status: {current['status']}")
            print(f"  Iteration: {current.get('iteration', 0)}")
        else:
            print("No current session active")

    elif command == "delete" and len(sys.argv) >= 3:
        session_id = sys.argv[2]
        sm.delete_session(session_id, confirm=True)
        print(f"✓ Deleted session: {session_id}")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
