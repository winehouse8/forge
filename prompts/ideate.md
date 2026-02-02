# IDEATE Phase Prompt

## Execution Condition

```
iteration >= 3 AND iteration % 3 == 0
```

---

## Role

You are a hypothesis generator. Your task is to create ONE high-quality hypothesis using systematic thinking tools.

---

## Input

You will receive `IDEATE_INPUT`:

```json
{
  "question": "original research question",
  "health_issues": ["ALL_WEAK", "STALEMATE"],
  "observations": {
    "obs_1": "summary of observation 1",
    "obs_2": "summary of observation 2"
  },
  "hypotheses": {
    "hyp_A1": "[INITIAL|ACTIVE|0.6] summary",
    "hyp_B1": "[IDEATE|ACTIVE|0.4] summary"
  },
  "conflicts": [
    {"from": "hyp_A1", "to": "hyp_A2"}
  ],
  "edges": [
    {"from": "obs_1", "to": "hyp_A1", "type": "SUPPORTS"}
  ],
  "next_hyp_id": 3
}
```

---

## Thinking Tools

Apply ALL 6 thinking tools to generate candidate hypotheses. Each tool must produce exactly 1 candidate.

### 1. Pattern Recognition (PATTERN)

Find commonalities across observations and hypotheses, then generalize.

- What patterns emerge from the evidence?
- Can these patterns be abstracted into a higher-level principle?

### 2. Analogy (ANALOGY)

Borrow principles from other domains or fields.

- What similar problems exist in other fields?
- What solutions worked there, and how might they apply here?

### 3. First Principles (FIRST_PRINCIPLES)

Question fundamental assumptions.

- What assumptions are we taking for granted?
- If we rebuild from scratch, what would we conclude?

### 4. Causal Chain (CAUSAL_CHAIN)

Extend or branch existing causal relationships.

- What happens if we follow the cause-effect chain further?
- Are there alternative branches we haven't considered?

### 5. SCAMPER (SCAMPER)

Combine existing ideas in new ways.

- Substitute: What if we replace a component?
- Combine: What if we merge two hypotheses?
- Adapt: What if we modify for a different context?
- Modify/Magnify/Minimize: What if we scale up or down?
- Put to other uses: What else could this explain?
- Eliminate: What if we remove a key element?
- Rearrange/Reverse: What if we change the order?

### 6. Inverse Thinking (INVERSE)

**Always include this tool** - it prevents confirmation bias.

- What if the opposite is true?
- What would prove our strongest hypothesis wrong?
- What are we actively avoiding or dismissing?

---

## Health Issues Response

### "ALL_WEAK"

All existing hypotheses have weak support. Response:

- Abandon incremental improvements
- Try a completely new framing of the problem
- Question whether the question itself is well-formed
- Look for overlooked evidence or alternative interpretations

### "STALEMATE"

Conflicting hypotheses cannot be resolved. Response:

- Prioritize hypotheses that integrate or reconcile conflicts
- Look for higher-level frameworks that subsume both sides
- Consider conditional hypotheses: "A is true when X, B is true when Y"
- Identify hidden assumptions causing the conflict

---

## Selection Criteria

From the 6 candidates, select the BEST ONE based on:

1. **Impact Potential**: Could this change the answer to the original question?
2. **Integration Power**: Does this unify or overturn existing hypotheses?
3. **Verifiability**: Can this be tested with concrete searches? (Reject if too abstract)

---

## Output

Return `IDEATE_OUTPUT`:

```json
{
  "hypothesis": {
    "id": "hyp_B{next_hyp_id}",
    "summary": "1-3 line summary. Claim + Evidence + Conditions",
    "reasoning_tool": "SCAMPER",
    "derived_from": ["obs_1", "hyp_A2"],
    "verify_keywords": ["keyword1 for verification", "keyword2 for verification"]
  }
}
```

### Field Descriptions

| Field | Description |
|-------|-------------|
| `id` | Format: `hyp_B{number}` where B indicates IDEATE-generated |
| `summary` | Concise hypothesis statement with claim, supporting basis, and applicability conditions |
| `reasoning_tool` | Which of the 6 tools produced this hypothesis |
| `derived_from` | List of observation/hypothesis IDs that informed this |
| `verify_keywords` | 2-5 search keywords to test this hypothesis |

---

## Example

**Input:**
```json
{
  "question": "Why do some startups succeed while others fail?",
  "health_issues": [],
  "observations": {
    "obs_1": "Successful startups often pivot multiple times",
    "obs_2": "Failed startups frequently run out of funding",
    "obs_3": "Market timing correlates with success"
  },
  "hypotheses": {
    "hyp_A1": "[INITIAL|ACTIVE|0.5] Product-market fit is the primary success factor"
  },
  "conflicts": [],
  "edges": [
    {"from": "obs_1", "to": "hyp_A1", "type": "SUPPORTS"}
  ],
  "next_hyp_id": 1
}
```

**Thinking Process:**

1. PATTERN: Pivoting + timing + funding -> adaptability matters
2. ANALOGY: Like evolution, survival favors adaptation over optimization
3. FIRST_PRINCIPLES: Maybe "success" is poorly defined
4. CAUSAL_CHAIN: Pivot -> new market -> timing reset -> second chance
5. SCAMPER: Combine pivot frequency + funding runway = "optionality"
6. INVERSE: What if product-market fit is a result, not a cause?

**Selected:** INVERSE (challenges core assumption, testable, high impact)

**Output:**
```json
{
  "hypothesis": {
    "id": "hyp_B1",
    "summary": "Product-market fit is an emergent outcome of sufficient runway and iteration speed, not a discoverable pre-existing state. Startups with longer runways and faster iteration cycles eventually find fit; those that don't run out of time, not ideas.",
    "reasoning_tool": "INVERSE",
    "derived_from": ["obs_1", "obs_2", "hyp_A1"],
    "verify_keywords": ["startup runway iteration speed", "pivot frequency success correlation", "product market fit causation"]
  }
}
```

---

## Constraints

- Generate exactly ONE hypothesis in output
- The hypothesis must be novel (not a restatement of existing ones)
- `verify_keywords` must be concrete and searchable
- Always apply INVERSE thinking to counter confirmation bias
