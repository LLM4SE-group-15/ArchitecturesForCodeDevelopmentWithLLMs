"""
HumanEval Dataset Task Loader

Loads coding tasks from the HumanEval dataset (openai/openai_humaneval) on HuggingFace.
Each task contains:
- task_id: Unique identifier (e.g., "HumanEval/0")
- prompt: Function signature + docstring describing the problem
- canonical_solution: Reference solution (not used during generation)
- test: Assertion-based test code
- entry_point: Name of the function to implement
"""

from dataclasses import dataclass
from typing import Optional
from datasets import load_dataset


@dataclass
class Task:
    """Represents a single coding task from the HumanEval dataset."""
    
    task_id: str
    prompt: str
    test: str
    entry_point: str
    canonical_solution: str = ""
    
    @property
    def question(self) -> str:
        """Returns the prompt as the task description (for compatibility)."""
        return self.prompt
    
    def __repr__(self) -> str:
        return f"Task(id={self.task_id}, entry_point={self.entry_point})"


class HumanEvalTaskLoader:
    """
    Loads tasks from the HumanEval dataset.
    
    The HumanEval dataset contains 164 hand-written programming problems
    with function signatures, docstrings, and assertion-based tests.
    
    Usage:
        loader = HumanEvalTaskLoader()
        
        # Load all tasks
        tasks = loader.load_all()
        
        # Load specific number of tasks
        tasks = loader.load_tasks(limit=10)
        
        # Load single task by ID
        task = loader.get_task("HumanEval/0")
        
        # Load single task by index
        task = loader.get_task_by_index(0)
    """
    
    def __init__(self):
        """Initialize the task loader."""
        self._dataset = None
    
    @property
    def dataset(self):
        """Lazy load the dataset on first access."""
        if self._dataset is None:
            print("Loading HumanEval dataset...")
            self._dataset = load_dataset(
                "openai/openai_humaneval",
                split="test",
                trust_remote_code=True
            )
            print(f"Loaded {len(self._dataset)} tasks.")
        return self._dataset
    
    def _parse_task(self, item: dict) -> Task:
        """
        Parse a dataset item into a Task object.
        
        Args:
            item: Raw dataset item with HumanEval fields.
            
        Returns:
            Task object.
        """
        return Task(
            task_id=item["task_id"],
            prompt=item["prompt"],
            test=item["test"],
            entry_point=item["entry_point"],
            canonical_solution=item.get("canonical_solution", "")
        )
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """
        Load a specific task by task_id.
        
        Args:
            task_id: The task_id field from the dataset (e.g., "HumanEval/0").
            
        Returns:
            Task object, or None if not found.
        """
        for item in self.dataset:
            if item["task_id"] == task_id:
                return self._parse_task(item)
        return None
    
    def get_task_by_index(self, index: int) -> Optional[Task]:
        """
        Load a task by dataset index.
        
        Args:
            index: Index in the dataset (0-163).
            
        Returns:
            Task object, or None if index is out of range.
        """
        if 0 <= index < len(self.dataset):
            return self._parse_task(self.dataset[index])
        return None
    
    def load_tasks(self, limit: int = 10, offset: int = 0) -> list[Task]:
        """
        Load a subset of tasks.
        
        Args:
            limit: Maximum number of tasks to load.
            offset: Starting index.
            
        Returns:
            List of Task objects.
        """
        tasks = []
        end_index = min(offset + limit, len(self.dataset))
        
        for i in range(offset, end_index):
            task = self._parse_task(self.dataset[i])
            tasks.append(task)
        
        return tasks
    
    def load_all(self) -> list[Task]:
        """
        Load all tasks from the dataset.
        
        Returns:
            List of all 164 Task objects.
        """
        return self.load_tasks(limit=len(self.dataset))
    
    def __len__(self) -> int:
        """Return total number of tasks in the dataset."""
        return len(self.dataset)


# Alias for backward compatibility
APPSTaskLoader = HumanEvalTaskLoader
