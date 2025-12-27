from typing import Literal

MODELS = {
    "planner": "meta-llama/Llama-3.1-8B-Instruct",
    "developer_s": "Qwen/Qwen2.5-Coder-1.5B-Instruct",
    "developer_m": "Qwen/Qwen2.5-Coder-7B-Instruct", 
    "developer_l": "deepseek-ai/DeepSeek-Coder-V2-Instruct",
}

DIFFICULTY_CATEGORIES: dict[Literal[1, 2, 3, 5, 8], Literal["S", "M", "L"]] = {
    1: "S",  
    2: "S",  
    3: "M",  
    5: "M",  
    8: "L", 
}


def get_developer_tier(story_points: Literal[1, 2, 3, 5, 8]) -> Literal["S", "M", "L"]:
    return DIFFICULTY_CATEGORIES[story_points]


def get_model_for_role(role: str) -> str:
    return MODELS.get(role, MODELS["developer_m"])


class NodeNames:
    PLANNER = "planner"
    ROUTER = "router"
    DEVELOPER_S = "developer_s"
    DEVELOPER_M = "developer_m"
    DEVELOPER_L = "developer_l"
