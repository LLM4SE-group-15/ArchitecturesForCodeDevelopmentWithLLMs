# Programming Tasks for A2 Project

This document lists the 15 programming tasks selected for evaluating single-agent vs adaptive multi-agent architectures.

## Task Selection Criteria

Tasks are selected to cover:
- **Difficulty Range**: Easy (0.2-0.3), Medium (0.4-0.6), Hard (0.7-0.9)
- **Variety**: Different algorithm types, data structures, complexity levels
- **Testability**: Clear requirements with unit tests

## Task Sources Distribution

- **HumanEval**: 8 tasks (canonical benchmarks)
- **MBPP**: 7 tasks (basic to intermediate Python problems)
- **Total**: 15 tasks

---

## Selected Tasks

### From HumanEval (8 tasks)

#### 1. **HumanEval/0: has_close_elements**
- **Description**: Check if any two numbers in a list are closer than a threshold
- **Difficulty**: 0.3 (Easy-Medium)
- **Source**: HumanEval dataset
- **URL**: https://github.com/openai/human-eval

#### 2. **HumanEval/1: separate_paren_groups**
- **Description**: Separate nested parentheses groups
- **Difficulty**: 0.5 (Medium)
- **Source**: HumanEval dataset

#### 3. **HumanEval/4: mean_absolute_deviation**
- **Description**: Calculate mean absolute deviation of a list
- **Difficulty**: 0.3 (Easy-Medium)
- **Source**: HumanEval dataset

#### 4. **HumanEval/7: filter_by_substring**
- **Description**: Filter strings containing a substring
- **Difficulty**: 0.2 (Easy)
- **Source**: HumanEval dataset

#### 5. **HumanEval/10: is_palindrome**
- **Description**: Check if string is a palindrome
- **Difficulty**: 0.2 (Easy)
- **Source**: HumanEval dataset

#### 6. **HumanEval/12: longest**
- **Description**: Find longest string in a list
- **Difficulty**: 0.2 (Easy)
- **Source**: HumanEval dataset

#### 7. **HumanEval/17: parse_music**
- **Description**: Parse musical note notation
- **Difficulty**: 0.6 (Medium-Hard)
- **Source**: HumanEval dataset

#### 8. **HumanEval/31: is_prime**
- **Description**: Check if number is prime
- **Difficulty**: 0.4 (Medium)
- **Source**: HumanEval dataset

---

### From MBPP (7 tasks)

#### 9. **MBPP/2: similar_elements**
- **Description**: Find similar elements in two lists
- **Difficulty**: 0.3 (Easy-Medium)
- **Source**: MBPP dataset
- **URL**: https://github.com/google-research/google-research/tree/master/mbpp

#### 10. **MBPP/11: remove_odd**
- **Description**: Remove odd numbers from a list
- **Difficulty**: 0.2 (Easy)
- **Source**: MBPP dataset

#### 11. **MBPP/13: sum_of_digits**
- **Description**: Calculate sum of digits in a number
- **Difficulty**: 0.3 (Easy-Medium)
- **Source**: MBPP dataset

#### 12. **MBPP/56: check_subset**
- **Description**: Check if one list is subset of another
- **Difficulty**: 0.3 (Easy-Medium)
- **Source**: MBPP dataset

#### 13. **MBPP/163: calculate_polygon_area**
- **Description**: Calculate area of regular polygon
- **Difficulty**: 0.5 (Medium)
- **Source**: MBPP dataset

#### 14. **MBPP/223: is_majority**
- **Description**: Check if element appears more than n/2 times
- **Difficulty**: 0.4 (Medium)
- **Source**: MBPP dataset

#### 15. **MBPP/412: remove_duplicates_sorted**
- **Description**: Remove duplicates from sorted array in-place
- **Difficulty**: 0.5 (Medium)
- **Source**: MBPP dataset

---

## Difficulty Distribution

| Difficulty | Count | Percentage | Expected Team Allocation |
|------------|-------|------------|-------------------------|
| Easy (0.2-0.3) | 7 | 47% | Solo (1 dev) or Pair (2 dev) |
| Medium (0.4-0.6) | 6 | 40% | Pair (2 dev) |
| Hard (0.7-0.9) | 2 | 13% | Team (3 dev) |

This distribution allows us to test all three allocation modes (solo/pair/team).

---

## How to Fetch Tasks

### Option 1: Use Automated Scraper
```bash
python scripts/fetch_tasks.py
```

### Option 2: Manual Download from Datasets

**HumanEval:**
```bash
# Clone HumanEval repository
git clone https://github.com/openai/human-eval.git

# Extract specific problems from data/HumanEval.jsonl
```

**MBPP:**
```bash
# Download MBPP dataset
wget https://raw.githubusercontent.com/google-research/google-research/master/mbpp/mbpp.jsonl

# Parse and extract specific problems
```

### Option 3: Use Helper Script
```python
from scripts.fetch_tasks import TaskDatasetBuilder

builder = TaskDatasetBuilder(output_dir="tasks")
builder.build_dataset(
    humaneval_count=8,
    mbpp_count=7,
    codenet_count=0
)
```

---

## Task Format

Each task directory contains:

```
task_XXX/
├── description.txt          # Natural language task description
├── reference_solution.py    # Verified correct solution
├── test_cases.py           # Unit tests
└── metadata.json           # Task metadata
```

### Metadata Format

```json
{
  "task_id": "task_001",
  "title": "Task Title",
  "difficulty": 0.4,
  "source": "humaneval",
  "source_id": "HumanEval/31",
  "category": "algorithms",
  "tags": ["numbers", "math", "iteration"],
  "estimated_time_minutes": 10
}
```

---

## Next Steps

1. **Fetch Tasks**: Run `python scripts/fetch_tasks.py`
2. **Validate Tasks**: Ensure all test cases pass with reference solutions
3. **Review Difficulty Scores**: Manually adjust if needed based on actual complexity
4. **Run Evaluation**: Execute both architectures on all 15 tasks
5. **Analyze Results**: Compare performance across difficulty levels

---

## Notes

- Tasks are deliberately varied to test adaptability
- Difficulty scores are initial estimates (can be refined after pilot runs)
- All tasks are Python-focused (consistent with course requirements)
- Test coverage is comprehensive for each task
- Reference solutions follow PEP 8 and best practices

---

## References

- HumanEval: https://github.com/openai/human-eval
- MBPP: https://github.com/google-research/google-research/tree/master/mbpp
- CodeNet: https://github.com/IBM/Project_CodeNet
