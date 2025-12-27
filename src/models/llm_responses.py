from typing import Literal
from pydantic import BaseModel, Field


class PlannerResponse(BaseModel):
    id: str = Field(
        description="Task identifier"
    )
    
    story_points: Literal[1, 2, 3, 5, 8] = Field(
        description=(
            "Difficulty estimate using Fibonacci scale: "
            "1=trivial, 2=small, 3=medium, 5=challenging, 8=hard"
        )
    )
    
    rationale: str = Field(
        description=(
            "Justification for the story point assignment. "
            "Must explain why this value fits AND why the closest lower value is insufficient."
        )
    )
