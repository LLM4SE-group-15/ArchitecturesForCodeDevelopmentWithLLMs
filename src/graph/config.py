from typing import Literal, Optional

DIFFICULTY_CATEGORIES: dict[Literal[1, 2, 3, 5, 8], Literal["S", "M", "L"]] = {
    1: "S",  
    2: "S",  
    3: "M",  
    5: "M",  
    8: "L", 
}

def get_developer_tier(
    story_points: Literal[1, 2, 3, 5, 8],
    architecture: Optional[str] = None
) -> Literal["S", "M", "L"]:
    """Get developer tier based on story points.
    
    For Architecture C2 (ablation without S model):
    Maps S tier -> M tier, so tasks start directly from M.
    """
    tier = DIFFICULTY_CATEGORIES[story_points]
    
    # C2 ablation: skip S tier entirely, start from M
    if architecture == "C2" and tier == "S":
        return "M"
    
    return tier


class NodeNames:
    PLANNER = "planner"
    ROUTER = "router"
    DEVELOPER = "developer"
    REVIEWER = "reviewer"
    TESTER = "tester"
    SINGLE_AGENT = "single_agent"
