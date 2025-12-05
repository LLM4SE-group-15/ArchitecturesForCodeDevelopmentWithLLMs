"""
Task Addition Helper Script

Interactive script to help add new tasks to the dataset.
"""

import json
from pathlib import Path


def create_task_directory(task_id: str, base_dir: Path = Path("tasks")):
    """Create directory structure for a new task."""
    pass


def interactive_task_creation():
    """Interactively create a new task."""
    print("=== Add New Programming Task ===\n")
    
    # Get task details
    task_id = input("Task ID (e.g., 002): ")
    title = input("Task title: ")
    difficulty = input("Difficulty (easy/medium/hard): ")
    
    # TODO: Create files
    # TODO: Prompt for description, reference solution, test cases
    
    print(f"\nTask {task_id} created successfully!")


if __name__ == "__main__":
    interactive_task_creation()
