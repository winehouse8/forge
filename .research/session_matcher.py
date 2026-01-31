#!/usr/bin/env python3
"""
Session Matcher: LLM-based similarity detection
Uses Claude itself to judge question similarity - no embeddings needed!

Principle: "Why use embeddings when you have Claude?"
"""

from typing import List, Dict, Optional


def format_sessions_for_comparison(sessions: List[Dict]) -> str:
    """
    Format existing sessions for Claude to review.

    Args:
        sessions: List of session metadata

    Returns:
        Formatted text listing all sessions
    """
    if not sessions:
        return "No existing sessions."

    lines = []
    for i, session in enumerate(sessions, 1):
        question = session.get("question", "Unknown")
        iteration = session.get("iteration", 0)
        status = session.get("status", "unknown")

        lines.append(f"{i}. \"{question}\"")
        lines.append(f"   ({iteration} iterations, {status})")

    return "\n".join(lines)


def create_similarity_prompt(new_question: str, sessions: List[Dict]) -> str:
    """
    Create prompt for Claude to judge similarity.

    Args:
        new_question: User's new research question
        sessions: List of existing session metadata

    Returns:
        Formatted prompt for Claude
    """
    sessions_text = format_sessions_for_comparison(sessions)

    prompt = f"""기존 연구 세션 목록:

{sessions_text}

새로운 질문: "{new_question}"

이 새 질문과 **의미적으로 유사한** 기존 세션이 있는지 판단해주세요.

판단 기준:
- 같은 주제/도메인을 다루는가?
- 같은 질문에 답하려는 것인가?
- 연구 목적이 겹치는가?

응답 형식 (JSON):
{{
  "match_type": "exact" | "similar" | "none",
  "matched_sessions": [1, 2, ...],  // 세션 번호 (유사한 순서)
  "reasoning": "판단 근거 설명"
}}

예시:
- "양자 컴퓨팅 최신 동향" vs "양자 컴퓨터 동향" → "exact" (거의 동일한 질문)
- "양자 컴퓨팅 최신 동향" vs "양자역학 기초" → "similar" (관련 있지만 다른 각도)
- "양자 컴퓨팅" vs "LangGraph 성능" → "none" (완전히 다른 주제)

JSON 응답:"""

    return prompt


def parse_claude_response(response: str) -> Dict:
    """
    Parse Claude's similarity judgment.

    Args:
        response: Claude's JSON response

    Returns:
        Parsed judgment dict
    """
    import json
    import re

    # Extract JSON from response (handle markdown code blocks)
    json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
    if json_match:
        json_text = json_match.group(1)
    else:
        # Try to find raw JSON
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            json_text = json_match.group(0)
        else:
            # No JSON found, return default
            return {
                "match_type": "none",
                "matched_sessions": [],
                "reasoning": "Could not parse response"
            }

    try:
        return json.loads(json_text)
    except json.JSONDecodeError:
        return {
            "match_type": "none",
            "matched_sessions": [],
            "reasoning": "JSON parse error"
        }


def find_similar_sessions_llm(
    new_question: str,
    sessions: List[Dict]
) -> tuple[List[Dict], str]:
    """
    Find similar sessions using Claude's judgment (no embeddings!).

    This function creates a prompt that will be shown to Claude.
    Claude itself will judge similarity based on semantic understanding.

    Args:
        new_question: User's new research question
        sessions: List of existing session metadata

    Returns:
        (matched_sessions, match_type)
        - matched_sessions: Sessions Claude judged as similar
        - match_type: "exact", "similar", or "none"

    Note:
        This function returns a PROMPT. The actual judgment happens
        when this prompt is sent to Claude in SKILL.md.
    """
    if not sessions:
        return [], "none"

    # This is just a prompt generator
    # Actual Claude invocation happens in SKILL.md
    prompt = create_similarity_prompt(new_question, sessions)

    return prompt, sessions


def main():
    """CLI test (simulation)."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python session_matcher.py <new_question>")
        sys.exit(1)

    new_question = " ".join(sys.argv[1:])

    # Mock sessions
    sessions = [
        {
            "id": "research_20260201_143022_quantum",
            "question": "양자 컴퓨팅 최신 동향",
            "iteration": 10,
            "status": "paused"
        },
        {
            "id": "research_20260201_150512_langgraph",
            "question": "LangGraph 성능 비교",
            "iteration": 5,
            "status": "running"
        }
    ]

    prompt = create_similarity_prompt(new_question, sessions)

    print("\n" + "="*60)
    print("Prompt for Claude:")
    print("="*60)
    print(prompt)
    print("="*60)
    print("\n[This prompt will be sent to Claude for judgment]")


if __name__ == "__main__":
    main()
