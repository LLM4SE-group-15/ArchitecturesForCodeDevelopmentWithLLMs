# Adaptive Multi-Agent System (AMAS)

## Overview

AMAS is a multi-role LangGraph pipeline where **adaptivity is driven by model
selection**, not by changing the number of developer agents.

The Planner estimates difficulty using **story points (1–2–3–5–8)** and the
Router selects an appropriate developer tier (**S/M/L**). When tests fail, the
system can **escalate** the difficulty estimate and reroute to a stronger
developer.

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
│  Assign story points (1–2–3–5–8) + rationale                  │
└────────────┬──────────────────────────────────────────────────┘
             │
             ▼
┌───────────────────────────────────────────────────────────────┐
│                            ROUTER                             │
│  Select developer tier using story points:                    │
│    1–2 → Developer-S                                          │
│    3–5 → Developer-M                                          │
│    8   → Developer-L                                          │
│  On repeated FAIL: escalate (S→M→L)                           │
└────────────┬──────────────────────────────────────────────────┘
             │
             ▼
┌───────────────────────────────────────────────────────────────┐
│                          DEVELOPER                            │
│  Generates code using tier-appropriate model (S/M/L)          │
└────────────┬──────────────────────────────────────────────────┘
             │
             ▼
┌───────────────────────────────────────────────────────────────┐
│                           REVIEWER                            │
│  Bugs, edge cases, style → feedback + improved code           │
└────────────┬──────────────────────────────────────────────────┘
             │
             ▼
┌───────────────────────────────────────────────────────────────┐
│                       TESTER (NON-LLM)                        │
│  Execute code with stdin, compare stdout                      │
└────────────┬──────────────────────────────────────────────────┘
             │
      ┌──────▼──────────┐
      │     PASS ?      │
      └─┬─────────┬─────┘
        │YES      │NO
        ▼         ▼
    FINAL CODE   LOOP:
                 - Add errors to failure_history
                 - Escalate tier if S or M
                 - Return to ROUTER
```

---

## LangGraph Implementation

The current implementation uses a single `developer` node that internally
selects the model based on the `developer_tier` field in state.

```python
from langgraph.graph import StateGraph, START, END

# Build graph for Architecture B/C
graph = StateGraph(GraphState)

graph.add_node("planner", planner_node)
graph.add_node("router", router_node)
graph.add_node("developer", developer_node)  # Selects S/M/L model internally
graph.add_node("reviewer", reviewer_node)
graph.add_node("tester", tester_node)

# Flow
graph.add_edge(START, "planner")
graph.add_edge("planner", "router")
graph.add_edge("router", "developer")
graph.add_edge("developer", "reviewer")
graph.add_edge("reviewer", "tester")

# Conditional edge for retry
graph.add_conditional_edges(
    "tester",
    should_continue_after_tester,
    {
        "end": END,
        "retry": "router"
    }
)
```

---

## State Structure

```python
class GraphState(TypedDict):
    task_id: str
    task_description: str
    
    plan: Optional[PlanOutput]  # {id, description, story_points, rationale}
    
    story_points_initial: Optional[Literal[1, 2, 3, 5, 8]]
    story_points_current: Optional[Literal[1, 2, 3, 5, 8]]
    
    escalations: int
    developer_tier: Optional[Literal["S", "M", "L"]]
    
    generated_code: Optional[str]
    reviewed_code: Optional[str]
    reviewer_feedback: Optional[str]
    
    test_inputs: list[str]
    test_outputs: list[str]
    test_passed: bool
    failure_history: list[str]
```

---

## Models (Architecture C)

| Role | Model |
|------|-------|
| Planner | `meta-llama/Llama-3.1-8B-Instruct` |
| Developer-S | `Qwen/Qwen2.5-Coder-1.5B-Instruct` |
| Developer-M | `Qwen/Qwen2.5-Coder-7B-Instruct` |
| Developer-L | `deepseek-ai/DeepSeek-Coder-V2-Instruct` |
| Reviewer | `meta-llama/Llama-3.1-8B-Instruct` |
| Tester | Python subprocess (not LLM) |

---

## Escalation Policy

| Condition | Action |
|-----------|--------|
| Test fails with S | Escalate to M, retry |
| Test fails with M | Escalate to L, retry |
| Test fails with L | End with `test_passed=False` |

Maximum escalations: 2 (S→M→L)

---

## Evaluation Metrics

- **Functional correctness**: % tasks where all tests pass
- **Routing distribution**: how often S/M/L is selected
- **Escalation count**: S→M and M→L transitions
- **Retries per task**: number of loops until PASS or failure
