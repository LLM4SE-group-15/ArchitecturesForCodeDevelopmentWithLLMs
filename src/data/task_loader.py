"""
APPS Dataset Task Loader

Loads coding tasks from the APPS dataset (codeparrot/apps) on HuggingFace.
Each task contains:
- question: Natural language description of the problem
- input_output: JSON with test inputs (stdin) and expected outputs (stdout)
- difficulty: "introductory", "interview", or "competition"
"""

import json
from dataclasses import dataclass
from typing import Optional
from datasets import load_dataset


@dataclass
class Task:
    """Represents a single coding task from the APPS dataset."""
    
    problem_id: int
    question: str
    difficulty: str
    inputs: list[str]
    outputs: list[str]
    starter_code: str = ""
    
    @property
    def task_id(self) -> str:
        """Returns task ID as string for use in GraphState."""
        return f"apps_{self.problem_id}"
    
    def __repr__(self) -> str:
        return (
            f"Task(id={self.problem_id}, difficulty={self.difficulty}, "
            f"tests={len(self.inputs)})"
        )


class APPSTaskLoader:
    """
    Loads and filters tasks from the APPS dataset.
    
    The APPS dataset contains 10,000 coding problems with three difficulty levels:
    - introductory: Basic programming problems (similar to easy LeetCode)
    - interview: Standard interview questions (similar to medium LeetCode)
    - competition: Competitive programming problems (similar to hard LeetCode)
    
    Usage:
        loader = APPSTaskLoader()
        
        # Load 5 tasks per difficulty level (15 total)
        tasks = loader.load_balanced(per_level=5)
        
        # Load specific difficulty
        easy_tasks = loader.load_by_difficulty("introductory", limit=10)
        
        # Load single task
        task = loader.get_task(problem_id=0)
    """
    
    VALID_DIFFICULTIES = {"introductory", "interview", "competition"}
    
    def __init__(self, split: str = "test"):
        """
        Initialize the task loader.
        
        Args:
            split: Dataset split to use ("train" or "test"). Default is "test".
                   Both splits contain 5000 samples each.
        """
        self.split = split
        self._dataset = None
    
    @property
    def dataset(self):
        """Lazy load the dataset on first access."""
        if self._dataset is None:
            print(f"Loading APPS dataset ({self.split} split)...")
            self._dataset = load_dataset(
                "codeparrot/apps",
                split=self.split,
                trust_remote_code=True
            )
            print(f"Loaded {len(self._dataset)} tasks.")
        return self._dataset
    
    def _parse_task(self, item: dict) -> Optional[Task]:
        """
        Parse a dataset item into a Task object.
        
        Args:
            item: Raw dataset item with fields from APPS.
            
        Returns:
            Task object, or None if parsing fails.
        """
        try:
            # Parse the input_output JSON string
            io_data = json.loads(item["input_output"])
            
            inputs = io_data.get("inputs", [])
            outputs = io_data.get("outputs", [])
            
            # Skip tasks with no test cases
            if not inputs or not outputs:
                return None
            
            return Task(
                problem_id=item["problem_id"],
                question=item["question"],
                difficulty=item["difficulty"].lower(),
                inputs=inputs,
                outputs=outputs,
                starter_code=item.get("starter_code", "") or ""
            )
        except (json.JSONDecodeError, KeyError, TypeError):
            return None
    
    def get_task(self, problem_id: int) -> Optional[Task]:
        """
        Load a specific task by problem ID.
        
        Args:
            problem_id: The problem_id field from the dataset.
            
        Returns:
            Task object, or None if not found or parsing fails.
        """
        for item in self.dataset:
            if item["problem_id"] == problem_id:
                return self._parse_task(item)
        return None
    
    def load_by_difficulty(
        self, 
        difficulty: str, 
        limit: int = 5,
        skip_empty_tests: bool = True
    ) -> list[Task]:
        """
        Load tasks filtered by difficulty level.
        
        Args:
            difficulty: One of "introductory", "interview", "competition".
            limit: Maximum number of tasks to load.
            skip_empty_tests: Skip tasks that have no test cases.
            
        Returns:
            List of Task objects.
        """
        if difficulty.lower() not in self.VALID_DIFFICULTIES:
            raise ValueError(
                f"Invalid difficulty: {difficulty}. "
                f"Must be one of {self.VALID_DIFFICULTIES}"
            )
        
        tasks = []
        for item in self.dataset:
            if item["difficulty"].lower() != difficulty.lower():
                continue
            
            task = self._parse_task(item)
            if task is None and skip_empty_tests:
                continue
            
            if task is not None:
                tasks.append(task)
            
            if len(tasks) >= limit:
                break
        
        return tasks
    
    def load_balanced(self, per_level: int = 5) -> list[Task]:
        """
        Load a balanced set of tasks across all difficulty levels.
        
        Args:
            per_level: Number of tasks per difficulty level.
            
        Returns:
            List of Task objects (total = per_level * 3).
        """
        tasks = []
        
        for difficulty in ["introductory", "interview", "competition"]:
            level_tasks = self.load_by_difficulty(difficulty, limit=per_level)
            tasks.extend(level_tasks)
            print(f"  Loaded {len(level_tasks)} {difficulty} tasks")
        
        return tasks
    
    def __len__(self) -> int:
        """Return total number of tasks in the dataset."""
        return len(self.dataset)
