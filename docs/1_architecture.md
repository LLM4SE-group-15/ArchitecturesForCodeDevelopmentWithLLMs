# System Architecture

## Overview

This project evaluates different LLM-based architectures for code generation, comparing single-agent vs multi-agent approaches, and testing the effect of prompt repetition on code generation accuracy.

The key insight is that **adaptivity is routing to different developer model sizes (S/M/L)** based on a Planner difficulty estimate and on test failures, rather than simply using more developers for harder tasks.

---

## Shared Logical Pipeline (Used in B and C)

```
Task
  → Planner (assign story points to the whole problem)
  → Router (select Developer-S/M/L based on difficulty)
  → Developer (S/M/L) — generates code snippet
  → Tester (non-LLM, runs Python tests)
  → Reviewer (reviews test results, provides feedback)
  → [PASS] finish | [FAIL] loop with feedback + possible escalation
```

### Architecture Diagram

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
│                       TESTER (NON-LLM)                        │
│  Runs Python tests, returns PASS/FAIL + error details         │
└────────────┬──────────────────────────────────────────────────┘
             │
             ▼
┌───────────────────────────────────────────────────────────────┐
│                           REVIEWER                            │
│  Analyzes test results + code, provides feedback for retry    │
│  Does NOT modify code - only generates actionable feedback    │
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

### Agent Roles

| Role | Responsibility |
|------|----------------|
| **Planner** | Assigns story points (1-2-3-5-8) as difficulty proxy; provides rationale |
| **Router** | Selects developer tier based on story points; handles escalation on failure |
| **Developer-S** | Implements code for easy tasks (story points 1-2) |
| **Developer-M** | Implements code for medium tasks (story points 3-5) or when S fails |
| **Developer-L** | Implements code for hard tasks (story points 8) or after repeated failures |
| **Reviewer** | Analyzes code + test results, provides feedback (no code modification) |
| **Tester** | Non-LLM: executes Python tests and collects errors |

### Story Points → Developer Tier Mapping

| Story Points | Difficulty | Developer Tier |
|--------------|------------|----------------|
| 1-2 | Easy | S (Small) |
| 3-5 | Medium | M (Medium) |
| 8 | Hard | L (Large) |

### Escalation Policy

When a task fails testing, the system can escalate to a stronger developer:

```
S (fail) → M (fail) → L (fail) → END
```

Maximum 2 escalations allowed (S→M→L).

---

## LangGraph Implementation

The pipeline is implemented using LangGraph's `StateGraph`. The `developer` node internally selects the model based on the `developer_tier` field in state.

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
graph.add_edge("developer", "tester")
graph.add_edge("tester", "reviewer")

# Conditional edge from reviewer (decides retry or end)
graph.add_conditional_edges(
    "reviewer",
    should_continue_after_reviewer,
    {
        "end": END,
        "retry": "router"
    }
)
```

### State Structure (GraphState)

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
    
    test_code: str
    entry_point: str
    test_passed: bool
    failure_history: list[str]
```

---

## Experimental Architectures

### Architecture A — Single-Agent Baseline

**Model Configuration:**
```python
Architecture.A = {
    "baseline": "Qwen/Qwen2.5-Coder-7B-Instruct"
}
```

**Flow:**
```
Task → Qwen2.5-Coder-7B (single call) → Tester → Result
```

**Purpose**: Measure baseline model performance without any orchestration.

---

### Architecture B — Multi-Agent, Single-Model

**Model Configuration:**
```python
Architecture.B = {
    "planner": "Qwen/Qwen2.5-Coder-7B-Instruct",
    "developer_s": "Qwen/Qwen2.5-Coder-7B-Instruct",
    "developer_m": "Qwen/Qwen2.5-Coder-7B-Instruct",
    "developer_l": "Qwen/Qwen2.5-Coder-7B-Instruct",
    "reviewer": "Qwen/Qwen2.5-Coder-7B-Instruct"
}
```

**Flow:**
```
Task
  → Planner (Qwen-7B)
  → Router (selects S/M/L, but all map to Qwen-7B)
  → Developer (Qwen-7B)
  → Tester
  → Reviewer (Qwen-7B)
  → [FAIL] correction loop (Qwen-7B)
```

**Purpose**: Isolate the effect of multi-role orchestration, holding the model constant.

---

### Architecture C — Multi-Agent, Multi-Model Hybrid

**Model Configuration:**
```python
Architecture.C = {
    "planner": "meta-llama/Meta-Llama-3-8B-Instruct",
    "developer_s": "Qwen/Qwen2.5-Coder-1.5B-Instruct",
    "developer_m": "Qwen/Qwen2.5-Coder-7B-Instruct",
    "developer_l": "Qwen/Qwen2.5-Coder-32B-Instruct",
    "reviewer": "meta-llama/Meta-Llama-3-8B-Instruct"
}
```

