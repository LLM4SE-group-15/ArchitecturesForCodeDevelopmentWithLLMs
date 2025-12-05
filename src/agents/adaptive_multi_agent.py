"""
Adaptive Multi-Agent System (AMAS)

This module implements an adaptive multi-agent architecture that dynamically
allocates development resources (1-3 developers) based on task complexity.

Architecture:
1. Planner: Analyzes task, decomposes into subtasks, assigns difficulty scores
2. Dynamic Allocator: Decides team size based on difficulty (solo/pair/team)
3. Developers: Implement subtasks (collaborative when multiple)
4. Integrator: Merges multiple solutions
5. Reviewer: Code quality assurance
6. Tester: Validation and retry logic
"""

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from typing import Dict, Any, TypedDict, List, Literal
import time

from src.utils.config import Config
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class SubtaskResult(TypedDict):
    """Result from processing a single subtask."""
    subtask_id: str
    description: str
    difficulty: float
    team_size: int
    mode: str
    code: str
    execution_time: float


class AdaptiveState(TypedDict):
    """State shared between agents in the adaptive workflow."""
    # Input
    task_description: str
    
    # Planning phase
    plan: Dict[str, Any]  # Contains subtasks with difficulty scores
    
    # Execution phase
    current_subtask_index: int
    subtask_results: List[SubtaskResult]
    
    # Integration phase
    integrated_code: str
    
    # Review phase
    reviewed_code: str
    review_feedback: str
    
    # Testing phase
    test_results: Dict[str, Any]
    
    # Control flow
    iterations: int
    max_iterations: int
    status: str  # "planning" | "executing" | "reviewing" | "testing" | "done" | "failed"
    
    # Metadata
    total_execution_time: float
    total_tokens: int


