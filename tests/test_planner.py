import pytest
from src.graph.graph import graph, create_initial_state


SAMPLE_TASK = """
Write a function that takes a list of integers and returns the sum of all even numbers.
If the list is empty or contains no even numbers, return 0.

Examples:
    sum_evens([1, 2, 3, 4, 5, 6]) → 12
    sum_evens([1, 3, 5, 7]) → 0
    sum_evens([]) → 0
"""

COMPLEX_TASK = """
Implement a function that finds the longest palindromic substring in a given string.
The function should handle:
- Empty strings (return empty)
- Single characters (return the character)
- Strings with no palindromes longer than 1 char
- Multiple palindromes of same length (return first found)
- Case sensitivity (treat 'A' and 'a' as different)

Examples:
    longest_palindrome("babad") → "bab" or "aba"
    longest_palindrome("cbbd") → "bb"
    longest_palindrome("a") → "a"
    longest_palindrome("") → ""
"""


def test_planner_returns_valid_story_points():
    """Test that the Planner returns a valid story point value."""
    initial_state = create_initial_state(
        task_id="test_001",
        task_description=SAMPLE_TASK
    )
    
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
    
    print(f"\n✓ Story Points: {result['plan']['story_points']}")
    print(f"✓ Rationale: {result['plan']['rationale'][:200]}...")


def test_planner_complex_task():
    """Test that the Planner assigns appropriate story points to a complex task."""
    initial_state = create_initial_state(
        task_id="test_002",
        task_description=COMPLEX_TASK
    )
    
    result = graph.invoke(initial_state)
    
    assert result["plan"]["story_points"] >= 3, (
        f"Complex task should have story points >= 3, got {result['plan']['story_points']}"
    )
    
    print(f"\n✓ Story Points: {result['plan']['story_points']}")
    print(f"✓ Rationale: {result['plan']['rationale']}")


if __name__ == "__main__":
    print("Running Planner agent tests...")
    test_planner_returns_valid_story_points()
    test_planner_complex_task()
    print("\n✓ All tests passed!")
