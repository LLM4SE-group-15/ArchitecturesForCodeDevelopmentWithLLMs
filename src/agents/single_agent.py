"""
Single-Agent Baseline System

This module implements a single LLM agent that generates complete code solutions
from task descriptions in one pass.
"""

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from typing import Dict, Any
import time

from src.utils.config import Config
from src.utils.logger import setup_logger
from src.utils.prompts import SINGLE_AGENT_SYSTEM_PROMPT, SINGLE_AGENT_USER_PROMPT

logger = setup_logger(__name__)


class SingleAgent:
    """Single-agent code generator using one LLM call."""
    
    def __init__(self, model_name: str = None, temperature: float = None):
        """
        Initialize the single agent.
        
        Args:
            model_name: OpenAI model name (default from config)
            temperature: Sampling temperature (default from config)
        """
        self.model_name = model_name or Config.MODEL_NAME
        self.temperature = temperature if temperature is not None else Config.TEMPERATURE
        
        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            max_tokens=Config.MAX_TOKENS
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", SINGLE_AGENT_SYSTEM_PROMPT),
            ("user", SINGLE_AGENT_USER_PROMPT)
        ])
        
        self.chain = self.prompt | self.llm | StrOutputParser()
        
        logger.info(f"SingleAgent initialized with model={self.model_name}, temp={self.temperature}")
    
    def generate_code(self, task_description: str) -> Dict[str, Any]:
        """
        Generate code solution for a given task.
        
        Args:
            task_description: Natural language description of the programming task
            
        Returns:
            Dictionary containing:
                - code: Generated Python code
                - prompt_tokens: Number of prompt tokens used
                - completion_tokens: Number of completion tokens used
                - execution_time: Time taken to generate code
        """
        logger.info("Generating code with SingleAgent")
        start_time = time.time()
        
        try:
            # Generate code
            code = self.chain.invoke({"task_description": task_description})
            
            execution_time = time.time() - start_time
            
            # TODO: Extract token usage from response
            # For now, estimate based on response
            result = {
                "code": code.strip(),
                "prompt_tokens": 0,  # Will be populated by LangSmith
                "completion_tokens": 0,  # Will be populated by LangSmith
                "execution_time": execution_time,
                "model": self.model_name,
                "architecture": "single-agent"
            }
            
            logger.info(f"Code generated successfully in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Error generating code: {str(e)}")
            raise
