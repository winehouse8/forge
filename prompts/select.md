# SELECT

## 입력 (SELECT_INPUT)
- question: "{question}"
- iteration: {iteration}
- health_issues: {health_issues}
- conflicts: {active_conflicts}  # resolved=false만
- unvisited_type_b: {list}
- unvisited_type_a: {list}
- tested_uncertain: {list}
- unexplored_unused: {list}
- lens_index: {number}
- hypotheses_summary: {hyp_id: summary}

## 우선순위
1. conflicts 있으면 → 충돌 해결
2. unvisited_type_b 있으면 → Type B 검증
3. unvisited_type_a 있으면 → Type A 검증
4. tested_uncertain 있으면 → 애매한 것 확정
5. unexplored_unused 있으면 → 키워드 탐색
6. 위 모두 없으면 → 6렌즈 발산

## health_issues 대응
- "STALEMATE" → conflicts 강제 선택
- "LOW_QUALITY" → 검색어에 "research paper" 추가
- "ALL_WEAK" → 새 관점 탐색 (6렌즈 또는 unexplored)

## 6렌즈
lens = ["definition", "scope", "comparison", "cases", "limitations", "application"]
current = lens[lens_index % 6]

## 출력 (SELECT_OUTPUT)
```json
{
  "target_type": "hypothesis" | "unexplored" | "6lens",
  "target_id": "hyp_A1" | "keyword" | null,
  "conflict_with": "hyp_B1" | null,
  "search_query": "검색어",
  "search_mode": "broad" | "deep",
  "reason": "선택 이유"
}
```

**conflict_with 규칙:**
- conflicts에서 선택 시: 상대방 가설 ID
- 그 외: null

**검색 모드:**
- Early Stage (가설 < 5개) → broad
- Late Stage (가설 >= 5개) → deep
