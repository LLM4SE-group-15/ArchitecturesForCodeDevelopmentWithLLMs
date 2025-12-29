import os
from enum import Enum
from typing import Literal


class Architecture(Enum):
    """Experimental architecture configurations."""
    A = "A"  # Single-agent baseline
    B = "B"  # Multi-agent, single-model
    C = "C"  # Multi-agent, multi-model hybrid


ARCHITECTURE_MODELS: dict[Architecture, dict[str, str]] = {
    Architecture.A: {
        # Single-agent: only baseline model (no planner/reviewer)
        "baseline": "Qwen/Qwen2.5-Coder-7B-Instruct",
    },
    Architecture.B: {
        # Multi-agent, same model for all roles
        "planner": "Qwen/Qwen2.5-Coder-7B-Instruct",
        "developer_s": "Qwen/Qwen2.5-Coder-7B-Instruct",
        "developer_m": "Qwen/Qwen2.5-Coder-7B-Instruct",
        "developer_l": "Qwen/Qwen2.5-Coder-7B-Instruct",
        "reviewer": "Qwen/Qwen2.5-Coder-7B-Instruct",
    },
    Architecture.C: {
        # Multi-agent, specialized models per role
        "planner": "meta-llama/Llama-3.1-8B-Instruct",
        "developer_s": "Qwen/Qwen2.5-Coder-1.5B-Instruct",
        "developer_m": "Qwen/Qwen2.5-Coder-7B-Instruct",
        "developer_l": "deepseek-ai/DeepSeek-Coder-V2-Instruct",
        "reviewer": "meta-llama/Llama-3.1-8B-Instruct",
    },
}


def get_architecture() -> Architecture:
    """Get architecture from environment variable."""
    arch_str = os.getenv("ARCHITECTURE", "C")
    return Architecture(arch_str)


def get_models(architecture: Architecture = None) -> dict[str, str]:
    """Get model mapping for the specified architecture."""
    if architecture is None:
        architecture = get_architecture()
    return ARCHITECTURE_MODELS[architecture]