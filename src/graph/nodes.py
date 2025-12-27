from src.graph.state import GraphState, PlanOutput
from src.graph.config import MODELS
from src.models.prompts import PLANNER_SYSTEM_PROMPT, PLANNER_USER_PROMPT_TEMPLATE
from src.models.llm_responses import PlannerResponse
from src.agents.client import invoke_with_structured_output


def planner_node(state: GraphState) -> dict:
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
    
    user_prompt = PLANNER_USER_PROMPT_TEMPLATE.format(
        task_id=task_id,
        task_description=task_description
    )
    
    messages = [
        {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]
    
    response: PlannerResponse = invoke_with_structured_output(
        model_name=MODELS["planner"],
        messages=messages,
        response_model=PlannerResponse,
        temperature=0.0
    )
    
    plan: PlanOutput = {
        "id": response.id,
        "description": task_description,
        "story_points": response.story_points,
        "rationale": response.rationale
    }
    
    return {
        "plan": plan,
        "story_points_initial": response.story_points,
        "story_points_current": response.story_points,
    }
