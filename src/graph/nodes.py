from src.graph.state import GraphState, PlanOutput
from src.agents.client import get_llm_client
from src.graph.config import get_developer_tier


def planner_node(state: GraphState) -> GraphState:
    """
    Planner node: assigns story points to the task.
    
    Uses a model to evaluate task difficulty
    and assign Scrum-style story points (1-2-3-5-8).
    """
    task_id = state["task_id"]
    task_description = state["task_description"]
    
    llm_client = get_llm_client()
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
    
    On test failure, escalates to a higher tier developer (S -> M -> L).
    """
    if not state["test_passed"]:
        developer_tier = state["developer_tier"]
        state["escalations"] += 1

        if developer_tier == "S":
            state["developer_tier"] = "M" 
            state["story_points_current"] = 3
        elif developer_tier == "M":
            state["developer_tier"] = "L"
            state["story_points_current"] = 8

    return state


def developer_node(state: GraphState) -> GraphState:
    """
    Developer node: generates code for the task.
    
    Uses the appropriate tier model based on story points and escalation.
    """
    plan = state["plan"]
    developer_tier = state["developer_tier"]
    
    llm_client = get_llm_client()
    response = llm_client.developer(
        plan_description=plan["description"],
        story_points=state["story_points_current"],
        developer_tier=developer_tier,
        failure_history="\n".join(state["failure_history"]),
        generated_code=state["generated_code"] or "",
        task_id=plan["id"],
        test_passed=state["test_passed"]
    )
    
    state["generated_code"] = response.generated_code
    
    return state


def single_agent_node(state: GraphState) -> GraphState:
    """
    Single-agent node: generates code in one call without planning/routing.
    
    Used only for Architecture A (single-agent baseline).
    """
    llm_client = get_llm_client()
    response = llm_client.single_agent(state["task_description"])
    
    state["generated_code"] = response.generated_code
    
    return state
