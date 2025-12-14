# Planner Story Points (Fibonacci) and Routing Policy

## Purpose

This document specifies how the **Planner + Story Point Estimator** assigns Scrum-style story points from the Fibonacci-like set **{1, 2, 3, 5, 8}** to a task, how that information is stored in LangGraph state, and how the **Router** uses it to select the appropriate developer tier (**S/M/L**) and retry/loop strategy.

---

## Story points: what they mean here

Story points are used as a **coarse difficulty proxy** that captures:

- **Complexity** (algorithmic / architectural complexity)
- **Uncertainty** (ambiguity in requirements, multiple plausible interpretations)
- **Edge-case density** (number and difficulty of corner cases)
- **Integration risk** (how likely the task affects other parts of the solution)
- **Verification effort** (how hard it is to validate with tests)

They are not “time estimates”; they are a routing signal.

### Allowed values

Only these values are allowed:

- **1**: trivial
- **2**: small
- **3**: medium
- **5**: challenging
- **8**: hard

---

## Planner: assignment rules (Scrum-style)

### Step 1 — Assign story points to the task
For MBPP/HumanEval-style tasks, the Planner treats the problem as atomic and assigns a story point to the whole task.

### Step 2 — Score the task by heuristics
The Planner evaluates the following dimensions:

- **Algorithmic complexity**: simple control flow vs non-trivial algorithm/data structure
- **Edge cases**: none/few vs many (input validation, empty inputs, boundary conditions)
- **External constraints**: performance constraints, strict I/O format, tricky parsing
- **Coupling**: isolated vs strongly coupled to other parts of the solution
- **Ambiguity**: requirements clear vs underspecified

### Step 3 — Map heuristics to {1,2,3,5,8}
Use the simplest mapping that is consistent across tasks:

- **1**: “obvious implementation”, minimal edge cases, low coupling
- **2**: straightforward, a few edge cases, still low risk
- **3**: requires careful handling, moderate edge cases or moderate coupling
- **5**: non-trivial approach, multiple edge cases, noticeable integration risk
- **8**: difficult algorithm/design, high edge-case density, high uncertainty, or repeated failures in the loop

### Step 4 — Justify the choice (including a “why 5 and not 3” check)
For every task, the Planner writes a short rationale. To reduce noise and keep rationales comparable, the Planner must answer:

- Why this value (e.g., 5) fits.
- Why the *closest lower* value (e.g., 3) is not sufficient.

A minimal “self-check loop” can be:

1. Propose story points.
2. Ask: “Could this be one level lower?”
3. If “no”, state the blocking reasons (edge cases, uncertainty, integration risk).

#### Example rationale (“why 5 and not 3”)

Example unit: implement core logic for an algorithm with tricky boundaries.

- Proposed: **5**
- Why **5**: requires a non-trivial algorithmic choice + careful boundary handling + multiple failure modes.
- Why not **3**: the number of corner cases and correctness pitfalls is high enough that a “standard” implementation attempt is likely to miss cases without a stronger model/review.

---

## State representation (LangGraph)

The Planner stores story points and rationale directly into the workflow state.

Example state fragment (atomic problem):

```json
{
  "plan": {
    "id": "problem_0",
    "description": "Full atomic problem",
    "story_points": 5,
    "rationale": "Non-trivial algorithm + hidden edge cases"
  }
}
```

Recommended additional fields (optional but useful for analysis):

- `story_points_initial` (before any escalation)
- `story_points_current`
- `escalations` (count / history)
- `failure_history` (test failures / logs for the problem)

---

## Router: tier selection and loop policy

The Router reads the story points and chooses developer tier and control-flow strategy.

### Routing policy (base)

- If `story_points <= 2`:
  - Use **Developer-S** (small/cheap)
  - Run **one pass**: Developer → Tester (no dedicated reviewer by default)

- If `story_points in {3, 5}`:
  - Use **Developer-M** (standard)
  - Run **one extra review step**: Developer → Reviewer → Tester

- If `story_points >= 8`:
  - Use **Developer-L** (strong)
  - Run **two correction iterations**: Tester → Fix → Retest (up to 2 times)
  - Optionally enable a **dedicated Reviewer** with a different model

### Escalation on failures

If tests fail, the Router can revise the decision by:

- Increasing `story_points_current` (e.g., 3 → 5 → 8)
- Escalating developer tier **S → M → L**

Escalation triggers should be explicit and logged, for example:

- First fail with S: escalate to M
- Repeated fail with M: escalate to L
- If already L: stay on L and continue within the configured retry budget

---

## Implementation notes (to keep experiments comparable)

- In Architecture B (single-model multi-agent), S/M/L are logically distinct but can map to the same underlying model; the routing decision is still logged.
- In Architecture C (hybrid), Planner/Reviewer are typically a generalist model, while S/M/L are code models; the routing decision affects both cost and quality.
- The Tester is not an LLM: it runs Python tests and returns logs to drive correction.
