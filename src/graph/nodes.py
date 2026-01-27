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
    
    For C1 architecture: Always uses tier L (no adaptive routing).
    For other architectures: On test failure, escalates S -> M -> L.
    """
    from src.agents.llm import get_architecture, Architecture
    
    arch = get_architecture()
    
    # C1 architecture: Always use L tier (bypass adaptive routing)
    if arch == Architecture.C1:
        state["developer_tier"] = "L"
        state["story_points_current"] = 8
        return state
    
    # Normal adaptive routing for B/C
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
    On retry, receives both failure_history (test errors) and reviewer_feedback.
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
        test_passed=state["test_passed"],
        reviewer_feedback=state["reviewer_feedback"] or ""
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
    Reviewer node: reviews code after testing and provides feedback.
    
    Placed after tester, the reviewer analyzes the generated code along with
    test results to provide actionable feedback for the next iteration.
    Does NOT generate any code - only provides feedback on the task.
    """
    code = state["generated_code"]
    task_description = state["task_description"]
    test_passed = state["test_passed"]
    failure_history = state["failure_history"]
    
    llm_client = get_llm_client()
    response = llm_client.reviewer(
        code=code,
        task_description=task_description,
        test_passed=test_passed,
        failure_history="\n".join(failure_history)
    )
    
    # Only save feedback - reviewer does not generate code
    state["reviewer_feedback"] = response.feedback
    
    return state


def tester_node(state: GraphState) -> GraphState:
    """
    Tester node: executes generated code with HumanEval assertion tests.
    
    This is pure Python logic, not an LLM call.
    Combines the generated code with test assertions and runs them.
    """
    code = state["generated_code"]
    test_code = state["test_code"]
    entry_point = state["entry_point"]
    
    if not code:
        state["test_passed"] = False
        state["failure_history"].append("No code to test")
        return state
    
    if not test_code:
        # No tests to run, assume passed
        state["test_passed"] = True
        return state
    
    # Combine generated code with test assertions
    full_code = f"{code}\n\n{test_code}\n\ncheck({entry_point})"
    
    success, error = _execute_code_with_tests(full_code)
    
    state["test_passed"] = success
    if not success:
        # Truncate error message to avoid context explosion
        safe_error = (error[:1500] + "... [truncated]") if len(error) > 1500 else error
        state["failure_history"].append(f"Test failed: {safe_error}")
    
    return state


def _execute_code_with_tests(code: str, timeout: int = 10) -> tuple[bool, str]:
    """
    Execute Python code containing function and assertion tests.
    
    Args:
        code: Complete Python code with function definition and test assertions
        timeout: Maximum execution time in seconds
        
    Returns:
        (success, error_message)
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
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode != 0:
            # Combine stderr and stdout for error info
            error_msg = result.stderr or result.stdout or "Unknown error"
            return False, error_msg
        
        return True, ""
        
    except subprocess.TimeoutExpired:
        return False, f"Timeout after {timeout} seconds"
    except Exception as e:
        return False, str(e)
    finally:
        # Clean up temp file
        try:
            os.unlink(temp_path)
        except:
            pass

