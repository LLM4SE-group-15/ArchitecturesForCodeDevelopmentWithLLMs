# System Architecture

## Overview

This project evaluates three experimental setups (A/B/C) built around a shared
multi-role pipeline. The key change versus the initial proposal is that
**adaptivity is no longer “more developers for harder tasks”**; instead,
adaptivity is **routing to different developer model sizes (S/M/L)** based on a
Planner difficulty estimate and on test failures.

## Shared Logical Pipeline (Used in B and C)

```
Task
  → Planner (assign story points to the whole problem)
  → Router (select Developer-S/M/L)
  → Developer (S/M/L) — single snippet produced
  → Reviewer (code review + refactor suggestions)
  → Tester (non-LLM, runs Python tests)
  → [PASS] finish | [FAIL] loop with feedback + possible escalation
```

### Roles

1. **Planner / Story-point estimator**
  - Assigns story points (1–2–3–5–8) to the whole problem as a difficulty proxy
   - Motivates the estimate (to support analysis)

2. **Router**
   - Reads story points
   - Selects the appropriate developer tier (S/M/L)
   - On repeated failures, can increase the estimated difficulty and escalate
    the task to a stronger developer

3. **Developer-S / Developer-M / Developer-L**
   - Implements or fixes code
   - Same role, different model capacity/cost
    - S: cheap, for easy problems (story points 1–2)
    - M: standard, for medium problems (3–5) or when S fails
    - L: strongest, for hard problems (8+) or after repeated failures

4. **Reviewer**
   - Performs code review: bugs, edge cases, style, maintainability
   - Provides actionable feedback for the correction loop
5. **Tester (non-LLM)**
   - Executes Python tests and collects logs/errors
   - Feeds failures back into the loop

## Experimental Setups

### Architecture A — Single-agent baseline

Model: **Qwen/Qwen2.5-Coder-7B-Instruct**

Flow:

```
Task → Qwen2.5-Coder-7B (single call) → Tester
```

Goal: measure how strong the baseline model is by itself.

### Architecture B — Multi-agent, single-model

Model: **Qwen/Qwen2.5-Coder-7B-Instruct** in every role.

Flow:

```
Task
  → Planner (Qwen-7B)
  → Router (selects S/M/L, but all map to Qwen-7B)
  → Developer (Qwen-7B)
  → Reviewer (Qwen-7B)
  → Tester
  → optional correction loop (Qwen-7B)
```

Comparison **A vs B** isolates the effect of the *multi-role architecture*
holding the model constant.

### Architecture C — Multi-agent, multi-model hybrid

Models:
- Planner + Reviewer: **meta-llama/Llama-3.1-8B-Instruct**
- Developer-S: **Qwen/Qwen2.5-Coder-1.5B-Instruct** (or 3B)
- Developer-M: **Qwen/Qwen2.5-Coder-7B-Instruct**
- Developer-L: **deepseek-ai/DeepSeek-Coder-V2-Instruct**

Flow:

```
Task
  → Planner (Llama 3.1 8B: story points)
  → Router (uses story points + failure history)
  → Developer-S/M/L (Qwen small / Qwen 7B / DeepSeek) — single snippet
  → Reviewer (Llama)
  → Tester
  → on FAIL: loop + story point escalation + reroute to stronger developer
```

Comparison **B vs C** measures the effect of using *different specialized
models per role* plus S/M/L routing.

## Research Questions / Experimental Comparisons

- **RQ1 — Effect of the multi-agent architecture (A vs B)**
  - Question: does adding Planner/Router/Reviewer around the same
    baseline code model improve functional correctness vs a single-shot agent?
  - Control: same model everywhere (**Qwen2.5-Coder-7B-Instruct**).

- **RQ2 — Effect of specialized models per role (B vs C)**
  - Question: do role-specialized models (generalist Planner/Reviewer + code
    specialists for Developers) outperform a single-model multi-agent pipeline?

- **RQ3 — Effect of adaptive routing inside C (C1 vs C2)**
  - **C1 (always-big)**: always route to Developer-L.
  - **C2 (adaptive S/M/L)**: route by story points and escalate on failures.
  - Question: can adaptive routing reduce cost (time/tokens) while maintaining
    comparable correctness/quality?

## Technology Stack

- **Orchestration**: LangGraph (StateGraph), LangChain
- **Models**: Open-source LLMs (Qwen / Llama / DeepSeek) via HuggingFace Inference API
- **Tracking**: LangSmith (optional)
- **Code analysis**: Radon, Pylint
- **Testing**: pytest, subprocess (for stdin/stdout tests)
- **Analysis**: pandas, matplotlib, seaborn

Note: the architecture assumes atomic (single-snippet) tasks — the Developer
returns a complete solution per task.

---

## Evaluation

See [evaluation.md](evaluation.md) for detailed metrics, analysis plan, and research questions.
