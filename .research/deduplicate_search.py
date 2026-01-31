#!/usr/bin/env python3
"""
Search Deduplication: Embedding-based semantic duplicate detection
Based on Research Report recommendations (SemDeDup, GPTrace)

Usage:
    from deduplicate_search import is_duplicate_query, add_query_to_history

    is_dup, similar = is_duplicate_query("new query text")
    if is_dup:
        print(f"Skip: similar to '{similar}'")
    else:
        # Execute search
        add_query_to_history("new query text", results_count=10)
"""

import json
import os
import sys
from datetime import datetime
from typing import Tuple, Optional

# Try to import OpenAI, fallback gracefully
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️  Warning: OpenAI not installed. Install with: pip install openai", file=sys.stderr)

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("⚠️  Warning: NumPy not installed. Install with: pip install numpy", file=sys.stderr)


HISTORY_FILE = ".research/search_history.json"
DUPLICATE_THRESHOLD = 0.95  # SemDeDup recommendation
CLUSTER_THRESHOLD = 0.75
EMBEDDING_MODEL = "text-embedding-3-small"  # Fast, cheap


def load_history():
    """Load search history from JSON file."""
    try:
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"queries": []}


def save_history(history):
    """Save search history to JSON file."""
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)


def get_embedding(text: str) -> Optional[list]:
    """
    Get embedding for text using OpenAI API.
    Returns None if OpenAI is not available.
    """
    if not OPENAI_AVAILABLE:
        return None

    try:
        client = OpenAI()  # Uses OPENAI_API_KEY env var
        response = client.embeddings.create(
            input=text,
            model=EMBEDDING_MODEL
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"⚠️  Embedding error: {e}", file=sys.stderr)
        return None


def cosine_similarity(a: list, b: list) -> float:
    """Calculate cosine similarity between two vectors."""
    if not NUMPY_AVAILABLE:
        # Fallback: simple dot product implementation
        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x ** 2 for x in a) ** 0.5
        norm_b = sum(x ** 2 for x in b) ** 0.5
        return dot_product / (norm_a * norm_b) if norm_a and norm_b else 0.0

    a_arr = np.array(a)
    b_arr = np.array(b)
    return np.dot(a_arr, b_arr) / (np.linalg.norm(a_arr) * np.linalg.norm(b_arr))


def is_duplicate_query(
    new_query: str,
    threshold: float = DUPLICATE_THRESHOLD
) -> Tuple[bool, Optional[str]]:
    """
    Check if new query is semantically duplicate of previous searches.

    Args:
        new_query: Query text to check
        threshold: Similarity threshold (default: 0.95 per SemDeDup)

    Returns:
        (is_duplicate, similar_query_text)
    """
    if not OPENAI_AVAILABLE or not NUMPY_AVAILABLE:
        # Fallback: simple string matching
        history = load_history()
        for query in history.get("queries", []):
            if new_query.lower() == query.get("text", "").lower():
                return True, query.get("text")
        return False, None

    history = load_history()
    queries = history.get("queries", [])

    if not queries:
        return False, None

    # Get embedding for new query
    new_emb = get_embedding(new_query)
    if new_emb is None:
        return False, None

    # Check similarity with all past queries
    for past_query in queries:
        # Add embedding if missing (lazy computation)
        if 'embedding' not in past_query:
            past_query['embedding'] = get_embedding(past_query.get('text', ''))
            save_history(history)  # Save updated history

        if past_query.get('embedding') is None:
            continue

        similarity = cosine_similarity(new_emb, past_query['embedding'])

        # SemDeDup thresholds
        if similarity > threshold:
            return True, past_query.get('text')
        elif similarity > CLUSTER_THRESHOLD:
            print(f"ℹ️  Cluster similarity ({similarity:.2f}): '{past_query.get('text')[:50]}...'", file=sys.stderr)

    return False, None


def add_query_to_history(
    query_text: str,
    iteration: int = 0,
    results_count: int = 0,
    success: bool = True
):
    """
    Add query to search history with embedding.

    Args:
        query_text: The search query
        iteration: Current iteration number
        results_count: Number of results returned
        success: Whether search succeeded
    """
    history = load_history()

    # Get embedding
    embedding = get_embedding(query_text) if OPENAI_AVAILABLE else None

    query_entry = {
        "text": query_text,
        "timestamp": datetime.now().isoformat(),
        "iteration": iteration,
        "results_count": results_count,
        "success": success
    }

    if embedding is not None:
        query_entry["embedding"] = embedding

    history["queries"].append(query_entry)
    save_history(history)


def main():
    """CLI interface for testing."""
    if len(sys.argv) < 2:
        print("Usage: python deduplicate_search.py <query>")
        sys.exit(1)

    query = " ".join(sys.argv[1:])

    print(f"Checking: '{query}'")
    is_dup, similar = is_duplicate_query(query)

    if is_dup:
        print(f"✗ DUPLICATE (>0.95 similarity)")
        print(f"  Similar to: '{similar}'")
        sys.exit(1)
    else:
        print(f"✓ NEW QUERY")
        add_query_to_history(query, iteration=0, results_count=0, success=True)
        print(f"  Added to history")
        sys.exit(0)


if __name__ == "__main__":
    main()
