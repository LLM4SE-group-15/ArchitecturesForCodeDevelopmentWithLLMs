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