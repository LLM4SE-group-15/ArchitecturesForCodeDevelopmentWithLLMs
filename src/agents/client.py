import json
import os
import re
from typing import TypeVar
from dotenv import load_dotenv
from pydantic import BaseModel
from huggingface_hub import InferenceClient
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
from src.agents.llm import Architecture, get_architecture, get_models, get_prompt_repetition

load_dotenv()

T = TypeVar("T", bound=BaseModel)


class LLMClient:
    """
    LLM Client class for interacting with language models.
    
    Supports architecture-aware model selection for A/B/C experimental setups.
    """
    
    def __init__(self, architecture: Architecture = None, prompt_repetition: bool = None):
        self.hf_token = os.getenv("HF_TOKEN")
        self.architecture = architecture or get_architecture()
        self.models = get_models(self.architecture)
        self.prompt_repetition = prompt_repetition if prompt_repetition is not None else get_prompt_repetition()
        self._client = InferenceClient(token=self.hf_token)
    
    def _apply_prompt_repetition(self, messages: list[dict]) -> list[dict]:
        """Apply prompt repetition technique to user messages.
        
        Based on: Leviathan et al., "Prompt Repetition Improves Non-Reasoning LLMs"
        (arXiv:2512.14982, 2025). Repeats user prompt content to allow each token
        to attend to all other tokens in the prompt.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys.
            
        Returns:
            Modified messages with user content repeated if prompt_repetition is enabled.
        """
        if not self.prompt_repetition:
            return messages
        
        repeated_messages = []
        for msg in messages:
            if msg["role"] == "user":
                # Repeat the user content as per the paper's technique
                repeated_content = f"{msg['content']}\n\n{msg['content']}"
                repeated_messages.append({"role": "user", "content": repeated_content})
            else:
                repeated_messages.append(msg)
        return repeated_messages
    
    def _invoke_chat(self, model_name: str, messages: list[dict], temperature: float = 0.0) -> str:
        """Invoke model using chat completion API which handles routing correctly."""
        # Apply prompt repetition if enabled
        processed_messages = self._apply_prompt_repetition(messages)
        response = self._client.chat_completion(
            model=model_name,
            messages=processed_messages,
            max_tokens=2048,
            temperature=temperature if temperature > 0 else 0.01,  # Avoid exact 0
        )
        return response.choices[0].message.content

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
        """Invoke model - now uses chat completion API for better compatibility."""
        return self._invoke_chat(model_name, messages, temperature)

    @staticmethod
    def _extract_first_json_object(text: str) -> dict:
        """Extract the first JSON object from a model response.

        Models may wrap JSON in markdown fences or add pre/post text.
        This parser finds the first top-level JSON object using brace balancing
        while respecting strings and escapes, so it won't get confused by braces
        inside code strings.
        """
        cleaned = text.strip()
        
        # Remove markdown fences: ```json, ```, or just "json" prefix
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"```\s*$", "", cleaned)
        # Also handle bare "json" prefix (without backticks) that some models add
        cleaned = re.sub(r"^json\s*", "", cleaned.strip(), flags=re.IGNORECASE)
        
        # Handle Python triple quotes inside JSON (model quirk)
        # Convert """ to escaped quotes for JSON parsing
        cleaned = cleaned.replace('"""', '"')

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
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            # Attempt to fix common invalid escape sequences (e.g. LaTeX in text)
            try:
                # Regex: match \ that is NOT followed by a valid escape char
                # Valid JSON escapes: \" \\ \/ \b \f \n \r \t \uXXXX
                patched = re.sub(r'\\(?![/u"\\bfnrt])', r'\\\\', payload)
                data = json.loads(patched)
            except Exception:
                raise ValueError(f"Unparseable JSON in model output: {text[:2000]}")

        # Small robustness: allow story_points as string digits
        if isinstance(data, dict) and "story_points" in data and isinstance(data["story_points"], str):
            sp = data["story_points"].strip()
            if sp.isdigit():
                data["story_points"] = int(sp)

        return data
    
    @staticmethod
    def _clean_code_string(code: str) -> str:
        """Removes markdown code fences and other artifacts from a string if present."""
        if not code:
            return ""
        
        code = code.strip()
        
        # Handle case where the entire response is wrapped in JSON with "generated_code" key
        # This happens when model returns nested JSON like: {"generated_code": "...actual code..."}
        if code.startswith("{") and "generated_code" in code:
            try:
                # Remove triple quotes that models sometimes use
                fixed = code.replace('"""', '"')
                parsed = json.loads(fixed)
                if isinstance(parsed, dict) and "generated_code" in parsed:
                    code = parsed["generated_code"]
            except (json.JSONDecodeError, KeyError):
                pass
        
        # Remove "json" prefix (model artifact)
        code = re.sub(r"^json\s*", "", code, flags=re.IGNORECASE)
        
        # Remove leading ```python, ```json, or ``` (case insensitive)
        code = re.sub(r"^```(?:python|json)?\s*", "", code.strip(), flags=re.IGNORECASE)
        # Remove trailing ```
        code = re.sub(r"\s*```$", "", code)
        
        # Handle triple quotes that models sometimes use instead of escaped quotes
        # Only do this if the code starts with triple quotes and contains them
        if code.startswith('"""') and code.count('"""') >= 2:
            # Extract content between triple quotes
            match = re.search(r'^"""(.*?)"""', code, re.DOTALL)
            if match:
                code = match.group(1)
        
        return code.strip()

    @staticmethod
    def _extract_code_from_response(text: str) -> str:
        """Extract Python code from a model response using multiple strategies.
        
        This is used as a fallback when the model doesn't follow JSON format instructions.
        """
        if not text:
            return ""
        
        text = text.strip()
        
        # Strategy 1: Try to find code inside markdown code blocks
        code_block_match = re.search(r"```(?:python)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
        if code_block_match:
            return code_block_match.group(1).strip()
        
        # Strategy 2: Try to extract "generated_code" from JSON-like structure with triple quotes
        # Pattern: {"generated_code": """..."""}
        triple_quote_match = re.search(r'"generated_code"\s*:\s*"""(.*?)"""', text, re.DOTALL)
        if triple_quote_match:
            return triple_quote_match.group(1).strip()
        
        # Strategy 3: Try to extract from regular JSON structure
        # Pattern: {"generated_code": "..."}
        try:
            # Remove "json" prefix if present
            cleaned = re.sub(r"^json\s*", "", text, flags=re.IGNORECASE)
            # Handle triple quotes
            cleaned = cleaned.replace('"""', '"')
            
            # Find and parse JSON
            start = cleaned.find("{")
            if start != -1:
                # Try to find matching brace
                depth = 0
                for i, ch in enumerate(cleaned[start:], start):
                    if ch == "{":
                        depth += 1
                    elif ch == "}":
                        depth -= 1
                        if depth == 0:
                            json_str = cleaned[start:i+1]
                            try:
                                data = json.loads(json_str)
                                if isinstance(data, dict) and "generated_code" in data:
                                    return data["generated_code"].strip()
                            except json.JSONDecodeError:
                                pass
                            break
        except Exception:
            pass
        
        # Strategy 4: Look for Python code patterns - if text looks like Python code, use it
        # Check if it starts with common Python patterns (after removing artifacts)
        cleaned_text = re.sub(r"^json\s*", "", text, flags=re.IGNORECASE)
        cleaned_text = re.sub(r"^```(?:python|json)?\s*", "", cleaned_text, flags=re.IGNORECASE)
        cleaned_text = re.sub(r"\s*```$", "", cleaned_text)
        
        # Remove any leading JSON wrapper characters
        cleaned_text = cleaned_text.strip()
        if cleaned_text.startswith("{"):
            # Try to skip past JSON wrapper
            newline_pos = cleaned_text.find("\n")
            if newline_pos > 0:
                rest = cleaned_text[newline_pos:].strip()
                if rest.startswith('"""'):
                    # Extract from triple quotes
                    match = re.search(r'^"""(.*?)"""', rest, re.DOTALL)
                    if match:
                        return match.group(1).strip()
        
        # Strategy 5: If text contains import statements or def/class, it's likely code
        if re.search(r'^(import|from|def|class|#)', cleaned_text, re.MULTILINE):
            return cleaned_text.strip()
        
        # Last resort: return cleaned text
        return cleaned_text.strip()

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
            response = DeveloperResponse.model_validate(data)
            response.generated_code = self._clean_code_string(response.generated_code)
            return response
        except Exception:
            # Fallback: try multiple strategies to extract code
            extracted_code = self._extract_code_from_response(text)
            return DeveloperResponse(generated_code=extracted_code)
    
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
            response = DeveloperResponse.model_validate(data)
            response.generated_code = self._clean_code_string(response.generated_code)
            return response
        except Exception:
            # Fallback: try multiple strategies to extract code
            extracted_code = self._extract_code_from_response(text)
            return DeveloperResponse(generated_code=extracted_code)
    
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
            response = ReviewerResponse.model_validate(data)
            response.reviewed_code = self._clean_code_string(response.reviewed_code)
            return response
        except Exception:
            # Fallback: try multiple strategies to extract code
            extracted_code = self._extract_code_from_response(text)
            
            return ReviewerResponse(
                feedback="Model did not return valid JSON per schema.",
                reviewed_code=extracted_code,
            )


def get_llm_client(architecture: Architecture = None, prompt_repetition: bool = None) -> LLMClient:
    """Factory function to get LLMClient with specified architecture and prompt repetition setting."""
    return LLMClient(architecture, prompt_repetition)