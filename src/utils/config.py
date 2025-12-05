"""
Configuration Management

Loads and manages environment variables and project configuration.
"""

import os
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()


class Config:
    """Application configuration."""
    
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # LangSmith
    LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "true")
    LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
    LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "llm-code-architectures")
    
    # Model
    MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.0"))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2048"))
    
    # Paths
    TASKS_DIR = "tasks"
    RESULTS_DIR = "results"
    OUTPUTS_DIR = "outputs"
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set in environment")
        return True
