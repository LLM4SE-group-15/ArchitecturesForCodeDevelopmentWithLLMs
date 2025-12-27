from src.graph.state import GraphState, PlanOutput
from src.agents.client import llm_client
from src.graph.config import get_developer_tier


def planner_node(state: GraphState) -> GraphState:
    """
    Planner node: assigns story points to the task.
    
    Uses Llama 3.1-8B-Instruct to evaluate task difficulty
    and assign Scrum-style story points (1-2-3-5-8).
    
    Args:
        state: Current graph state with task_id and task_description
        
    Returns:
        Updated state fields: plan, story_points_initial, story_points_current
    """
    task_id = state["task_id"]
    task_description = state["task_description"]
    
    response = llm_client.planner(task_description, task_id)
    
    plan: PlanOutput = {
        "id": response.id,
        "description": task_description,
        "story_points": response.story_points,
        "rationale": response.rationale
    }

    state["plan"] = plan
    state["story_points_initial"] = response.story_points
    state["story_points_current"] = response.story_points
    state["developer_tier"] = get_developer_tier(response.story_points)
    
    return state

def router_node(state: GraphState) -> GraphState:
    """
    Router node: routes the task to the appropriate developer.
    
    Args:
        state: Current graph state with story_points_current
        
    Returns:
        Updated state fields: developer_tier
    """
    if not state["test_passed"]:
        developer_tier = state["developer_tier"]

        if developer_tier == "S":
            state["developer_tier"] = "M"
        elif developer_tier == "M":
            state["developer_tier"] = "L"

    return state

def developer_node(state: GraphState) -> GraphState:
    """
    Developer node: generates code for the task.
    
    Uses Qwen 2.5-Coder-7B-Instruct to generate code for the task.
    
    Args:
        state: Current graph state with plan and story_points_current
        
    Returns:
        Updated state fields: generated_code, developer_tier
    """

