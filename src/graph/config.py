from typing import Literal

DIFFICULTY_CATEGORIES: dict[Literal[1, 2, 3, 5, 8], Literal["S", "M", "L"]] = {
    1: "S",  
    2: "S",  
    3: "M",  
    5: "M",  
    8: "L", 
}

def get_developer_tier(story_points: Literal[1, 2, 3, 5, 8]) -> Literal["S", "M", "L"]:
    return DIFFICULTY_CATEGORIES[story_points]

class NodeNames:
    PLANNER = "planner"
    ROUTER = "router"
    DEVELOPER = "developer"
    REVIEWER = "reviewer"
    TESTER = "tester"
    SINGLE_AGENT = "single_agent"
