#!/usr/bin/env python3
"""
Knowledge Tracker: Lightweight knowledge graph using embeddings
Automatically tracks findings, detects contradictions, and maps relationships.

Usage (auto-called by SKILL.md SYNTHESIZE phase):
    from knowledge_tracker import KnowledgeTracker

    kt = KnowledgeTracker()
    kt.add_finding("ToT improves success by 74%", confidence=0.85, embedding=emb)
    contradictions = kt.detect_contradictions()
"""

import json
import os
from typing import List, Dict, Tuple, Optional
from datetime import datetime

# Reuse embedding infrastructure from deduplicate_search
try:
    from deduplicate_search import get_embedding, cosine_similarity, OPENAI_AVAILABLE
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️  Warning: deduplicate_search not available", file=__import__('sys').stderr)


KNOWLEDGE_FILE = ".research/knowledge_graph.json"
CONTRADICTION_THRESHOLD = 0.85  # High similarity but different confidence
RELATION_THRESHOLD = 0.70       # Related findings


class KnowledgeTracker:
    """Lightweight knowledge graph for research findings."""

    def __init__(self):
        self.data = self._load()

    def _load(self) -> Dict:
        """Load knowledge graph from file."""
        try:
            with open(KNOWLEDGE_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "version": "1.0",
                "nodes": [],
                "contradictions": [],
                "last_updated": datetime.now().isoformat()
            }

    def _save(self):
        """Save knowledge graph to file."""
        self.data["last_updated"] = datetime.now().isoformat()
        os.makedirs(os.path.dirname(KNOWLEDGE_FILE), exist_ok=True)
        with open(KNOWLEDGE_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)

    def add_finding(
        self,
        text: str,
        confidence: float,
        hypothesis_id: Optional[str] = None,
        iteration: int = 0,
        embedding: Optional[List[float]] = None
    ) -> str:
        """
        Add a new finding to the knowledge graph.

        Args:
            text: Finding content
            confidence: Confidence score (0.0-1.0)
            hypothesis_id: Related hypothesis ID (e.g., "h1")
            iteration: Iteration number when discovered
            embedding: Precomputed embedding (auto-computed if None)

        Returns:
            Finding ID
        """
        # Generate embedding if not provided
        if embedding is None and OPENAI_AVAILABLE:
            embedding = get_embedding(text)

        finding_id = f"finding_{len(self.data['nodes']) + 1:03d}"

        node = {
            "id": finding_id,
            "text": text,
            "confidence": confidence,
            "hypothesis_id": hypothesis_id,
            "iteration": iteration,
            "timestamp": datetime.now().isoformat(),
            "embedding": embedding
        }

        self.data["nodes"].append(node)
        self._save()

        return finding_id

    def detect_contradictions(self) -> List[Dict]:
        """
        Detect contradictions: high semantic similarity but different confidence.

        Returns:
            List of contradiction pairs with similarity scores
        """
        if not OPENAI_AVAILABLE:
            return []

        contradictions = []
        nodes = self.data["nodes"]

        for i, node1 in enumerate(nodes):
            if not node1.get("embedding"):
                continue

            for node2 in nodes[i+1:]:
                if not node2.get("embedding"):
                    continue

                # Calculate semantic similarity
                similarity = cosine_similarity(node1["embedding"], node2["embedding"])

                # High similarity + confidence difference = potential contradiction
                conf_diff = abs(node1["confidence"] - node2["confidence"])

                if similarity > CONTRADICTION_THRESHOLD and conf_diff > 0.2:
                    contradiction = {
                        "finding_1": {
                            "id": node1["id"],
                            "text": node1["text"][:100],
                            "confidence": node1["confidence"]
                        },
                        "finding_2": {
                            "id": node2["id"],
                            "text": node2["text"][:100],
                            "confidence": node2["confidence"]
                        },
                        "similarity": round(similarity, 3),
                        "confidence_diff": round(conf_diff, 3),
                        "detected_at": datetime.now().isoformat()
                    }
                    contradictions.append(contradiction)

        # Update stored contradictions
        self.data["contradictions"] = contradictions
        self._save()

        return contradictions

    def find_related(self, query: str, threshold: float = RELATION_THRESHOLD, top_k: int = 5) -> List[Dict]:
        """
        Find related findings for a query.

        Args:
            query: Query text
            threshold: Minimum similarity threshold
            top_k: Max number of results

        Returns:
            List of related findings sorted by similarity
        """
        if not OPENAI_AVAILABLE:
            return []

        query_emb = get_embedding(query)
        if query_emb is None:
            return []

        results = []
        for node in self.data["nodes"]:
            if not node.get("embedding"):
                continue

            similarity = cosine_similarity(query_emb, node["embedding"])

            if similarity > threshold:
                results.append({
                    "id": node["id"],
                    "text": node["text"],
                    "confidence": node["confidence"],
                    "similarity": round(similarity, 3)
                })

        # Sort by similarity descending
        results.sort(key=lambda x: x["similarity"], reverse=True)

        return results[:top_k]

    def get_statistics(self) -> Dict:
        """Get knowledge graph statistics."""
        nodes = self.data["nodes"]
        contradictions = self.data["contradictions"]

        # Confidence distribution
        high_conf = sum(1 for n in nodes if n.get("confidence", 0) >= 0.8)
        medium_conf = sum(1 for n in nodes if 0.5 <= n.get("confidence", 0) < 0.8)
        low_conf = sum(1 for n in nodes if n.get("confidence", 0) < 0.5)

        return {
            "total_findings": len(nodes),
            "total_contradictions": len(contradictions),
            "confidence_distribution": {
                "high (≥0.8)": high_conf,
                "medium (0.5-0.8)": medium_conf,
                "low (<0.5)": low_conf
            },
            "embeddings_available": sum(1 for n in nodes if n.get("embedding")),
            "last_updated": self.data.get("last_updated")
        }


