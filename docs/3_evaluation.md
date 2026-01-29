# Evaluation and Analysis Plan

This document describes the metrics, comparisons, and analysis to perform at the end of the project.

---

## Research Questions

### RQ1 — Effect of Multi-Agent Architecture (A vs B)

**Comparison**: Architecture A vs Architecture B (same model: Qwen-7B)

**Question**: Does introducing a multi-agent pipeline (Planner → Developer → Tester → Reviewer) improve code correctness compared to a single-agent approach?

| Aspect | A (Single-Agent) | B (Multi-Agent) |
|--------|------------------|-----------------|
| Model | Qwen-7B | Qwen-7B (all roles) |
| Pipeline | Single call | Planner → Router → Developer → Tester → Reviewer |
| Retry | No | Yes (on test failure) |

---

### RQ2 — Effect of Specialized Models per Role (B vs C)

**Comparison**: Architecture B vs Architecture C

**Question**: Does using different specialized models (generalist Planner/Reviewer, code-specialist Developer S/M/L) provide measurable benefits compared to using the same model for all roles?

| Aspect | B (Single-Model) | C (Multi-Model) |
|--------|------------------|-----------------|
| Planner | Qwen-7B | Llama-8B |
| Developer | Qwen-7B | Qwen-1.5B / 7B / 32B |
| Reviewer | Qwen-7B | Llama-8B |

---

### RQ3 — Effect of Adaptive Routing (C vs C1)

**Comparison**: Within Architecture C variants

- **C (Adaptive)**: Route by story points (S for easy, M for medium, L for hard)
- **C1 (Always-Big)**: Always use Developer-L

**Question**: Can adaptive routing reduce cost (tokens, time) while maintaining or improving quality compared to always using the strongest developer?

| Aspect | C1 (Always-L) | C (Adaptive S/M/L) |
|--------|---------------|---------------------|
| Routing | Always L | Based on story points |
| Cost | High | Variable (lower average) |
| Escalation | Never | S→M→L on failure |

---

### RQ4 — Effect of Prompt Repetition (A/B/C vs A-PR/B-PR/C-PR)

PAPER: https://arxiv.org/abs/2512.14982 

**Comparison**: Each architecture with and without prompt repetition

**Question**: Does repeating the user prompt improve code generation accuracy, as suggested by recent research on non-reasoning LLMs?

#### Technique Overview

Based on the paper by **Leviathan et al., "Prompt Repetition Improves Non-Reasoning LLMs"** (arXiv:2512.14982, 2025):

- **Why it works**: LLMs are causal language models where past tokens cannot attend to future tokens. Repeating the prompt allows each token to attend to every other prompt token, improving comprehension.
- **How it works**: Transform the user prompt from `<QUERY>` to `<QUERY>\n\n<QUERY>`
- **Key finding**: The paper reports 47 wins out of 70 benchmark-model combinations, with 0 losses across Gemini, GPT, Claude, and DeepSeek models.

#### Implementation in This Project

| Component | What Gets Repeated |
|-----------|-------------------|
| **System prompts** | NOT repeated (unchanged) |
| **User prompts** | Repeated: content duplicated with `\n\n` separator |

Example transformation:

```
# Before (standard)
User: "Implement the following function:\n\ndef add(a, b):\n    ..."

# After (with prompt repetition)
User: "Implement the following function:\n\ndef add(a, b):\n    ...

Implement the following function:\n\ndef add(a, b):\n    ..."
```

#### Comparison Table

| Aspect | Standard | With Prompt Repetition (-PR) |
|--------|----------|------------------------------|
| Prompt format | `<QUERY>` | `<QUERY>\n\n<QUERY>` |
| Input tokens | Normal | ~2x (prefill stage only) |
| Output tokens | Normal | Unchanged |
| Latency | Normal | Unchanged (prefill is parallelizable) |
| Output format | Normal | Unchanged |

#### Experimental Variants

| Variant | Base Architecture | Prompt Repetition |
|---------|-------------------|-------------------|
| A | Single-agent | ❌ |
| A-PR | Single-agent | ✅ |
| B | Multi-agent, single-model | ❌ |
| B-PR | Multi-agent, single-model | ✅ |
| C | Multi-agent, multi-model | ❌ |
| C-PR | Multi-agent, multi-model | ✅ |

---

## Dataset

**HumanEval Dataset** (openai/openai_humaneval) — 164 hand-written programming problems

| Field | Description |
|-------|-------------|
| `task_id` | Unique identifier (e.g., "HumanEval/0") |
| `prompt` | Function signature + docstring |
| `test` | Assertion-based test code |
| `entry_point` | Function name to implement |
| `canonical_solution` | Reference solution (not used during generation) |

