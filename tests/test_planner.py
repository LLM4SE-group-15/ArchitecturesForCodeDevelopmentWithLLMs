import pytest
from src.graph.graph import build_graph, run_graph
from src.graph.state import create_initial_state
from src.data.task_loader import HumanEvalTaskLoader


# Sample HumanEval-style task for testing
SAMPLE_PROMPT = '''from typing import List


def has_close_elements(numbers: List[float], threshold: float) -> bool:
    """ Check if in given list of numbers, are any two numbers closer to each other than
    given threshold.
    >>> has_close_elements([1.0, 2.0, 3.0], 0.5)
    False
    >>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)
    True
    """
'''

SAMPLE_TEST = '''
def check(candidate):
    assert candidate([1.0, 2.0, 3.0], 0.5) == False
    assert candidate([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3) == True
    assert candidate([1.0, 2.0, 3.9, 4.0, 5.0, 2.2], 0.3) == True
    assert candidate([1.0, 2.0, 3.9, 4.0, 5.0, 2.2], 0.05) == False
    assert candidate([1.0, 2.0, 5.9, 4.0, 5.0], 0.95) == True
    assert candidate([1.0, 2.0, 5.9, 4.0, 5.0], 0.8) == False
    assert candidate([1.0, 2.0, 3.0, 4.0, 5.0, 2.0], 0.1) == True
'''


def test_planner_returns_valid_story_points():
    """Test that the Planner returns a valid story point value."""
    initial_state = create_initial_state(
        task_id="HumanEval/0",
        task_description=SAMPLE_PROMPT,
        test_code=SAMPLE_TEST,
        entry_point="has_close_elements"
    )
    
    graph = build_graph()
    result = graph.invoke(initial_state)
    
    # Verify plan exists
    assert result["plan"] is not None, "Plan should not be None"
    
    # Verify story points is valid
    assert result["plan"]["story_points"] in [1, 2, 3, 5, 8], (
        f"Story points {result['plan']['story_points']} not in valid set"
    )
    
    # Verify rationale exists
    assert len(result["plan"]["rationale"]) > 0, "Rationale should not be empty"
    
    # Verify story points are tracked
    assert result["story_points_initial"] == result["plan"]["story_points"]
    assert result["story_points_current"] == result["plan"]["story_points"]
    
    print(f"\n Story Points: {result['plan']['story_points']}")
    print(f" Rationale: {result['plan']['rationale'][:200]}...")


def test_humaneval_loader():
    """Test that HumanEval loader works correctly."""
    loader = HumanEvalTaskLoader()
    
    # Test loading by index
    task = loader.get_task_by_index(0)
    assert task is not None, "Should load task at index 0"
    assert task.task_id == "HumanEval/0", f"Expected HumanEval/0, got {task.task_id}"
    assert len(task.prompt) > 0, "Prompt should not be empty"
    assert len(task.test) > 0, "Test should not be empty"
    assert len(task.entry_point) > 0, "Entry point should not be empty"
    
    print(f"\n Loaded task: {task.task_id}")
    print(f" Entry point: {task.entry_point}")
    print(f" Prompt length: {len(task.prompt)} chars")


def test_load_multiple_tasks():
    """Test loading multiple tasks."""
    loader = HumanEvalTaskLoader()
    tasks = loader.load_tasks(limit=5)
    
    assert len(tasks) == 5, f"Expected 5 tasks, got {len(tasks)}"
    
    for task in tasks:
        assert task.task_id.startswith("HumanEval/")
        assert len(task.prompt) > 0
        assert len(task.test) > 0
    
    print(f"\n Loaded {len(tasks)} tasks")
    for t in tasks:
        print(f"   - {t.task_id}: {t.entry_point}")


if __name__ == "__main__":
    print("Running HumanEval tests...")
    test_humaneval_loader()
    test_load_multiple_tasks()
    # test_planner_returns_valid_story_points()  # Requires API call
    print("\n All tests passed!")
