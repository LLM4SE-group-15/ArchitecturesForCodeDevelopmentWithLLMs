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
    failure_history: list[str]
    
    developer_tier: Optional[Literal["S", "M", "L"]]
    
    generated_code: Optional[str]
