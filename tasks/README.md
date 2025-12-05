# Programming Tasks Dataset

This directory contains the programming tasks used for evaluation.

## Structure

Each task is in a separate directory: `task_001/`, `task_002/`, etc.

Each task directory contains:
- `description.txt` - Natural language task description
- `reference_solution.py` - Reference implementation
- `test_cases.py` - Unit tests for validation
- `metadata.json` - Task metadata (difficulty, source, etc.)

## Task Sources

Tasks are selected from:
- HumanEval dataset
- MBPP (Mostly Basic Python Problems)
- CodeNet subsets
- Past course assignments

## Example Task Structure

```
tasks/
├── task_001/
│   ├── description.txt
│   ├── reference_solution.py
│   ├── test_cases.py
│   └── metadata.json
├── task_002/
│   └── ...
```

## Adding Tasks

To add a new task:
1. Create a new directory `task_XXX/`
2. Add all required files
3. Ensure test cases are comprehensive
4. Update metadata with source and difficulty