**Testing approach**: Assertion-based testing — the generated code is combined with test assertions and executed in a sandboxed subprocess.

---

## Metrics

### Primary Metrics

| Metric | Description | Formula |
|--------|-------------|---------|
| **Pass Rate** | % of tasks where all tests pass | `passed_tasks / total_tasks` |
| **Pass@1** | Correctness on first attempt | First attempt for A; first Developer call for B/C |

### Cost Metrics

| Metric | Description |
|--------|-------------|
| **Total Tokens** | Sum of input + output tokens per task |
| **API Calls** | Number of LLM invocations per task |
| **Execution Time** | End-to-end time per task (seconds) |

### Adaptive Metrics (B/C only)

| Metric | Description |
|--------|-------------|
| **Retry Count** | Number of Developer→Reviewer→Tester loops until PASS or final FAIL |
| **Escalation Count** | Number of S→M and M→L tier transitions |
| **Story Point Accuracy** | Correlation between Planner's estimate and actual task difficulty |
| **Tier Distribution** | Percentage of tasks routed to S/M/L |

### Static Code Quality Metrics

Static code quality metrics are computed for all generated code using **Radon**, a Python library for code analysis. These metrics evaluate code quality independently of functional correctness.

#### Cyclomatic Complexity (CC)

**Definition**: Cyclomatic Complexity measures the number of linearly independent paths through a program's source code. It quantifies the structural complexity of code based on control flow.

**Formula**: `CC = E - N + 2P`

Where:
- `E` = Number of edges in the control flow graph
- `N` = Number of nodes in the control flow graph
- `P` = Number of connected components (usually 1 for a single function)

**Interpretation Scale (lower is better)**:

| CC Range | Risk Assessment | Description |
|----------|-----------------|-------------|
| 1-5 | Low | Simple, well-structured code |
| 6-10 | Moderate | Moderately complex, acceptable |
| 11-20 | High | Complex, harder to test |
| 21+ | Very High | Untestable, high maintenance risk |

**What contributes to CC**:
- Each `if`, `elif`, `for`, `while`, `except`, `with`, `assert`, `and`, `or` adds +1
- Each function starts with CC = 1

**Implementation**: Computed using `radon.complexity.cc_visit()` for each function in the generated code. The average CC across all functions is reported.

#### Maintainability Index (MI)

**Definition**: The Maintainability Index is a composite metric that estimates how maintainable the source code is. Higher values indicate more maintainable code.

**Formula**:

```
MI = max(0, 100 * (171 - 5.2 * ln(HV) - 0.23 * CC - 16.2 * ln(LOC)) / 171)
```

Where:
- `HV` = Halstead Volume (based on operators and operands)
- `CC` = Cyclomatic Complexity
- `LOC` = Lines of Code

**Interpretation Scale (0-100, higher is better)**:

| MI Range | Maintainability | Description |
|----------|-----------------|-------------|
| 0-9 | Very Low | Extremely difficult to maintain |
| 10-19 | Low | Difficult to maintain |
| 20-39 | Moderate | Moderately maintainable |
| 40-64 | Good | Reasonably maintainable |
| 65-84 | High | Easy to maintain |
| 85-100 | Very High | Excellent maintainability |

**Implementation**: Computed using `radon.metrics.mi_visit()` which returns the MI score for the entire code block.

#### Metrics Summary Table

| Metric | Tool | Direction | Description |
|--------|------|-----------|-------------|
| **Cyclomatic Complexity** | Radon | Lower is better | Number of independent paths through code |
| **Maintainability Index** | Radon | Higher is better | Composite maintainability score (0-100) |
| **Lines of Code** | — | Contextual | Total lines of generated code |

#### Analysis: Passed vs Failed Tasks

The static metrics are computed separately for passed and failed tasks to investigate whether code quality correlates with functional correctness. This analysis helps answer:

- Do failed tasks exhibit higher complexity?
- Is there a maintainability threshold that predicts success?
- Does the multi-agent pipeline produce more maintainable code than single-agent?

---

## Data Logging Format

For each task execution, log the following JSON record:

```json
{
    "task_id": "HumanEval/42",
    "architecture": "C-PR",
    "prompt_repetition": true,
    
    "story_points_initial": 5,
    "story_points_final": 8,
    "planner_rationale": "...",
    
    "developer_tier_initial": "M",
    "developer_tier_final": "L",
    "escalations": 1,
    "retry_count": 2,
    
    "test_passed": true,
    
    "total_tokens": 15000,
    "api_calls": 5,
    "elapsed_seconds": 45.2,
    
    "generated_code": "...",
    "reviewed_code": "...",
    "reviewer_feedback": "...",
    "failure_history": ["AssertionError: expected 5, got 4"],
    
    "cyclomatic_complexity": 4.0,
    "maintainability_index": 75.51
}
```

