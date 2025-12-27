from langgraph.graph import StateGraph, START, END

from src.graph.state import GraphState, create_initial_state
from src.graph.config import NodeNames
from src.graph.nodes import (
    planner_node,
    router_node,
    developer_node,
)


def build_graph() -> StateGraph:

    graph = StateGraph(GraphState)
    
    graph.add_node(NodeNames.PLANNER, planner_node)
    graph.add_node(NodeNames.ROUTER, router_node)
    graph.add_node(NodeNames.DEVELOPER, developer_node)
    
    graph.add_edge(START, NodeNames.PLANNER)
    graph.add_edge(NodeNames.PLANNER, NodeNames.ROUTER)
    graph.add_edge(NodeNames.ROUTER, NodeNames.DEVELOPER)
    graph.add_edge(NodeNames.DEVELOPER, END)
    
    return graph.compile()


def run_graph(task_id: str, task_description: str):
    graph = build_graph()
    
    initial_state = create_initial_state(task_id, task_description)

    compiled_graph = graph.compile()

    return compiled_graph.invoke(initial_state)
