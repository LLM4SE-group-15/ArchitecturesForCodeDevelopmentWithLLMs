# Planner Story Points (Fibonacci) and Routing Policy

## Purpose

This document specifies how the **Planner** assigns story points from the set **{1, 2, 3, 5, 8}** to a task, and how the **Router** uses them to select the appropriate developer tier (**S/M/L**).

---

## Story Points: What They Mean

Story points are a **difficulty proxy** that captures:

- **Complexity** (algorithmic / architectural complexity)
- **Uncertainty** (ambiguity in requirements)
- **Edge-case density** (number of corner cases)
- **Verification effort** (how hard it is to validate with tests)

They are not time estimates — they are a routing signal.

### Allowed Values

| Value | Interpretation | Default Tier |
|------:|----------------|--------------|
| 1 | Trivial | S |
| 2 | Small | S |
| 3 | Medium | M |
| 5 | Challenging | M |
| 8 | Hard | L |

---

## Planner: Assignment Rules

### Step 1 — Evaluate the Task

The Planner evaluates these dimensions:

- **Algorithmic complexity**: simple vs non-trivial algorithm
- **Edge cases**: few vs many (empty inputs, boundaries)
- **External constraints**: performance, strict I/O format
- **Ambiguity**: requirements clear vs underspecified

### Step 2 — Map to Story Points

| Story Points | Criteria |
|-------------:|----------|
| 1 | Obvious implementation, minimal edge cases |
| 2 | Straightforward, a few edge cases |
| 3 | Requires careful handling, moderate edge cases |
| 5 | Non-trivial approach, multiple edge cases |
| 8 | Difficult algorithm, high uncertainty |

### Step 3 — Justify the Choice

For every task, the Planner provides a rationale explaining:
- Why this value fits
- Why the *closest lower* value is not sufficient

Example:
> **Story Points: 5**
> - Why 5: requires non-trivial algorithm + careful boundary handling
> - Why not 3: too many corner cases for a "standard" implementation

---

## State Representation

```python
class GraphState(TypedDict):
    plan: PlanOutput  # {id, description, story_points, rationale}
    
    story_points_initial: Literal[1, 2, 3, 5, 8]  # Before escalation
    story_points_current: Literal[1, 2, 3, 5, 8]  # Current (may increase)
    
    escalations: int
    developer_tier: Literal["S", "M", "L"]
```

---

## Router: Tier Selection

The Router reads `story_points_current` and selects the developer tier:

| Story Points | Developer Tier |
|-------------:|----------------|
| 1–2 | S (small/cheap) |
| 3–5 | M (standard) |
| 8 | L (large/strong) |

---

## Workflow (Architecture B/C)

All developer tiers follow the same flow:

```
Planner → Router → Developer (S/M/L) → Reviewer → Tester
                          ↑                         │
                          └────── (on FAIL) ────────┘
```

**Note**: All tiers (S, M, L) pass through the Reviewer. The only difference is the model used by the Developer node.

---

## Escalation Policy

When tests fail:

| Current Tier | Action |
|--------------|--------|
| S | Escalate to M, `escalations += 1` |
| M | Escalate to L, `escalations += 1` |
| L | End with `test_passed=False` |

The `story_points_current` is also updated:
- S → M: set to 3
- M → L: set to 8

---

## Architecture A (Single-Agent)

In Architecture A (single-agent baseline):
- No Planner, Router, or Reviewer
- Flow: `Single Agent → Tester → END`
- No escalation (single attempt)

---

## Implementation Notes

- In Architecture B, S/M/L map to the same model (Qwen-7B); routing is still logged for analysis
- In Architecture C, S/M/L map to different models with varying capabilities
- The Tester is always pure Python (subprocess), not an LLM
