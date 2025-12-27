from typing import TypedDict, Optional, Literal


class PlanOutput(TypedDict):
    id: str
    description: str
    story_points: Literal[1, 2, 3, 5, 8]
    rationale: str


class GraphState(TypedDict):

    task_id: str
    task_description: str
    
    plan: Optional[PlanOutput]
    
    story_points_initial: Optional[Literal[1, 2, 3, 5, 8]]
    story_points_current: Optional[Literal[1, 2, 3, 5, 8]]
    
    escalations: int
    test_passed: bool
    failure_history: list[str]

    review_feedback: Optional[str] # Da riempire con il risultato del tester (eventuali errori)
    
    developer_tier: Optional[Literal["S", "M", "L"]]
    
    generated_code: Optional[str]


def create_initial_state(task_id: str, task_description: str) -> GraphState:
    return GraphState(
        task_id=task_id,
        task_description=task_description,
        plan=None,
        story_points_initial=None,
        story_points_current=None,
        escalations=0,
        failure_history=[],
        developer_tier=None,
        generated_code=None,
        review_feedback=None,
        test_passed=True,
    )