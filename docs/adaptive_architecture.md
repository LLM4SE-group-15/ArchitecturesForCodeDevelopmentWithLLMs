# Adaptive Multi-Agent System (AMAS) — Updated Architecture

## Overview

AMAS is a multi-role LangGraph pipeline where **adaptivity is driven by model
selection**, not by changing the number of developer agents.

The Planner estimates difficulty using **story points (1–2–3–5–8)** and the
Router selects an appropriate developer tier (**S/M/L**). For atomic problems
the Planner assigns a story point to the whole problem. When tests fail, the
system can **escalate** the difficulty estimate and reroute the task to a
stronger developer.

---

## Architecture Diagram

```
┌───────────────────────────────────────────────────────────────┐
│                           INPUT TASK                          │
└────────────┬──────────────────────────────────────────────────┘
             │
             ▼
┌───────────────────────────────────────────────────────────────┐
│                           PLANNER                             │
│  - assign story points (1–2–3–5–8) to the whole problem + motivation               │
└────────────┬──────────────────────────────────────────────────┘
             │
             ▼
┌───────────────────────────────────────────────────────────────┐
│                            ROUTER                             │
│  Select developer tier using story points + failure history:  │
│    1–2 → Developer-S                                          │
│    3–5 → Developer-M                                          │
│    8+  → Developer-L                                          │
│  On repeated FAIL: escalate (S→M→L)                           │
└───┬───────────────────────┬──────────────────────┬────────────┘
    │                       │                      │  
    ▼                       ▼                      ▼  
  ┌────────────────┐     ┌────────────────┐    ┌───────────┐     
  │  DEVELOPER-S   │     │  DEVELOPER-M   │    │DEVELOPER-L│    
  │  (cheap/small) │     │  (standard)    │    │ (strong)  │    
  └───────┬────────┘     └──┬─────────────┘    └───┬───────┘    
          │                 │                      │   
          └─────────────────┬──────────────────────┘
                            ▼
┌───────────────────────────────────────────────────────────────┐
│                           REVIEWER                            │
│  Bugs, edge cases, style, maintainability → feedback          │
└────────────┬──────────────────────────────────────────────────┘
             ▼
┌───────────────────────────────────────────────────────────────┐
│                       TESTER (NON-LLM)                        │
│  Run Python tests → collect logs                              │
└────────────┬──────────────────────────────────────────────────┘
             │
      ┌──────▼──────────┐
      │     PASS ?      │
      └─┬─────────┬─────┘
        │YES      │NO
        ▼         ▼
         FINAL CODE   LOOP:
         - propagate test errors
         - optionally raise story points
         - reroute to stronger developer
```

---

## Detailed Workflow State

### State 1: Planning (Story Points)
```
Input: Task Description
Output: {
  "plan": {
    "id": "problem_0",
    "description": "Full atomic problem",
    "story_points": 5,
    "rationale": "Non-trivial logic + hidden edge cases"
  },
  "strategy": "route_by_story_points"
}
```

### State 2: Routing (Developer Tier Selection)
```
# Atomic problem: read story points from the plan
sp = plan.story_points

IF sp in {1,2}:
  developer = "S"
ELIF sp in {3,5}:
  developer = "M"
ELSE:
  developer = "L"

IF tests_fail_repeatedly:
  escalate developer S→M→L (and optionally increase plan.story_points)
```

### State 3: Implementation

Developer-(S/M/L) generates or fixes a single code snippet for the whole
problem, guided by the Planner rationale and any test feedback.

### State 4: Quality Assurance
```
Developer output → Reviewer → Tester → PASS or RETRY
```

---

## Models Used in the Hybrid Setup (Architecture C)


- Planner + Reviewer: **meta-llama/Llama-3.1-8B-Instruct**
- Developer-S (easy problems, first attempt): **Qwen/Qwen2.5-Coder-1.5B-Instruct** (or 3B)
- Developer-M (standard): **Qwen/Qwen2.5-Coder-7B-Instruct**
- Developer-L (hard / after repeated failures): **deepseek-ai/DeepSeek-Coder-V2-Instruct**

Tester is always a Python test runner (not an LLM).

---

## Agent Roles & Responsibilities

