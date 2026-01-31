#!/usr/bin/env python3
"""
Memory Manager: 3-tier memory architecture (Letta-inspired)
Based on RESEARCH_REPORT.md recommendations

Working Memory:  최근 10 iterations (hot context)
Semantic Memory: 핵심 발견 사항 (structured knowledge)
Archival Memory: 전체 iteration 로그 (cold storage)

Usage:
    from memory_manager import MemoryManager

    mm = MemoryManager()
    mm.update_working_memory(iteration=5, findings=[...])
    working = mm.get_working_memory()  # Recent 10 iterations only
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime


CURRENT_SESSION_DIR = ".research/current"  # Symlink to active session
WORKING_MEMORY_FILE = f"{CURRENT_SESSION_DIR}/working_memory.json"
SEMANTIC_MEMORY_FILE = f"{CURRENT_SESSION_DIR}/findings.md"
ARCHIVAL_DIR = f"{CURRENT_SESSION_DIR}/archival/"
STATE_FILE = f"{CURRENT_SESSION_DIR}/state.json"

OBSERVATION_WINDOW = 10  # JetBrains Research recommendation


class MemoryManager:
    """3-tier memory architecture for research agent."""

    def __init__(self):
        self.working = self._load_working()

    def _load_working(self) -> Dict:
        """Load working memory from file."""
        try:
            with open(WORKING_MEMORY_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "version": "1.0",
                "window_size": OBSERVATION_WINDOW,
                "iterations": [],
                "last_updated": datetime.now().isoformat()
            }

    def _save_working(self):
        """Save working memory to file."""
        self.working["last_updated"] = datetime.now().isoformat()
        os.makedirs(os.path.dirname(WORKING_MEMORY_FILE), exist_ok=True)
        with open(WORKING_MEMORY_FILE, 'w') as f:
            json.dump(self.working, f, indent=2)

    def update_working_memory(
        self,
        iteration: int,
        findings: List[Dict],
        queries_executed: List[str],
        active_hypotheses: List[str],
        next_actions: List[str]
    ):
        """
        Update working memory with new iteration data.
        Automatically maintains observation window (latest 10 iterations).

        Args:
            iteration: Current iteration number
            findings: List of findings from this iteration
            queries_executed: Search queries executed
            active_hypotheses: Top 5 hypothesis IDs
            next_actions: Planned actions for next iteration
        """
        iteration_data = {
            "iteration": iteration,
            "timestamp": datetime.now().isoformat(),
            "findings": findings,
            "queries": queries_executed,
            "active_hypotheses": active_hypotheses,
            "next_actions": next_actions
        }

        # Add to iterations list
        self.working["iterations"].append(iteration_data)

        # Observation masking: keep only recent OBSERVATION_WINDOW iterations
        if len(self.working["iterations"]) > OBSERVATION_WINDOW:
            # Archive old iterations before removing
            archived = self.working["iterations"][:-OBSERVATION_WINDOW]
            self._archive_iterations(archived)

            # Keep only recent window
            self.working["iterations"] = self.working["iterations"][-OBSERVATION_WINDOW:]

        self._save_working()

    def _archive_iterations(self, iterations: List[Dict]):
        """
        Archive old iterations to cold storage.

        Args:
            iterations: List of iteration data to archive
        """
        os.makedirs(ARCHIVAL_DIR, exist_ok=True)

        for iter_data in iterations:
            iter_num = iter_data["iteration"]
            archive_file = os.path.join(ARCHIVAL_DIR, f"iteration_{iter_num:03d}.json")

            with open(archive_file, 'w') as f:
                json.dump(iter_data, f, indent=2)

    def get_working_memory(self) -> Dict:
        """
        Get working memory (recent OBSERVATION_WINDOW iterations).

        Returns:
            Working memory dict with recent iterations
        """
        return self.working

    def get_recent_iterations(self, count: int = 5) -> List[Dict]:
        """
        Get most recent N iterations.

        Args:
            count: Number of recent iterations to retrieve

        Returns:
            List of iteration data (most recent first)
        """
        iterations = self.working["iterations"]
        return list(reversed(iterations[-count:]))

    def update_semantic_memory(self, findings_md_content: str):
        """
        Update semantic memory (findings.md).

        Args:
            findings_md_content: Markdown content for findings
        """
        os.makedirs(os.path.dirname(SEMANTIC_MEMORY_FILE), exist_ok=True)
        with open(SEMANTIC_MEMORY_FILE, 'w') as f:
            f.write(findings_md_content)

    def get_semantic_memory(self) -> str:
        """
        Get semantic memory (findings.md).

        Returns:
            Markdown content of findings
        """
        try:
            with open(SEMANTIC_MEMORY_FILE, 'r') as f:
                return f.read()
        except FileNotFoundError:
            return ""

    def retrieve_from_archival(self, iteration: int) -> Optional[Dict]:
        """
        Retrieve specific iteration from archival storage.

        Args:
            iteration: Iteration number to retrieve

        Returns:
            Iteration data or None if not found
        """
        archive_file = os.path.join(ARCHIVAL_DIR, f"iteration_{iteration:03d}.json")

        try:
            with open(archive_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    def get_statistics(self) -> Dict:
        """Get memory statistics."""
        working_iters = len(self.working["iterations"])

        # Count archival files
        archival_count = 0
        if os.path.exists(ARCHIVAL_DIR):
            archival_count = len([f for f in os.listdir(ARCHIVAL_DIR) if f.endswith('.json')])

        # Semantic memory size
        semantic_size = 0
        if os.path.exists(SEMANTIC_MEMORY_FILE):
            semantic_size = os.path.getsize(SEMANTIC_MEMORY_FILE)

        return {
            "working_memory": {
                "iterations": working_iters,
                "window_size": OBSERVATION_WINDOW,
                "usage": f"{working_iters}/{OBSERVATION_WINDOW}"
            },
            "semantic_memory": {
                "size_bytes": semantic_size,
                "size_kb": round(semantic_size / 1024, 2)
            },
            "archival_memory": {
                "iterations_archived": archival_count
            },
            "total_iterations": working_iters + archival_count
        }

    def truncate_findings_for_context(self, max_findings: int = 30) -> str:
        """
        Get truncated findings for context (Observation masking).

        Args:
            max_findings: Maximum number of findings to include

        Returns:
            Truncated findings.md content
        """
        full_content = self.get_semantic_memory()

        if not full_content:
            return ""

        # Simple truncation: take last N findings
        lines = full_content.split('\n')

        # Count findings (lines starting with '- ')
        finding_count = 0
        truncated_lines = []

        for line in reversed(lines):
            if line.strip().startswith('- '):
                finding_count += 1
                if finding_count > max_findings:
                    break
            truncated_lines.insert(0, line)

        return '\n'.join(truncated_lines)


def main():
    """CLI interface for testing."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python memory_manager.py <command>")
        print("Commands:")
        print("  stats           - Show memory statistics")
        print("  working         - Display working memory")
        print("  archival <N>    - Retrieve iteration N from archival")
        sys.exit(1)

    mm = MemoryManager()
    command = sys.argv[1]

    if command == "stats":
        stats = mm.get_statistics()
        print("\n📊 Memory Statistics")
        print("=" * 50)
        print(f"\nWorking Memory (Hot):")
        print(f"  Iterations: {stats['working_memory']['usage']}")
        print(f"  Window Size: {stats['working_memory']['window_size']}")
        print(f"\nSemantic Memory (Structured):")
        print(f"  Size: {stats['semantic_memory']['size_kb']} KB")
        print(f"\nArchival Memory (Cold):")
        print(f"  Archived: {stats['archival_memory']['iterations_archived']} iterations")
        print(f"\nTotal: {stats['total_iterations']} iterations processed")

    elif command == "working":
        working = mm.get_working_memory()
        print(f"\n📝 Working Memory (Recent {working['window_size']} Iterations)")
        print("=" * 50)
        for iter_data in working["iterations"]:
            print(f"\nIteration {iter_data['iteration']}:")
            print(f"  Timestamp: {iter_data['timestamp']}")
            print(f"  Findings: {len(iter_data.get('findings', []))}")
            print(f"  Queries: {len(iter_data.get('queries', []))}")
            print(f"  Active Hypotheses: {iter_data.get('active_hypotheses', [])}")

    elif command == "archival" and len(sys.argv) >= 3:
        iteration = int(sys.argv[2])
        data = mm.retrieve_from_archival(iteration)
        if data:
            print(f"\n📦 Archival - Iteration {iteration}")
            print("=" * 50)
            print(json.dumps(data, indent=2))
        else:
            print(f"❌ Iteration {iteration} not found in archival")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