**Flow:**
```
Task
  → Planner (Llama-8B)
  → Router (uses story points + failure history)
  → Developer-S/M/L (Qwen 1.5B/7B/32B)
  → Tester
  → Reviewer (Llama-8B)
  → [FAIL] loop + story point escalation + reroute to stronger developer
```

**Purpose**: Measure the effect of specialized models per role + adaptive S/M/L routing.

---

### Architecture C1 — Multi-Agent, Always-Large Developer

Same as Architecture C, but always routes to Developer-L regardless of story points.

**Purpose**: Baseline for comparing adaptive routing (C) vs always using the strongest model (C1).

---

## Prompt Repetition Variants (-PR)

Based on **Leviathan et al., "Prompt Repetition Improves Non-Reasoning LLMs"** (arXiv:2512.14982, 2025).

### Technique

The technique repeats the user prompt content to allow each token to attend to all other prompt tokens:

```
# Standard prompt
User: "<QUERY>"

# With prompt repetition
User: "<QUERY>\n\n<QUERY>"
```

### Key Properties

| Property | Value |
|----------|-------|
| What gets repeated | User prompt content only (not system prompts) |
| Input token overhead | ~2x (prefill stage only) |
| Output token overhead | None |
| Latency overhead | Minimal (prefill is parallelizable) |
| Output format | Unchanged |

### Prompt Repetition Variants

| Variant | Base | Prompt Repetition |
|---------|------|-------------------|
| **A** | Single-agent | ❌ Disabled |
| **A-PR** | Single-agent | ✅ Enabled |
| **B** | Multi-agent, single-model | ❌ Disabled |
| **B-PR** | Multi-agent, single-model | ✅ Enabled |
| **C** | Multi-agent, multi-model | ❌ Disabled |
| **C-PR** | Multi-agent, multi-model | ✅ Enabled |

### Implementation

Prompt repetition is controlled by the `PROMPT_REPETITION` environment variable:

```bash
# Disable (default)
PROMPT_REPETITION=false

# Enable for -PR experiments
PROMPT_REPETITION=true
```

In the notebooks, this is set programmatically:
```python
os.environ["PROMPT_REPETITION"] = "true"
```

---

## Research Questions

### RQ1 — Effect of Multi-Agent Architecture (A vs B)

- **Question**: Does adding Planner/Router/Reviewer around the same baseline model improve functional correctness vs a single-shot agent?
- **Control**: Same model everywhere (Qwen2.5-Coder-7B-Instruct)
- **Expected**: B > A due to review and retry loop

### RQ2 — Effect of Specialized Models per Role (B vs C)

- **Question**: Do role-specialized models (generalist Planner/Reviewer + code specialists for Developers) outperform a single-model multi-agent pipeline?
- **Expected**: C ≥ B on hard tasks due to stronger Developer-L

### RQ3 — Effect of Adaptive Routing (C vs C1)

- **C1 (always-big)**: Always route to Developer-L
- **C (adaptive S/M/L)**: Route by story points and escalate on failures
- **Question**: Can adaptive routing reduce cost (time/tokens) while maintaining comparable correctness/quality?
- **Expected**: C ≈ C1 in pass rate, but C < C1 in cost

### RQ4 — Effect of Prompt Repetition (A/B/C vs A-PR/B-PR/C-PR)

- **Reference**: Leviathan et al., "Prompt Repetition Improves Non-Reasoning LLMs" (arXiv:2512.14982)
- **Technique**: Repeat user prompt content (`<QUERY>` → `<QUERY>\n\n<QUERY>`)
- **Question**: Does prompt repetition improve code generation accuracy for non-reasoning LLMs?
- **Expected**: -PR variants ≥ standard variants in pass rate

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| **Orchestration** | LangGraph (StateGraph), LangChain |
| **Models** | HuggingFace Inference API (Qwen, Llama) |
| **Tracking** | LangSmith (optional) |
| **Code Analysis** | Radon, Pylint |
| **Testing** | pytest, subprocess (sandboxed execution) |
| **Analysis** | pandas, matplotlib, seaborn |

---

## Notes

- All architectures assume **atomic (single-snippet) tasks** — the Developer returns a complete solution per task.
- The Tester runs generated code in a **sandboxed subprocess** with timeout protection.
- All experiments use the same **random seed (31)** for task sampling to ensure reproducibility.

---

## Related Documents

- **[3_evaluation.md](3_evaluation.md)**: Detailed metrics, analysis plan, and statistical tests
- **[2_story_points_planner.md](2_story_points_planner.md)**: Planner prompt design and rationale