---

## Analysis Plan

### 1. Pass Rate Comparison

| Architecture | Pass Rate | 95% CI |
|--------------|-----------|--------|
| A | X% | [lo, hi] |
| A-PR | X% | [lo, hi] |
| B | Y% | [lo, hi] |
| B-PR | Y% | [lo, hi] |
| C | Z% | [lo, hi] |
| C-PR | Z% | [lo, hi] |

**Visualization**: Bar chart with error bars, grouped by prompt repetition status

### 2. Prompt Repetition Effect (RQ4)

| Comparison | Δ Pass Rate | p-value | Effect Size |
|------------|-------------|---------|-------------|
| A vs A-PR | | | |
| B vs B-PR | | | |
| C vs C-PR | | | |

**Visualization**: Paired bar chart showing before/after prompt repetition

### 3. Cost Analysis

| Architecture | Avg Tokens | Avg Time | Avg API Calls |
|--------------|------------|----------|---------------|
| A / A-PR | | | |
| B / B-PR | | | |
| C / C-PR | | | |

**Visualization**: Cost vs pass rate scatter plot

### 4. Routing Distribution (C/C-PR only)

| Initial Tier | Count | % | Pass Rate |
|--------------|-------|---|-----------|
| S | | | |
| M | | | |
| L | | | |

**Visualization**: Pie chart or stacked bar chart

### 5. Escalation Analysis (B/C only)

| Pattern | Count | Pass Rate |
|---------|-------|-----------|
| S (no escalation) | | |
| S → M | | |
| S → M → L | | |
| M (no escalation) | | |
| M → L | | |
| L (no escalation) | | |

**Visualization**: Sankey diagram or flow chart

### 6. Story Point Accuracy (C only)

Compare Planner's story points vs actual task outcome:

| Story Points | Count | Pass Rate | Avg Escalations |
|--------------|-------|-----------|-----------------|
| 1-2 (Easy) | | | |
| 3-5 (Medium) | | | |
| 8 (Hard) | | | |

**Visualization**: Box plot or violin plot

### 7. Static Code Quality Analysis

Compare Cyclomatic Complexity and Maintainability Index across architectures and task outcomes:

| Architecture | Avg CC | Median CC | Max CC | Avg MI | Median MI | Min MI |
|--------------|--------|-----------|--------|--------|-----------|--------|
| A | | | | | | |
| A-PR | | | | | | |
| B | | | | | | |
| B-PR | | | | | | |
| C | | | | | | |
| C-PR | | | | | | |

**Comparison: Passed vs Failed Tasks**

| Task Outcome | Avg CC | Avg MI | Count |
|--------------|--------|--------|-------|
| Passed | | | |
| Failed | | | |

**Analysis Questions**:
- Does lower CC correlate with higher pass rates?
- Do multi-agent architectures produce more maintainable code (higher MI)?
- Is there a significant difference in code quality between passed and failed tasks?

**Visualization**: 
- Violin plot of CC distribution by architecture
- Scatter plot: MI vs Pass Rate
- Box plot comparing CC/MI for passed vs failed tasks

---

## Statistical Tests

| Comparison | Test | Purpose |
|------------|------|---------|
| Pass Rate (paired) | McNemar's test | Compare A vs A-PR, B vs B-PR, C vs C-PR |
| Pass Rate (unpaired) | Chi-square test | Compare A vs B vs C |
| Cost Comparison | Mann-Whitney U / Wilcoxon | Compare distributions |
| Effect Size | Cohen's d / Cliff's delta | Measure magnitude of difference |
| CC: Passed vs Failed | Mann-Whitney U | Compare complexity between passed/failed tasks |
| MI: Passed vs Failed | Mann-Whitney U | Compare maintainability between passed/failed tasks |
| CC: Across Architectures | Kruskal-Wallis | Compare CC distributions across A/B/C |
| MI: Across Architectures | Kruskal-Wallis | Compare MI distributions across A/B/C |

---

## Deliverables

1. **Results JSONL**: Raw data for all task executions (one file per architecture)
2. **Summary Tables**: Aggregated metrics as shown above
3. **Visualizations**: Charts for each analysis section
4. **Statistical Report**: Significance tests with p-values and effect sizes
5. **Discussion**: Interpretation of RQ1, RQ2, RQ3, RQ4 findings
