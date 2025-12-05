# Adaptive Multi-Agent System (AMAS) Architecture

## 🎯 Overview

The Adaptive Multi-Agent System dynamically allocates development resources based on task complexity, spawning 1-3 collaborative developers depending on the difficulty score assigned by the Planner.

---

## 📊 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                          INPUT TASK                              │
│              "Write a function to solve problem X"               │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────────┐
        │         PLANNER AGENT                    │
        │  ┌────────────────────────────────┐      │
        │  │ 1. Analyze task complexity     │      │
        │  │ 2. Decompose into subtasks     │      │
        │  │ 3. Assign difficulty scores    │      │
        │  │    (0.0 - 1.0 per subtask)     │      │
        │  └────────────────────────────────┘      │
        └──────────────────┬───────────────────────┘
                           │
                           ▼
        ┌─────────────────────────────────────────────┐
        │        PLAN OUTPUT (TODO List)              │
        │ ┌─────────────────────────────────────────┐ │
        │ │ TODO-1: Core logic    [difficulty: 0.4] │ │
        │ │ TODO-2: Edge cases    [difficulty: 0.8] │ │
        │ │ TODO-3: Documentation [difficulty: 0.2] │ │
        │ └─────────────────────────────────────────┘ │
        └──────────────────┬──────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────────┐
        │    DYNAMIC TEAM ALLOCATION DECISION      │
        │                                          │
        │   FOR EACH TODO in plan.subtasks:        │
        │                                          │
        │   IF difficulty < 0.3:   → SOLO MODE    │
        │   IF 0.3 ≤ difficulty < 0.7: → PAIR MODE│
        │   IF difficulty ≥ 0.7:   → TEAM MODE    │
        └──────────────┬───────────────────────────┘
                       │
         ──────────────┼──────────────
         │             │             │
         ▼             ▼             ▼
    ┌────────┐   ┌──────────┐  ┌──────────────┐
    │ SOLO   │   │  PAIR    │  │   TEAM       │
    │ MODE   │   │  MODE    │  │   MODE       │
    └────────┘   └──────────┘  └──────────────┘


┌─────────────────────────────────────────────────────────────────┐
│                     SOLO MODE (difficulty < 0.3)                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│                    ┌─────────────────┐                          │
│                    │   DEVELOPER-1   │                          │
│                    │                 │                          │
│     TODO-3 ───────▶│  Implements     │────────▶ Subtask Code   │
│  "Add docs"        │  solution solo  │                          │
│  [diff: 0.2]       │                 │                          │
│                    └─────────────────┘                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│                PAIR MODE (0.3 ≤ difficulty < 0.7)                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   TODO-1 ──────┬──────────────────────────────────┐             │
│ "Core logic"   │                                  │             │
│ [diff: 0.4]    ▼                                  ▼             │
│         ┌──────────────┐                 ┌──────────────┐       │
│         │ DEVELOPER-A  │                 │ DEVELOPER-B  │       │
│         │              │                 │              │       │
│         │ Proposes     │                 │ Proposes     │       │
│         │ Solution A   │                 │ Solution B   │       │
│         └──────┬───────┘                 └───────┬──────┘       │
│                │                                 │              │
│                └────────────┬────────────────────┘              │
│                             ▼                                   │
│                  ┌─────────────────────┐                        │
│                  │  COLLABORATION      │                        │
│                  │  ┌───────────────┐  │                        │
│                  │  │ 1. Compare    │  │                        │
│                  │  │ 2. Discuss    │  │                        │
│                  │  │ 3. Merge best │  │                        │
│                  │  └───────────────┘  │                        │
│                  └──────────┬──────────┘                        │
│                             ▼                                   │
│                      Merged Subtask Code                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│                   TEAM MODE (difficulty ≥ 0.7)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   TODO-2 ──────┬──────────────┬──────────────┐                  │
│ "Edge cases"   │              │              │                  │
│ [diff: 0.8]    ▼              ▼              ▼                  │
│         ┌────────────┐ ┌────────────┐ ┌────────────┐            │
│         │  DEV-A     │ │  DEV-B     │ │  DEV-C     │            │
│         │            │ │            │ │            │            │
│         │ Handles    │ │ Handles    │ │ Handles    │            │
│         │ Core Edge  │ │ Validation │ │ Error      │            │
│         │ Cases      │ │ Logic      │ │ Handling   │            │
│         └─────┬──────┘ └─────┬──────┘ └─────┬──────┘            │
│               │              │              │                   │
│               └──────────────┼──────────────┘                   │
│                              ▼                                  │
│                   ┌─────────────────────┐                       │
│                   │    INTEGRATOR       │                       │
│                   │  ┌───────────────┐  │                       │
│                   │  │ 1. Merge code │  │                       │
│                   │  │ 2. Resolve    │  │                       │
│                   │  │    conflicts  │  │                       │
│                   │  │ 3. Optimize   │  │                       │
│                   │  └───────────────┘  │                       │
│                   └──────────┬──────────┘                       │
│                              ▼                                  │
│                      Integrated Subtask Code                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘


                              │
              ────────────────┼────────────────
              │               │               │
              ▼               ▼               ▼
         Subtask-1       Subtask-2       Subtask-3
           Code            Code            Code
              │               │               │
              └───────────────┼───────────────┘
                              ▼
                ┌──────────────────────────────┐
                │   INTEGRATION LAYER          │
                │                              │
                │  ┌────────────────────────┐  │
                │  │ 1. Combine all         │  │
                │  │    subtask solutions   │  │
                │  │ 2. Ensure coherence    │  │
                │  │ 3. Resolve dependencies│  │
                │  └────────────────────────┘  │
                └──────────────┬───────────────┘
                               ▼
                ┌──────────────────────────────┐
                │      REVIEWER AGENT          │
                │                              │
                │  ┌────────────────────────┐  │
                │  │ 1. Code quality check  │  │
                │  │ 2. Style compliance    │  │
                │  │ 3. Refactoring         │  │
                │  │ 4. Best practices      │  │
                │  └────────────────────────┘  │
                └──────────────┬───────────────┘
                               ▼
                ┌──────────────────────────────┐
                │       TESTER AGENT           │
                │                              │
                │  ┌────────────────────────┐  │
                │  │ 1. Run unit tests      │  │
                │  │ 2. Validate correctness│  │
                │  │ 3. Check edge cases    │  │
                │  └────────────────────────┘  │
                └──────────────┬───────────────┘
                               │
                               ▼
                        ┌─────────────┐
                        │   PASS?     │
                        └──────┬──────┘
                               │
                    ───────────┼───────────
                    │                     │
                    ▼ YES                 ▼ NO
            ┌──────────────┐      ┌──────────────┐
            │ FINAL CODE   │      │ RETRY LOOP   │
            │   OUTPUT     │      │ (max 2 iter) │
            └──────────────┘      └──────┬───────┘
                                         │
                                         ▼
                              Back to DEVELOPER(s)
                              with test feedback
