import json
import os
import re
from typing import TypeVar
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_huggingface import HuggingFaceEndpoint
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
    
    def _get_llm(self, model_name: str, temperature: float = 0.0) -> HuggingFaceEndpoint:
        """Get a configured HF text-generation endpoint for the specified model.

        Important: we deliberately avoid chat-completions APIs here because they
        may route through HuggingFace "Inference Providers" and require extra
        token permissions (leading to 403 errors).
        """
        return HuggingFaceEndpoint(
            repo_id=model_name,
            task="text-generation",
            temperature=temperature,
            huggingfacehub_api_token=self.hf_token,
            max_new_tokens=2048,
            provider="hf-inference",  # Force native HF API to avoid nscale/other provider routing
        )

    @staticmethod
    def _messages_to_prompt(messages: list[dict]) -> str:
        """Convert system/user messages into a single plain prompt.

        We keep the format intentionally simple and provider-agnostic.
        """
        system_parts: list[str] = []
        user_parts: list[str] = []
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")
            if role == "system":
                system_parts.append(content)
            elif role == "user":
                user_parts.append(content)

        system_block = "\n\n".join(system_parts).strip()
        user_block = "\n\n".join(user_parts).strip()

        if system_block and user_block:
            return f"SYSTEM:\n{system_block}\n\nUSER:\n{user_block}\n\nASSISTANT:\n"
        if user_block:
            return f"USER:\n{user_block}\n\nASSISTANT:\n"
        return f"SYSTEM:\n{system_block}\n\nASSISTANT:\n"

    def _invoke_text(self, model_name: str, messages: list[dict], temperature: float = 0.0) -> str:
        llm = self._get_llm(model_name, temperature)
        prompt = self._messages_to_prompt(messages)
        result = llm.invoke(prompt)
        return str(result)

    @staticmethod
    def _extract_first_json_object(text: str) -> dict:
        """Extract the first JSON object from a model response.

        Models may wrap JSON in markdown fences or add pre/post text.
        This parser finds the first top-level JSON object using brace balancing
        while respecting strings and escapes, so it won't get confused by braces
        inside code strings.
        """
        cleaned = text.strip()
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"```\s*$", "", cleaned)

        start = cleaned.find("{")
        if start == -1:
            raise ValueError(f"No JSON object found in model output: {text[:2000]}")

        in_string = False
        escape = False
        depth = 0
        end = None
        for i in range(start, len(cleaned)):
            ch = cleaned[i]
            if in_string:
                if escape:
                    escape = False
                    continue
                if ch == "\\":
                    escape = True
                    continue
                if ch == '"':
                    in_string = False
                continue

            if ch == '"':
                in_string = True
                continue
            if ch == "{":
                depth += 1
                continue
            if ch == "}":
                depth -= 1
                if depth == 0:
                    end = i
                    break

        if end is None:
            raise ValueError(f"Unterminated JSON object in model output: {text[:2000]}")

        payload = cleaned[start : end + 1]
        data = json.loads(payload)

        # Small robustness: allow story_points as string digits
        if isinstance(data, dict) and "story_points" in data and isinstance(data["story_points"], str):
            sp = data["story_points"].strip()
            if sp.isdigit():
                data["story_points"] = int(sp)

        return data
    
    # NOTE:
    # LangChain's `with_structured_output()` typically relies on provider-specific
    # function calling / tool calling. HuggingFace Inference endpoints used here
    # do not support that mechanism, so we do manual parsing instead.
    
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
            {
                "role": "system",
                "content": (
                    "Return ONLY a valid JSON object (no markdown, no code fences, no extra keys). "
                    "Schema: {id: string, story_points: one of [1,2,3,5,8], rationale: string}."
                ),
            },
            {"role": "user", "content": user_prompt},
        ]

        text = self._invoke_text(self.models["planner"], messages, temperature=0.0)
        data = self._extract_first_json_object(text)
        return PlannerResponse.model_validate(data)
    
    def developer(
        self,
        plan_description: str,
        story_points: int,
        developer_tier: str,
        failure_history: str,
        generated_code: str,
        task_id: str,
        test_passed: bool,
        reviewer_feedback: str = ""
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
                failure_history=failure_history,
                reviewer_feedback=reviewer_feedback or "No feedback available."
            )
        
        messages = [
            {"role": "system", "content": f"You are a {developer_tier} tier developer."},
            {
                "role": "system",
                "content": (
                    "Return ONLY a valid JSON object (no markdown, no code fences, no extra keys). "
                    "Schema: {generated_code: string}. "
                    "The string must contain the FULL Python solution."
                ),
            },
            {"role": "user", "content": prompt},
        ]

        text = self._invoke_text(self.models["developer_" + developer_tier.lower()], messages, temperature=0.0)
        try:
            data = self._extract_first_json_object(text)
            return DeveloperResponse.model_validate(data)
        except Exception:
            # Fallback: keep pipeline running even if the model ignored JSON format.
            return DeveloperResponse(generated_code=text.strip())
    
    def single_agent(self, task_description: str) -> DeveloperResponse:
        """
        Single-agent baseline: generate code in one call without planning/routing.
        
        Used only for Architecture A.
        """
        prompt = SINGLE_AGENT_PROMPT.format(task_description=task_description)
        
        messages = [
            {"role": "system", "content": "You are an expert Python developer."},
            {
                "role": "system",
                "content": (
                    "Return ONLY a valid JSON object (no markdown, no code fences, no extra keys). "
                    "Schema: {generated_code: string}. "
                    "The string must contain the FULL Python solution."
                ),
            },
            {"role": "user", "content": prompt},
        ]

        text = self._invoke_text(self.models["baseline"], messages, temperature=0.0)
        try:
            data = self._extract_first_json_object(text)
            return DeveloperResponse.model_validate(data)
        except Exception:
            return DeveloperResponse(generated_code=text.strip())
    
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
            {
                "role": "system",
                "content": (
                    "Return ONLY a valid JSON object (no markdown, no code fences, no extra keys). "
                    "Schema: {feedback: string, reviewed_code: string}. "
                    "The reviewed_code must contain the FULL improved Python solution."
                ),
            },
            {"role": "user", "content": user_prompt},
        ]

        text = self._invoke_text(self.models["reviewer"], messages, temperature=0.0)
        try:
            data = self._extract_first_json_object(text)
            return ReviewerResponse.model_validate(data)
        except Exception:
            # Fallback: keep pipeline running even if the model ignored JSON format.
            return ReviewerResponse(
                feedback="Model did not return valid JSON per schema.",
                reviewed_code=text.strip(),
            )


def get_llm_client(architecture: Architecture = None) -> LLMClient:
    """Factory function to get LLMClient with specified architecture."""
    return LLMClient(architecture)