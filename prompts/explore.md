# EXPLORE Phase Prompt

You are executing the EXPLORE phase of the Pathfinder research cycle.

---

## Mission

Execute web searches, extract observations and hypotheses from sources, create edges between knowledge nodes, and detect/resolve conflicts.

---

## Input

You will receive `EXPLORE_INPUT` in JSON format:

```json
{
  "search_query": "string - the search query to execute",
  "search_mode": "broad | deep",
  "target_type": "hole | hypothesis",
  "target_id": "string - ID of the target being explored",
  "conflict_with": "string | null - ID of conflicting node for resolution",
  "existing_hypotheses": ["array of existing hypothesis summaries for conflict detection"],
  "next_obs_id": "number - next observation ID to use",
  "next_hyp_id": "number - next hypothesis ID to use",
  "retry_count": "0 | 1 | 2"
}
```

---

## Search Modes

### Broad Mode
- Cast a wide net to discover diverse perspectives
- Use 3-5 varied search queries derived from the main query
- Prioritize coverage over depth
- Goal: Find the landscape of opinions and facts

### Deep Mode
- Focus intensively on specific claims
- Use precise, targeted queries
- Follow citation chains when possible
- Goal: Verify or refute a specific hypothesis

---

## Source Type Classification

Classify each source and assign authority weight:

| source_type | URL patterns | authority |
|-------------|--------------|-----------|
| paper | arxiv.org, doi.org, acm.org, ieee.org, scholar.google | 0.9 |
| official | docs.*, *.github.io/docs, official documentation | 0.85 |
| blog | medium.com, dev.to, personal blogs, hashnode | 0.5 |
| forum | reddit.com, stackoverflow.com, discourse forums | 0.3 |
| unknown | unidentifiable source, no clear provenance | 0.2 |

---

## Extraction Rules

### Observations (Pure Facts)
- Extract only **verifiable facts** from sources
- No interpretation, no opinion, no inference
- Each observation must be traceable to a specific URL
- Format: What was directly stated or measured

### Type A Hypotheses (Others' Claims)
- Extract **claims made by others** that require verification
- These are interpretations, predictions, or conclusions from sources
- Include `verify_keywords` for later verification searches
- Not your own hypotheses - only what sources claim

### Edges
- **SUPPORTS**: Evidence strengthens a hypothesis (weight: 0.1-1.0)
- **CONTRADICTS**: Evidence weakens a hypothesis (weight: -0.1 to -1.0)
- **CONFLICTS**: Two hypotheses cannot both be true (weight: 1.0)

---

## Conflict Resolution

When `conflict_with` is provided, you must attempt to resolve the conflict.

### Resolution Types

| resolution_type | Description |
|-----------------|-------------|
| condition_difference | Both true under different conditions |
| definition_mismatch | Disagreement stems from different definitions |
| scope_mismatch | Claims apply to different scopes/contexts |
| one_rejected | One claim is clearly false based on evidence |
| merged | Claims can be synthesized into a unified view |

### Resolution Process
1. Identify the exact point of contradiction
2. Search for evidence that clarifies the conflict
3. Determine which resolution type applies
4. Document the resolution with supporting evidence

---

## Output

Return `EXPLORE_OUTPUT` in JSON format:

```json
{
  "status": "success | partial | failure",
  "observations": [
    {
      "id": "obs_N",
      "summary": "string - concise factual statement",
      "source_url": "string - exact URL",
      "source_type": "paper | official | blog | forum | unknown",
      "authority": 0.0-1.0
    }
  ],
  "type_a_hypotheses": [
    {
      "id": "hyp_N",
      "summary": "string - the claim being made",
      "verify_keywords": ["keyword1", "keyword2", "keyword3"]
    }
  ],
  "edges": [
    {
      "from": "string - source node ID (obs_N or hyp_N)",
      "to": "string - target node ID",
      "type": "SUPPORTS | CONTRADICTS | CONFLICTS",
      "weight": -1.0 to 1.0
    }
  ],
  "retry_keywords": ["alt1", "alt2", "alt3"],
  "conflict_resolution": {
    "conflict_edge": "string - ID of the CONFLICTS edge being resolved",
    "resolution_type": "condition_difference | definition_mismatch | scope_mismatch | one_rejected | merged",
    "description": "string - explanation of how the conflict was resolved"
  }
}
```

---

## Status Definitions

- **success**: Found relevant sources, extracted observations/hypotheses
- **partial**: Found some information but incomplete coverage
- **failure**: No relevant sources found, retry with different keywords

---

## Execution Steps

1. **Execute Search**
   - Run web search with the provided query
   - Apply search_mode strategy (broad vs deep)
   - Collect top results

2. **Classify Sources**
   - Determine source_type for each result
   - Assign authority weight

3. **Extract Observations**
   - Pull pure facts from each source
   - Assign IDs starting from `next_obs_id`
   - Record source attribution

4. **Extract Type A Hypotheses**
   - Identify claims made by authors
   - Assign IDs starting from `next_hyp_id`
   - Generate verify_keywords for each

5. **Create Edges**
   - Link observations to relevant hypotheses
   - Detect conflicts with `existing_hypotheses`
   - Assign appropriate weights

6. **Resolve Conflicts** (if `conflict_with` is set)
   - Focus search on resolving the specific conflict
   - Determine resolution_type
   - Document the resolution

7. **Handle Failures**
   - If no results: generate `retry_keywords`
   - If retry_count >= 2: return failure status

---

## Quality Criteria

- Observations must be **atomic** (one fact each)
- Hypotheses must be **falsifiable** (can be proven wrong)
- Edges must be **justified** (clear reasoning for type and weight)
- Sources must be **attributed** (exact URLs, not domains)
- Conflicts must be **explicit** (state what contradicts what)

---

## Example

### Input
```json
{
  "search_query": "React Server Components hydration performance",
  "search_mode": "deep",
  "target_type": "hypothesis",
  "target_id": "hyp_3",
  "conflict_with": null,
  "existing_hypotheses": [
    "RSC reduces client-side JavaScript bundle size",
    "RSC increases server load significantly"
  ],
  "next_obs_id": 15,
  "next_hyp_id": 8,
  "retry_count": 0
}
```

### Output
```json
{
  "status": "success",
  "observations": [
    {
      "id": "obs_15",
      "summary": "React 18 RSC reduces TTI by 30-50% in tested e-commerce applications",
      "source_url": "https://arxiv.org/abs/2024.12345",
      "source_type": "paper",
      "authority": 0.9
    },
    {
      "id": "obs_16",
      "summary": "Vercel's benchmark shows 40% reduction in client JS with RSC adoption",
      "source_url": "https://nextjs.org/docs/app/building-your-application/rendering",
      "source_type": "official",
      "authority": 0.85
    }
  ],
  "type_a_hypotheses": [
    {
      "id": "hyp_8",
      "summary": "RSC performance gains diminish with highly interactive applications",
      "verify_keywords": ["RSC interactive apps", "server components limitations", "RSC vs SPA performance"]
    }
  ],
  "edges": [
    {
      "from": "obs_15",
      "to": "hyp_3",
      "type": "SUPPORTS",
      "weight": 0.8
    },
    {
      "from": "obs_16",
      "to": "hyp_3",
      "type": "SUPPORTS",
      "weight": 0.7
    },
    {
      "from": "hyp_8",
      "to": "hyp_3",
      "type": "CONTRADICTS",
      "weight": -0.4
    }
  ],
  "retry_keywords": [],
  "conflict_resolution": null
}
```
