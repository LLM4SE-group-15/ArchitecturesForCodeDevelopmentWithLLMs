from langgraph.graph import StateGraph, START, END

from src.graph.state import GraphState
from src.graph.config import NodeNames
from src.graph.nodes import planner_node


def build_graph() -> StateGraph:

    graph = StateGraph(GraphState)
    
    graph.add_node(NodeNames.PLANNER, planner_node)
    
    graph.add_edge(START, NodeNames.PLANNER)
    graph.add_edge(NodeNames.PLANNER, END)
    
    return graph.compile()


def create_initial_state(task_id: str, task_description: str) -> GraphState:
    return GraphState(
        task_id=task_id,
        task_description=task_description,
        plan=None,
        story_points_initial=None,
        story_points_current=None,
        escalations=0,
        failure_history=[],
        developer_tier=None,
        generated_code=None,
        review_feedback=None,
        test_passed=None,
        test_output=None,
    )

graph = build_graph()