def main():
    """CLI interface for testing."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python knowledge_tracker.py <command>")
        print("Commands:")
        print("  stats               - Show knowledge graph statistics")
        print("  contradictions      - Detect and display contradictions")
        print("  related <query>     - Find related findings")
        sys.exit(1)

    kt = KnowledgeTracker()
    command = sys.argv[1]

    if command == "stats":
        stats = kt.get_statistics()
        print("\n📊 Knowledge Graph Statistics")
        print("=" * 50)
        print(f"Total Findings: {stats['total_findings']}")
        print(f"Total Contradictions: {stats['total_contradictions']}")
        print(f"\nConfidence Distribution:")
        for level, count in stats['confidence_distribution'].items():
            print(f"  {level}: {count}")
        print(f"\nEmbeddings Available: {stats['embeddings_available']}/{stats['total_findings']}")
        print(f"Last Updated: {stats['last_updated']}")

    elif command == "contradictions":
        contradictions = kt.detect_contradictions()
        print(f"\n⚠️  Detected {len(contradictions)} Contradictions")
        print("=" * 50)
        for i, c in enumerate(contradictions, 1):
            print(f"\n{i}. Similarity: {c['similarity']}, Confidence Δ: {c['confidence_diff']}")
            print(f"   [{c['finding_1']['id']}] {c['finding_1']['text'][:60]}... (conf: {c['finding_1']['confidence']})")
            print(f"   [{c['finding_2']['id']}] {c['finding_2']['text'][:60]}... (conf: {c['finding_2']['confidence']})")

    elif command == "related" and len(sys.argv) >= 3:
        query = " ".join(sys.argv[2:])
        related = kt.find_related(query)
        print(f"\n🔗 Related Findings for: '{query}'")
        print("=" * 50)
        for r in related:
            print(f"[{r['id']}] Similarity: {r['similarity']}, Confidence: {r['confidence']}")
            print(f"  {r['text'][:100]}...")
            print()

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
