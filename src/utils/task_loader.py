"""
Task Loader

Utilities for loading programming tasks from the dataset.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional

from src.utils.logger import setup_logger
from src.utils.config import Config

logger = setup_logger(__name__)


class Task:
    """Represents a programming task."""
    
    def __init__(self, task_dir: Path):
        """
        Initialize task from directory.
        
        Args:
            task_dir: Path to task directory
        """
        self.task_dir = task_dir
        self.task_id = task_dir.name
        
        # Load task components
        self.description = self._load_description()
        self.reference_solution = self._load_reference_solution()
        self.test_cases = self._load_test_cases()
        self.metadata = self._load_metadata()
    
    def _load_description(self) -> str:
        """Load task description."""
        desc_file = self.task_dir / "description.txt"
        if desc_file.exists():
            return desc_file.read_text(encoding='utf-8').strip()
        return ""
    
    def _load_reference_solution(self) -> str:
        """Load reference solution code."""
        ref_file = self.task_dir / "reference_solution.py"
        if ref_file.exists():
            return ref_file.read_text(encoding='utf-8')
        return ""
    
    def _load_test_cases(self) -> str:
        """Load test cases code."""
        test_file = self.task_dir / "test_cases.py"
        if test_file.exists():
            return test_file.read_text(encoding='utf-8')
        return ""
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load task metadata."""
        meta_file = self.task_dir / "metadata.json"
        if meta_file.exists():
            with open(meta_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        return {
            "task_id": self.task_id,
            "description": self.description,
            "reference_solution": self.reference_solution,
            "test_cases": self.test_cases,
            "metadata": self.metadata
        }


class TaskLoader:
    """Loads programming tasks from the dataset."""
    
    def __init__(self, tasks_dir: Optional[str] = None):
        """
        Initialize task loader.
        
        Args:
            tasks_dir: Path to tasks directory (default from config)
        """
        self.tasks_dir = Path(tasks_dir or Config.TASKS_DIR)
        logger.info(f"TaskLoader initialized with tasks_dir={self.tasks_dir}")
    
    def load_task(self, task_id: str) -> Task:
        """
        Load a single task by ID.
        
        Args:
            task_id: Task identifier (e.g., "task_001")
            
        Returns:
            Task object
        """
        task_dir = self.tasks_dir / task_id
        if not task_dir.exists():
            raise ValueError(f"Task directory not found: {task_dir}")
        
        task = Task(task_dir)
        logger.info(f"Loaded task: {task_id}")
        return task
    
    def load_all_tasks(self) -> List[Task]:
        """
        Load all tasks from the tasks directory.
        
        Returns:
            List of Task objects
        """
        tasks = []
        
        if not self.tasks_dir.exists():
            logger.warning(f"Tasks directory not found: {self.tasks_dir}")
            return tasks
        
        for task_dir in sorted(self.tasks_dir.iterdir()):
            if task_dir.is_dir() and task_dir.name.startswith("task_"):
                try:
                    task = Task(task_dir)
                    tasks.append(task)
                except Exception as e:
                    logger.error(f"Error loading task {task_dir.name}: {e}")
        
        logger.info(f"Loaded {len(tasks)} tasks")
        return tasks
    
    def get_task_ids(self) -> List[str]:
        """
        Get list of all task IDs.
        
        Returns:
            List of task IDs
        """
        if not self.tasks_dir.exists():
            return []
        
        task_ids = [
            d.name for d in sorted(self.tasks_dir.iterdir())
            if d.is_dir() and d.name.startswith("task_")
        ]
        
        return task_ids