| Agent | Role | Input | Output |
|------|------|-------|--------|
| **Planner** | Story-point estimator (whole problem) | Task description | `plan` with `story_points` + rationale |
| **Router** | Tier selection + escalation | Plan + story_points + failure history | Developer tier (S/M/L) |
| **Developer-S/M/L** | Implementation / correction | Plan + constraints + feedback | Single code snippet |
| **Reviewer** | Review + refactor feedback | Developer snippet | Reviewed code + feedback |
| **Tester (non-LLM)** | Validation | Code + tests | PASS/FAIL + logs |

---

## Story Points (Difficulty Proxy)

The Planner assigns story points from the Fibonacci-like set **{1,2,3,5,8}**.

| Story points | Interpretation | Default routing |
|------------:|----------------|----------------|
| 1–2 | straightforward | Developer-S |
| 3–5 | moderate | Developer-M |
| 8 | difficult / many edge cases / non-trivial algorithm | Developer-L |

Escalation policy (used in the loop):
- If tests fail after using S, reroute to M.
- If tests keep failing with M, reroute to L.
- Optionally increase story points to reflect revised difficulty.

---

## Correction Loop (Test-driven)

When the Tester reports failures, the system loops with:
- the failing test output and stack traces,
- the Reviewer feedback,
- and an optional escalation decision (S→M→L).

---

### Example Execution Flow (atomic tasks)

### Task: "Implement a function to find prime numbers up to N"

**Step 1: Planning**
```
Planner:
├─ Plan for problem: story_points: 5, rationale: "needs careful handling and edge cases"
```

**Step 2: Routing**
```
Problem (5) → Developer-M
```

**Step 3: Implementation**
```
Developer-M produces a single solution snippet for the problem
```

**Step 4: QA + Loop**
```
Reviewer checks edge cases and maintainability
Tester runs tests
If FAIL with M: escalate to L and retry
```

---

## Key Advantages

1. **Cost-aware**: cheap models for easy tasks/problems, strong models only when needed
2. **Test-driven adaptivity**: failures trigger escalation and targeted fixes
3. **Clear comparisons**: A vs B isolates architecture; B vs C isolates specialization

---

## Evaluation Metrics

### Standard Metrics
- Functional correctness
- Code quality (complexity, maintainability)
- Token usage
- Execution time

### Adaptive-Specific Metrics
- **Routing distribution**: how often S/M/L is selected
- **Escalation counts**: S→M and M→L transitions
- **Retries per task**: number of correction loops until PASS
- **Story point drift**: how story points change after failures

---

## Research Questions Supported

AMAS supports the experimental comparisons described in [docs/architecture.md](architecture.md):

- **RQ1 (A vs B)**: effect of a multi-role pipeline at fixed model.
- **RQ2 (B vs C)**: effect of specialized models per role.
- **RQ3 (within C)**: routing S/M/L vs always using the strongest developer.

---

## Implementation with LangGraph (Sketch)

```python
from langgraph.graph import StateGraph, END

# Define state
class AdaptiveState(TypedDict):
  task: str
  plan: dict  # contains story_points and rationale
  failure_history: dict
  result: dict
  reviewed_code: str
  test_results: dict
  iterations: int

# Build graph (single-snippet workflow)
workflow = StateGraph(AdaptiveState)

# Add nodes
workflow.add_node("planner", planner_node)
workflow.add_node("router", router_node)
workflow.add_node("dev_s", developer_s_node)
workflow.add_node("dev_m", developer_m_node)
workflow.add_node("dev_l", developer_l_node)
workflow.add_node("reviewer", reviewer_node)
workflow.add_node("tester", tester_node)

# Add conditional edges
workflow.add_edge("planner", "router")
workflow.add_conditional_edges(
  "router",
  route_by_story_points,
  {
    "S": "dev_s",
    "M": "dev_m",
    "L": "dev_l",
  }
)

# After developer produces snippet, go to reviewer then tester
workflow.add_edge("dev_s", "reviewer")
workflow.add_edge("dev_m", "reviewer")
workflow.add_edge("dev_l", "reviewer")
workflow.add_edge("reviewer", "tester")
workflow.add_conditional_edges(
  "tester",
  should_retry,
  {
    "pass": END,
    "retry": "router"
  }
)

# Compile
app = workflow.compile()
```

---

## Next Steps

1. Implement Planner story-point estimation + rationale logging
2. Implement Router routing + escalation policy (S→M→L)
3. Implement Developer-S/M/L prompts and backends
4. Ensure Tester captures and propagates failing logs cleanly
5. Log routing, escalation, retries, and token/time costs for analysis
