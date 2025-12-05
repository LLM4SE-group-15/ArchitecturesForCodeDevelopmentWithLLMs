# System Architecture

## Overview

This project compares two LLM-based code generation architectures:

### 1. Single-Agent Baseline

```
Task Description → LLM → Generated Code
```

**Characteristics:**
- One prompt, one response
- Direct code generation
- Minimal overhead
- Baseline for comparison

**Implementation:**
- LangChain ChatOpenAI
- Single prompt template
- GPT-4o-mini model

---

### 2. Multi-Agent System

```
Task → Planner → Developer → Reviewer → Tester
         ↓          ↓          ↓         ↓
       Plan      Code      Feedback   Results
                                         ↓
                                   [Pass/Retry]
```

**Agent Roles:**

1. **Planner Agent**
   - Analyzes task requirements
   - Creates implementation plan
   - Identifies edge cases

2. **Developer Agent**
   - Implements code from plan
   - Follows coding standards
   - Adds documentation

3. **Reviewer Agent**
   - Reviews code quality
   - Suggests improvements
   - Checks for bugs

4. **Tester Agent**
   - Validates correctness
   - Identifies failures
   - Triggers re-iteration if needed

**Implementation:**
- LangGraph StateGraph
- Conditional routing
- State management
- Iteration loops (max 3)

---

## Technology Stack

- **LLM Framework**: LangChain, LangGraph
- **Model**: GPT-4o-mini (OpenAI)
- **Tracking**: LangSmith
- **Code Analysis**: Radon, Pylint
- **Testing**: pytest, unittest
- **Data Analysis**: pandas, matplotlib

---

## Evaluation Pipeline

```
1. Load Task
2. Generate Code (Single-Agent)
3. Generate Code (Multi-Agent)
4. Run Tests (Functional Correctness)
5. Analyze Code (Quality Metrics)
6. Collect Performance Data
7. Store Results
8. Compare Architectures
```
