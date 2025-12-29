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


def reviewer_node(state: GraphState) -> GraphState:
    """
    Reviewer node: reviews generated code and provides improvements.
    
    Uses LLM to analyze code for bugs, edge cases, and style issues.
    """
    code = state["generated_code"]
    task_description = state["task_description"]
    
    llm_client = get_llm_client()
    response = llm_client.reviewer(code, task_description)
    
    state["reviewed_code"] = response.reviewed_code
    state["reviewer_feedback"] = response.feedback
    
    return state


def tester_node(state: GraphState) -> GraphState:
    """
    Tester node: executes code with test inputs and validates outputs.
    
    This is pure Python logic, not an LLM call.
    Uses reviewed_code if available, otherwise generated_code.
    """
    import subprocess
    import tempfile
    import os
    
    # Use reviewed code if available, otherwise use generated code
    code = state["reviewed_code"] or state["generated_code"]
    test_inputs = state["test_inputs"]
    test_outputs = state["test_outputs"]
    
    if not code:
        state["test_passed"] = False
        state["failure_history"].append("No code to test")
        return state
    
    if not test_inputs or not test_outputs:
        # No tests to run, assume passed
        state["test_passed"] = True
        return state
    
    all_passed = True
    errors = []
    
    for i, (test_input, expected_output) in enumerate(zip(test_inputs, test_outputs)):
        success, actual_output, error = _execute_code(code, test_input)
        
        if not success:
            all_passed = False
            errors.append(f"Test {i+1}: Execution error - {error}")
            continue
        
        # Normalize outputs for comparison (strip whitespace)
        actual_normalized = actual_output.strip()
        expected_normalized = expected_output.strip()
        
        if actual_normalized != expected_normalized:
            all_passed = False
            errors.append(
                f"Test {i+1}: Expected '{expected_normalized}', got '{actual_normalized}'"
            )
    
    state["test_passed"] = all_passed
    if errors:
        state["failure_history"].extend(errors)
    
    return state


def _execute_code(code: str, stdin_input: str, timeout: int = 10) -> tuple[bool, str, str]:
    """
    Execute Python code with given stdin input.
    
    Returns:
        (success, stdout, error_message)
    """
    import subprocess
    import tempfile
    import os
    
    # Write code to temporary file
    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.py',
        delete=False,
        encoding='utf-8'
    ) as f:
        f.write(code)
        temp_path = f.name
    
    try:
        result = subprocess.run(
            ['python', temp_path],
            input=stdin_input,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode != 0:
            return False, "", result.stderr
        
        return True, result.stdout, ""
        
    except subprocess.TimeoutExpired:
        return False, "", f"Timeout after {timeout} seconds"
    except Exception as e:
        return False, "", str(e)
    finally:
        # Clean up temp file
        try:
            os.unlink(temp_path)
        except:
            pass
