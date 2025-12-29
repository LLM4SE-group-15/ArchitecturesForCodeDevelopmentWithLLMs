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
    - Test execution data (inputs, outputs, results)
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
    reviewed_code: Optional[str]  # Output from Reviewer (future)
    
    # Test execution (for Tester node)
    test_inputs: list[str]       # stdin inputs for each test case
    test_outputs: list[str]      # expected stdout for each test case
    test_passed: bool            # Whether all tests passed
    failure_history: list[str]   # Error messages from failed tests


def create_initial_state(
    task_id: str,
    task_description: str,
    test_inputs: list[str] = None,
    test_outputs: list[str] = None
) -> GraphState:
    """
    Create the initial state for a graph execution.
    
    Args:
        task_id: Unique identifier for the task
        task_description: Natural language description of the coding problem
        test_inputs: List of stdin inputs for test cases
        test_outputs: List of expected stdout outputs for test cases
        
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
        reviewed_code=None,
        test_inputs=test_inputs or [],
        test_outputs=test_outputs or [],
        test_passed=True,
        failure_history=[],
    )