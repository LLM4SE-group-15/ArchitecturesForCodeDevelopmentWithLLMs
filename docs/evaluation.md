# Evaluation and Analysis Plan

This document describes the metrics, comparisons, and analysis to perform at the end of the project.

---

## Research Questions

### RQ1 — Effect of Multi-Agent Architecture (A vs B)

**Comparison**: Architecture A vs Architecture B (same model: Qwen-7B)

**Question**: Does introducing a multi-agent pipeline (Planner → Developer → Reviewer → Tester) improve code correctness compared to a single-agent approach?

| Aspect | A (Single-Agent) | B (Multi-Agent) |
|--------|------------------|-----------------|
| Model | Qwen-7B | Qwen-7B (all roles) |
| Pipeline | Single call | Planner → Router → Developer → Reviewer → Tester |
| Retry | No | Yes (on test failure) |

**Expected outcome**: B should have higher pass rate due to review and retry loop.

---

### RQ2 — Effect of Specialized Models per Role (B vs C)

**Comparison**: Architecture B vs Architecture C

**Question**: Does using different specialized models (generalist Planner/Reviewer, code-specialist Developer S/M/L) provide measurable benefits compared to using the same model for all roles?

| Aspect | B (Single-Model) | C (Multi-Model) |
|--------|------------------|-----------------|
| Planner | Qwen-7B | Llama-8B |
| Developer | Qwen-7B | Qwen-1.5B/7B/DeepSeek |
| Reviewer | Qwen-7B | Llama-8B |

**Expected outcome**: C should have better quality on hard tasks due to stronger Developer-L.

---

### RQ3 — Effect of Adaptive Routing (C1 vs C2)

**Comparison**: Within Architecture C

- **C1 (Always-Big)**: Always use Developer-L
- **C2 (Adaptive)**: Route by story points (S for easy, M for medium, L for hard)

**Question**: Can adaptive routing reduce cost (tokens, time) while maintaining or improving quality compared to always using the strongest developer?

| Aspect | C1 (Always-L) | C2 (Adaptive S/M/L) |
|--------|---------------|---------------------|
| Routing | Always L | Based on story points |
| Cost | High | Variable (lower average) |
| Escalation | Never | S→M→L on failure |

**Expected outcome**: C2 should have similar pass rate but lower average cost.

---

## Dataset

**APPS Dataset** (codeparrot/apps) - 5000 test tasks

| Difficulty | Count | Description |
|------------|-------|-------------|
| introductory | ~1000 | Basic problems (LeetCode Easy) |
| interview | ~3000 | Interview-level (LeetCode Medium) |
| competition | ~1000 | Competitive programming (LeetCode Hard) |

**Subset for experiments**: Use `load_balanced(per_level=N)` to get equal tasks per difficulty.

---

## Metrics

### Primary Metrics

| Metric | Description | Formula |
|--------|-------------|---------|
| **Pass Rate** | % of tasks where all tests pass | `passed_tasks / total_tasks` |
| **Pass@1** | Correctness on first attempt | For A and first attempt B/C |

### Cost Metrics

| Metric | Description |
|--------|-------------|
| **Total Tokens** | Sum of input + output tokens per task |
| **API Calls** | Number of LLM invocations per task |
| **Execution Time** | End-to-end time per task |

### Adaptive Metrics (B/C only)

| Metric | Description |
|--------|-------------|
| **Retry Count** | Number of loops until PASS or final FAIL |
| **Escalation Count** | How many S→M and M→L transitions |
| **Story Point Accuracy** | Compare Planner's estimate vs actual difficulty |
| **Tier Distribution** | % of tasks routed to S/M/L |

### Code Quality Metrics (Optional)

| Metric | Tool | Description |
|--------|------|-------------|
| **Cyclomatic Complexity** | Radon | Code complexity |
| **Maintainability Index** | Radon | Maintainability score |
| **Lines of Code** | - | Code length |
| **Pylint Score** | Pylint | Code quality score |

---

## Data to Log

For each task execution, log:

```python
{
    "task_id": "apps_123",
    "architecture": "C",
    "difficulty_ground_truth": "interview",  # From dataset
    
    # Planner output
    "story_points_initial": 5,
    "story_points_final": 8,  # After escalations
    "planner_rationale": "...",
    
    # Routing
    "developer_tier_initial": "M",
    "developer_tier_final": "L",
    "escalations": 1,
    "retry_count": 2,
    
    # Result
    "test_passed": True,
    "tests_total": 10,
    "tests_passed": 10,
    
    # Cost
    "total_tokens": 15000,
    "api_calls": 5,
    "execution_time_seconds": 45.2,
    
    # Code
    "generated_code": "...",
    "reviewed_code": "...",
    "reviewer_feedback": "...",
    "failure_history": ["Test 1: Expected 5, got 4", ...]
}
```

---

## Analysis Plan

### 1. Pass Rate Comparison

| Architecture | Pass Rate | 95% CI |
|--------------|-----------|--------|
| A | X% | [lo, hi] |
| B | Y% | [lo, hi] |
| C (Adaptive) | Z% | [lo, hi] |
| C (Always-L) | W% | [lo, hi] |

**Visualization**: Bar chart with error bars

### 2. Pass Rate by Difficulty

| Difficulty | A | B | C |
|------------|---|---|---|
| Introductory | | | |
| Interview | | | |
| Competition | | | |

**Visualization**: Grouped bar chart

### 3. Cost Analysis

| Architecture | Avg Tokens | Avg Time | Avg API Calls |
|--------------|------------|----------|---------------|
| A | | | |
| B | | | |
| C (Adaptive) | | | |
| C (Always-L) | | | |

**Visualization**: Bar chart, cost vs pass rate scatter plot

### 4. Routing Distribution (C only)

| Initial Tier | Count | % |
|--------------|-------|---|
| S | | |
| M | | |
| L | | |

**Visualization**: Pie chart or bar chart

### 5. Escalation Analysis (B/C only)

| Pattern | Count | Pass Rate |
|---------|-------|-----------|
| S (no escalation) | | |
| S → M | | |
| S → M → L | | |
| M (no escalation) | | |
| M → L | | |
| L (no escalation) | | |

**Visualization**: Sankey diagram or stacked bar

### 6. Story Point Accuracy (C only)

Compare Planner's story points vs dataset difficulty:

| Dataset Difficulty | Avg Story Points | Expected |
|--------------------|------------------|----------|
| Introductory | | 1-2 |
| Interview | | 3-5 |
| Competition | | 8 |

**Visualization**: Box plot or violin plot

### 7. Retry Dynamics

| Retries | A | B | C |
|---------|---|---|---|
| 0 (first pass) | | | |
| 1 | | | |
| 2 | | | |
| Failed after max | | | |

**Visualization**: Histogram

---

## Statistical Tests

- **Pass Rate Comparison**: McNemar's test (paired) or Chi-square (unpaired)
- **Cost Comparison**: Wilcoxon signed-rank or Mann-Whitney U
- **Effect Size**: Cohen's d or Cliff's delta

---

## Deliverables

1. **Results CSV**: Raw data for all task executions
2. **Summary Tables**: As shown above
3. **Visualizations**: Charts for each analysis
4. **Statistical Report**: Significance tests with p-values
5. **Discussion**: Interpretation of RQ1, RQ2, RQ3 findings