```

---

## 🔄 Detailed Workflow States

### State 1: Planning Phase
```
Input: Task Description
Output: {
  "subtasks": [
    {"id": "todo_1", "description": "...", "difficulty": 0.4},
    {"id": "todo_2", "description": "...", "difficulty": 0.8},
    {"id": "todo_3", "description": "...", "difficulty": 0.2}
  ],
  "overall_complexity": 0.47,
  "strategy": "adaptive_allocation"
}
```

### State 2: Dynamic Allocation
```
FOR each subtask:
  difficulty_score = subtask.difficulty
  
  IF difficulty_score < 0.3:
    team_size = 1
    mode = "SOLO"
  
  ELIF difficulty_score < 0.7:
    team_size = 2
    mode = "PAIR"
  
  ELSE:
    team_size = 3
    mode = "TEAM"
    require_integrator = True
```

### State 3: Collaborative Execution

**SOLO Mode:**
```
Developer-1 → Implements → Code
```

**PAIR Mode:**
```
Developer-A → Solution-A ┐
                         ├→ Collaborate → Compare → Merge → Code
Developer-B → Solution-B ┘
```

**TEAM Mode:**
```
Developer-A → Part-A ┐
Developer-B → Part-B ├→ Integrator → Merge + Optimize → Code
Developer-C → Part-C ┘
```

### State 4: Integration & Quality Assurance
```
All Subtask Codes → Integration Layer → Complete Solution
                                              ↓
                                         Reviewer
                                              ↓
                                          Tester
                                              ↓
                                      PASS or RETRY
```

---

## 📈 Agent Roles & Responsibilities

| Agent | Role | Input | Output | Complexity |
|-------|------|-------|--------|------------|
| **Planner** | Task Analyzer & Decomposer | Task description | TODO list + difficulty scores | High |
| **Developer(s)** | Code Implementation | Subtask + plan | Python code | Medium |
| **Integrator** | Solution Merger | Multiple code fragments | Unified code | High |
| **Reviewer** | Quality Assurance | Complete code | Reviewed code + feedback | Medium |
| **Tester** | Validation | Code + tests | PASS/FAIL + results | Medium |

---

## 🎲 Difficulty Scoring Criteria

The Planner assigns difficulty scores based on:

| Score Range | Difficulty | Characteristics | Team Allocation |
|-------------|-----------|-----------------|-----------------|
| **0.0 - 0.3** | **LOW** | Simple logic, straightforward implementation, minimal edge cases | **1 Developer** |
| **0.3 - 0.7** | **MEDIUM** | Moderate complexity, multiple approaches possible, some edge cases | **2 Developers** (Pair) |
| **0.7 - 1.0** | **HIGH** | Complex logic, many edge cases, requires optimization, error handling | **3 Developers** (Team) |

**Scoring Factors:**
- Algorithm complexity
- Number of edge cases
- Required error handling
- Data structure complexity
- Optimization needs
- External dependencies

---

## 🔀 Collaboration Mechanisms

### Pair Collaboration (2 Developers)
```python
# Developer-A proposes
solution_a = """
def sum_even(nums):
    return sum([n for n in nums if n % 2 == 0])
"""

# Developer-B proposes
solution_b = """
def sum_even(nums):
    total = 0
    for n in nums:
        if n % 2 == 0:
            total += n
    return total
"""

