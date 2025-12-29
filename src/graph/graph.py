from langgraph.graph import StateGraph, START, END

from src.graph.state import GraphState, create_initial_state
from src.graph.config import NodeNames
from src.graph.nodes import (
    planner_node,
    router_node,
    developer_node,
    single_agent_node,
)
from src.agents.llm import Architecture, get_architecture


def build_graph(architecture: Architecture = None) -> StateGraph:
    """
    Build the LangGraph workflow based on the selected architecture.
    
    Args:
        architecture: Architecture enum (A, B, or C). If None, reads from env.
        
    Returns:
        Compiled StateGraph for the specified architecture.
    """
    if architecture is None:
        architecture = get_architecture()
    
    graph = StateGraph(GraphState)
    
    if architecture == Architecture.A:
        # Architecture A: Single-agent baseline
        # Task -> Single Agent -> END
        graph.add_node(NodeNames.SINGLE_AGENT, single_agent_node)
        
        graph.add_edge(START, NodeNames.SINGLE_AGENT)
        graph.add_edge(NodeNames.SINGLE_AGENT, END)
    else:
        # Architecture B/C: Multi-agent pipeline
        # Task -> Planner -> Router -> Developer -> END
        # (Reviewer and Tester to be added later)
        graph.add_node(NodeNames.PLANNER, planner_node)
        graph.add_node(NodeNames.ROUTER, router_node)
        graph.add_node(NodeNames.DEVELOPER, developer_node)
        
        graph.add_edge(START, NodeNames.PLANNER)
        graph.add_edge(NodeNames.PLANNER, NodeNames.ROUTER)
        graph.add_edge(NodeNames.ROUTER, NodeNames.DEVELOPER)
        graph.add_edge(NodeNames.DEVELOPER, END)
    
    return graph.compile()


def run_graph(
    task_id: str,
    task_description: str,
    test_inputs: list[str] = None,
    test_outputs: list[str] = None,
    architecture: Architecture = None
):
    """
    Run the graph workflow for a given task.
    
    Args:
        task_id: Unique identifier for the task
        task_description: Description of the coding task
        test_inputs: List of stdin inputs for test cases
        test_outputs: List of expected stdout outputs for test cases
        architecture: Architecture enum (A, B, or C). If None, reads from env.
        
    Returns:
        Final graph state after execution.
    """
    graph = build_graph(architecture)
    initial_state = create_initial_state(
        task_id=task_id,
        task_description=task_description,
        test_inputs=test_inputs,
        test_outputs=test_outputs
    )
    return graph.invoke(initial_state)

