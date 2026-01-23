from typing import TypedDict, Optional, Literal


class PlanOutput(TypedDict):
    """Output from the Planner node."""
    id: str
    description: str
    story_points: Literal[1, 2, 3, 5, 8]
    rationale: str


class GraphState(TypedDict):
    """
    State object passed through the LangGraph workflow.
    
    Contains all information needed for task execution including:
    - Task metadata (id, description)
    - Planning output (story points, rationale)
    - Developer routing (tier, escalations)
    - Generated code
    - Test execution data (test code, entry point, results)
    """
    
    # Task metadata
    task_id: str
    task_description: str
    
    # Planner output
    plan: Optional[PlanOutput]
    
    # Story points (difficulty)
    story_points_initial: Optional[Literal[1, 2, 3, 5, 8]]
    story_points_current: Optional[Literal[1, 2, 3, 5, 8]]
    
    # Developer routing
    escalations: int
    developer_tier: Optional[Literal["S", "M", "L"]]
    
    # Generated code
    generated_code: Optional[str]
    reviewer_feedback: Optional[str]  # Feedback from Reviewer
    
    # Test execution (for Tester node) - HumanEval style
    test_code: str                # Assertion-based test code
    entry_point: str              # Function name to test
    test_passed: bool             # Whether all tests passed
    failure_history: list[str]    # Error messages from failed tests


def create_initial_state(
    task_id: str,
    task_description: str,
    test_code: str = "",
    entry_point: str = ""
) -> GraphState:
    """
    Create the initial state for a graph execution.
    
    Args:
        task_id: Unique identifier for the task
        task_description: The prompt describing the coding problem
        test_code: Assertion-based test code from HumanEval
        entry_point: Name of the function to implement
        
    Returns:
        Initialized GraphState ready for workflow execution.
    """
    return GraphState(
        task_id=task_id,
        task_description=task_description,
        plan=None,
        story_points_initial=None,
        story_points_current=None,
        escalations=0,
        developer_tier=None,
        generated_code=None,
        reviewer_feedback=None,
        test_code=test_code,
        entry_point=entry_point,
        test_passed=True,
        failure_history=[],
    )