# Collaboration: Compare and merge
merged = """
def sum_even(nums):
    # List comprehension for Pythonic style (Dev-A)
    # with explicit clarity (Dev-B suggestion)
    return sum(n for n in nums if n % 2 == 0)
"""
```

### Team Collaboration (3 Developers)
```python
# Developer-A: Core logic
core = "Main function implementation"

# Developer-B: Edge cases
edge_cases = "None handling, empty list, validation"

# Developer-C: Optimization
optimization = "Type hints, docstrings, error messages"

# Integrator: Combine all parts
final_code = integrate(core, edge_cases, optimization)
```

---

## 📊 Example Execution Flow

### Task: "Implement a function to find prime numbers up to N"

**Step 1: Planning**
```
Planner Analysis:
├─ Overall Difficulty: 0.65 (MEDIUM-HIGH)
├─ Subtasks:
│  ├─ TODO-1: Basic prime checking logic [0.5] → PAIR
│  ├─ TODO-2: Optimization (sieve) [0.8] → TEAM
│  └─ TODO-3: Input validation [0.3] → PAIR
```

**Step 2: Allocation**
```
TODO-1 [0.5] → Allocate 2 developers (PAIR mode)
TODO-2 [0.8] → Allocate 3 developers (TEAM mode)
TODO-3 [0.3] → Allocate 2 developers (PAIR mode)
```

**Step 3: Execution**
```
TODO-1: Dev-A + Dev-B → Trial division vs modulo check → Merge
TODO-2: Dev-A (sieve core) + Dev-B (optimization) + Dev-C (edge cases) → Integrator
TODO-3: Dev-A + Dev-B → Type checking + range validation → Merge
```

**Step 4: Integration**
```
Combine all TODO solutions → Complete prime finder function
```

**Step 5: QA**
```
Reviewer → Check efficiency, readability
Tester → Run tests (small N, large N, edge cases)
```

---

## 🎯 Key Advantages

1. **Resource Efficiency**: Only use multiple developers when complexity justifies it
2. **Quality Scaling**: More complex tasks get more collaborative attention
3. **Adaptive**: Automatically adjusts to task requirements
4. **Measurable**: Can analyze correlation between difficulty, team size, and outcomes
5. **Novel**: Unique approach for research comparison

---

## 📏 Evaluation Metrics

### Standard Metrics
- Functional correctness
- Code quality (complexity, maintainability)
- Token usage
- Execution time

### Adaptive-Specific Metrics
- **Difficulty Prediction Accuracy**: How well Planner estimates difficulty
- **Team Allocation Efficiency**: Optimal team size for each difficulty level
- **Collaboration Benefit**: Quality improvement with multiple developers
- **Integration Overhead**: Cost of merging multiple solutions
- **Scalability**: Performance across various difficulty distributions

---

## 🔬 Research Questions Addressed

| Research Question | How AMAS Addresses It |
|-------------------|----------------------|
| "Which architectures produce higher-quality code?" | Compare quality across team sizes (1 vs 2 vs 3 developers) |
| "How do agent coordination strategies impact correctness?" | Measure solo vs pair vs team collaboration effectiveness |
| "Does modular role separation improve code generation?" | Analyze subtask decomposition + integration benefits |

---

## 💻 Implementation with LangGraph

```python
from langgraph.graph import StateGraph, END

# Define state
class AdaptiveState(TypedDict):
    task: str
    plan: dict
    subtask_results: list
    integrated_code: str
    reviewed_code: str
    final_code: str
    iterations: int

# Build graph
workflow = StateGraph(AdaptiveState)

# Add nodes
workflow.add_node("planner", planner_node)
workflow.add_node("allocator", team_allocator_node)
workflow.add_node("solo_dev", solo_developer_node)
workflow.add_node("pair_dev", pair_developer_node)
workflow.add_node("team_dev", team_developer_node)
workflow.add_node("integrator", integration_node)
workflow.add_node("reviewer", reviewer_node)
workflow.add_node("tester", tester_node)

# Add conditional edges
workflow.add_edge("planner", "allocator")
workflow.add_conditional_edges(
    "allocator",
    route_by_difficulty,
    {
        "solo": "solo_dev",
        "pair": "pair_dev",
        "team": "team_dev"
    }
)
workflow.add_edge("solo_dev", "integrator")
workflow.add_edge("pair_dev", "integrator")
workflow.add_edge("team_dev", "integrator")
workflow.add_edge("integrator", "reviewer")
workflow.add_edge("reviewer", "tester")
workflow.add_conditional_edges(
    "tester",
    should_retry,
    {
        "pass": END,
        "retry": "allocator"
    }
)

# Compile
app = workflow.compile()
```

---

## 🚀 Next Steps

1. ✅ Implement Planner with difficulty scoring
2. ✅ Implement dynamic team allocator
3. ✅ Implement Developer agents (solo/pair/team modes)
4. ✅ Implement Integrator agent
5. ✅ Build LangGraph workflow
6. ✅ Test on sample tasks
7. ✅ Run full evaluation on 15 tasks
8. ✅ Analyze results and correlation metrics
