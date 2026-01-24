import os
from enum import Enum
from typing import Literal


class Architecture(Enum):
    """Experimental architecture configurations."""
    A = "A"   # Single-agent baseline
    B = "B"   # Multi-agent, single-model
    C = "C"   # Multi-agent, multi-model adaptive (routes S/M/L by story points)
    C1 = "C1" # Multi-agent, multi-model always-L (always uses strongest developer)


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
        # Multi-agent, specialized models per role (adaptive routing)
        "planner": "meta-llama/Meta-Llama-3-8B-Instruct",        
        "developer_s": "Qwen/Qwen2.5-Coder-1.5B-Instruct",
        "developer_m": "Qwen/Qwen2.5-Coder-7B-Instruct",
        "developer_l": "Qwen/Qwen2.5-Coder-32B-Instruct",
        "reviewer": "meta-llama/Meta-Llama-3-8B-Instruct",
    },
    Architecture.C1: {
        # Multi-agent, always uses L tier (same models as C)
        "planner": "meta-llama/Meta-Llama-3-8B-Instruct",        
        "developer_s": "Qwen/Qwen2.5-Coder-32B-Instruct",  # All tiers use L model
        "developer_m": "Qwen/Qwen2.5-Coder-32B-Instruct",  # All tiers use L model
        "developer_l": "Qwen/Qwen2.5-Coder-32B-Instruct",
        "reviewer": "meta-llama/Meta-Llama-3-8B-Instruct",
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