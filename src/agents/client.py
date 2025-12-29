import os
from typing import Type, TypeVar
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.messages import HumanMessage, SystemMessage
from src.models.llm_responses import PlannerResponse, DeveloperResponse, ReviewerResponse
from src.models.prompts import (
    PLANNER_SYSTEM_PROMPT,
    PLANNER_USER_PROMPT_TEMPLATE,
    DEVELOPER_FIRST_PROMPT,
    DEVELOPER_AFTER_FAILURE,
    SINGLE_AGENT_PROMPT,
    REVIEWER_SYSTEM_PROMPT,
    REVIEWER_USER_PROMPT,
)
from src.agents.llm import Architecture, get_architecture, get_models

load_dotenv()

T = TypeVar("T", bound=BaseModel)


class LLMClient:
    """
    LLM Client class for interacting with language models.
    
    Supports architecture-aware model selection for A/B/C experimental setups.
    """
    
    def __init__(self, architecture: Architecture = None):
        self.hf_token = os.getenv("HF_TOKEN")
        self.architecture = architecture or get_architecture()
        self.models = get_models(self.architecture)
    
    def _get_llm(self, model_name: str, temperature: float = 0.0) -> ChatHuggingFace:
        """Get a configured LLM client for the specified model."""
        llm = HuggingFaceEndpoint(
            repo_id=model_name,
            task="text-generation",
            temperature=temperature,
            huggingfacehub_api_token=self.hf_token,
            max_new_tokens=2048,
        )
        return ChatHuggingFace(llm=llm)
    
    def invoke_with_structured_output(
        self,
        model_name: str,
        messages: list[dict],
        response_model: Type[T],
        temperature: float = 0.0
    ) -> T:
        """
        Invoke a model with structured output based on a Pydantic model.
        
        Args:
            model_name: HuggingFace model repository ID
            messages: List of message dicts with 'role' and 'content' keys
            response_model: Pydantic model class for structured output
            temperature: Sampling temperature
            
        Returns:
            Structured response matching the response_model type
        """
        llm = self._get_llm(model_name, temperature)
        
        lc_messages = []
        for msg in messages:
            if msg["role"] == "system":
                lc_messages.append(SystemMessage(content=msg["content"]))
            elif msg["role"] == "user":
                lc_messages.append(HumanMessage(content=msg["content"]))
        
        structured_llm = llm.with_structured_output(response_model)
        return structured_llm.invoke(lc_messages)
    
    def planner(self, task_description: str, task_id: str) -> PlannerResponse:
        """
        Plan a coding task by assigning story points.
        
        Uses configured planner model to evaluate task difficulty
        and assign Scrum-style story points (1-2-3-5-8).
        """
        user_prompt = PLANNER_USER_PROMPT_TEMPLATE.format(
            task_id=task_id,
            task_description=task_description
        )
        
        messages = [
            {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]
        
        return self.invoke_with_structured_output(
            model_name=self.models["planner"],
            messages=messages,
            response_model=PlannerResponse,
            temperature=0.0
        )
    
    def developer(
        self,
        plan_description: str,
        story_points: int,
        developer_tier: str,
        failure_history: str,
        generated_code: str,
        task_id: str,
        test_passed: bool
    ) -> DeveloperResponse:
        """
        Generate code for a given plan using the appropriate developer model.
        """
        if test_passed:
            prompt = DEVELOPER_FIRST_PROMPT.format(
                story_points=story_points,
                task_description=plan_description
            )
        else:
            prompt = DEVELOPER_AFTER_FAILURE.format(
                story_points=story_points,
                task_description=plan_description,
                generated_code=generated_code,
                failure_history=failure_history
            )
        
        messages = [
            {"role": "system", "content": f"You are a {developer_tier} tier developer."},
            {"role": "user", "content": prompt}
        ]
        
        return self.invoke_with_structured_output(
            model_name=self.models["developer_" + developer_tier.lower()],
            messages=messages,
            response_model=DeveloperResponse,
            temperature=0.0
        )
    
    def single_agent(self, task_description: str) -> DeveloperResponse:
        """
        Single-agent baseline: generate code in one call without planning/routing.
        
        Used only for Architecture A.
        """
        prompt = SINGLE_AGENT_PROMPT.format(task_description=task_description)
        
        messages = [
            {"role": "system", "content": "You are an expert Python developer."},
            {"role": "user", "content": prompt}
        ]
        
        return self.invoke_with_structured_output(
            model_name=self.models["baseline"],
            messages=messages,
            response_model=DeveloperResponse,
            temperature=0.0
        )
    
    def reviewer(self, code: str, task_description: str) -> ReviewerResponse:
        """
        Review generated code and provide feedback with improvements.
        
        Uses configured reviewer model to analyze code for bugs,
        edge cases, and style issues.
        """
        user_prompt = REVIEWER_USER_PROMPT.format(
            task_description=task_description,
            code=code
        )
        
        messages = [
            {"role": "system", "content": REVIEWER_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]
        
        return self.invoke_with_structured_output(
            model_name=self.models["reviewer"],
            messages=messages,
            response_model=ReviewerResponse,
            temperature=0.0
        )


def get_llm_client(architecture: Architecture = None) -> LLMClient:
    """Factory function to get LLMClient with specified architecture."""
    return LLMClient(architecture)