class AdaptiveMultiAgentSystem:
    """Adaptive multi-agent code generation system using LangGraph."""
    
    def __init__(self, model_name: str = None, temperature: float = None):
        """Initialize the adaptive multi-agent system."""
        self.model_name = model_name or Config.MODEL_NAME
        self.temperature = temperature if temperature is not None else Config.TEMPERATURE
        
        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            max_tokens=Config.MAX_TOKENS
        )
        
        self.graph = self._build_graph()
        
        logger.info(f"AdaptiveMultiAgentSystem initialized with model={self.model_name}")
    
    def _planner_node(self, state: AdaptiveState) -> AdaptiveState:
        """
        Planner agent: Analyzes task, decomposes into subtasks, assigns difficulty scores.
        
        Returns:
            Updated state with plan containing subtasks and difficulty scores
        """
        logger.info("Planner: Analyzing task and creating plan")
        # TODO: Implement planner logic
        pass
    
    def _allocate_team(self, difficulty: float) -> Dict[str, Any]:
        """
        Decide team configuration based on difficulty score.
        
        Args:
            difficulty: Difficulty score (0.0-1.0)
            
        Returns:
            Team configuration with size and mode
        """
        if difficulty < 0.3:
            return {"team_size": 1, "mode": "solo"}
        elif difficulty < 0.7:
            return {"team_size": 2, "mode": "pair"}
        else:
            return {"team_size": 3, "mode": "team"}
    
    def _execute_subtask_node(self, state: AdaptiveState) -> AdaptiveState:
        """
        Execute current subtask with appropriate team allocation.
        
        Routes to solo/pair/team execution based on difficulty.
        """
        logger.info("Executing subtask with adaptive team allocation")
        # TODO: Implement subtask execution logic
        pass
    
    def _solo_developer_node(self, state: AdaptiveState) -> AdaptiveState:
        """Single developer implements the subtask."""
        logger.info("Solo developer mode")
        # TODO: Implement solo development
        pass
    
    def _pair_developers_node(self, state: AdaptiveState) -> AdaptiveState:
        """Two developers collaborate on the subtask."""
        logger.info("Pair developers mode")
        # TODO: Implement pair collaboration
        pass
    
    def _team_developers_node(self, state: AdaptiveState) -> AdaptiveState:
        """Three developers work on different aspects, then integrate."""
        logger.info("Team developers mode")
        # TODO: Implement team collaboration
        pass
    
    def _integrator_node(self, state: AdaptiveState) -> AdaptiveState:
        """
        Integrator agent: Combines all subtask solutions into coherent code.
        """
        logger.info("Integrator: Merging subtask solutions")
        # TODO: Implement integration logic
        pass
    
    def _reviewer_node(self, state: AdaptiveState) -> AdaptiveState:
        """
        Reviewer agent: Code quality review and refactoring suggestions.
        """
        logger.info("Reviewer: Analyzing code quality")
        # TODO: Implement review logic
        pass
    
    def _tester_node(self, state: AdaptiveState) -> AdaptiveState:
        """
        Tester agent: Validates code against requirements.
        """
        logger.info("Tester: Validating code")
        # TODO: Implement testing logic
        pass
    
    def _route_subtask_execution(self, state: AdaptiveState) -> str:
        """Route to appropriate execution mode based on current subtask difficulty."""
        current_idx = state.get("current_subtask_index", 0)
        subtasks = state["plan"]["subtasks"]
        
        if current_idx >= len(subtasks):
            return "integrate"
        
        difficulty = subtasks[current_idx]["difficulty"]
        team_config = self._allocate_team(difficulty)
        
        mode_routing = {
            "solo": "solo_dev",
            "pair": "pair_dev",
            "team": "team_dev"
        }
        
        return mode_routing[team_config["mode"]]
    
    def _should_retry(self, state: AdaptiveState) -> str:
        """Decide whether to retry or finish based on test results."""
        if state["test_results"].get("passed", False):
            return "done"
        elif state["iterations"] >= state["max_iterations"]:
            return "failed"
        else:
            return "retry"
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(AdaptiveState)
        
        # Add nodes
        workflow.add_node("planner", self._planner_node)
        workflow.add_node("execute_subtask", self._execute_subtask_node)
        workflow.add_node("solo_dev", self._solo_developer_node)
        workflow.add_node("pair_dev", self._pair_developers_node)
        workflow.add_node("team_dev", self._team_developers_node)
        workflow.add_node("integrator", self._integrator_node)
        workflow.add_node("reviewer", self._reviewer_node)
        workflow.add_node("tester", self._tester_node)
        
        # Set entry point
        workflow.set_entry_point("planner")
        
        # Add edges
        workflow.add_edge("planner", "execute_subtask")
        
        # Conditional routing based on difficulty
        workflow.add_conditional_edges(
            "execute_subtask",
            self._route_subtask_execution,
            {
                "solo_dev": "solo_dev",
                "pair_dev": "pair_dev",
                "team_dev": "team_dev",
                "integrate": "integrator"
            }
        )
        
        # All execution modes loop back to execute next subtask
        workflow.add_edge("solo_dev", "execute_subtask")
        workflow.add_edge("pair_dev", "execute_subtask")
        workflow.add_edge("team_dev", "execute_subtask")
        
        # Integration -> Review -> Test
        workflow.add_edge("integrator", "reviewer")
        workflow.add_edge("reviewer", "tester")
        
        # Conditional end or retry
        workflow.add_conditional_edges(
            "tester",
            self._should_retry,
            {
                "done": END,
                "failed": END,
                "retry": "planner"
            }
        )
        
        return workflow.compile()
    
    def generate_code(self, task_description: str) -> Dict[str, Any]:
        """
        Generate code solution using adaptive multi-agent workflow.
        
        Args:
            task_description: Natural language description of the programming task
            
        Returns:
            Dictionary containing generated code and metadata
        """
        logger.info("Starting adaptive multi-agent code generation")
        start_time = time.time()
        
        # Initialize state
        initial_state: AdaptiveState = {
            "task_description": task_description,
            "plan": {},
            "current_subtask_index": 0,
            "subtask_results": [],
            "integrated_code": "",
            "reviewed_code": "",
            "review_feedback": "",
            "test_results": {},
            "iterations": 0,
            "max_iterations": 3,
            "status": "planning",
            "total_execution_time": 0.0,
            "total_tokens": 0
        }
        
        try:
            # Execute workflow
            final_state = self.graph.invoke(initial_state)
            
            execution_time = time.time() - start_time
            
            result = {
                "code": final_state.get("reviewed_code", ""),
                "plan": final_state.get("plan", {}),
                "subtask_results": final_state.get("subtask_results", []),
                "iterations": final_state.get("iterations", 0),
                "status": final_state.get("status", "unknown"),
                "execution_time": execution_time,
                "model": self.model_name,
                "architecture": "adaptive-multi-agent"
            }
            
            logger.info(f"Code generated successfully in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Error in adaptive multi-agent generation: {str(e)}")
            raise
