# Setup Guide

## Prerequisites

- Python 3.10+
- HuggingFace account with API token
- LangSmith account (optional, for tracking)

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/LLM4SE-group-15/ArchitecturesForCodeDevelopmentWithLLMs.git
cd ArchitecturesForCodeDevelopmentWithLLMs
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Required
HF_TOKEN=your_huggingface_token_here

# Optional (for tracking)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=llm-code-architectures

# Architecture Selection (A, B, or C)
ARCHITECTURE=C
```

### Architecture Options

| Value | Description |
|-------|-------------|
| `A` | Single-agent baseline (Qwen-7B only) |
| `B` | Multi-agent, single-model (Qwen-7B for all roles) |
| `C` | Multi-agent, multi-model hybrid (specialized models per role) |

Model configurations are defined in `src/agents/llm.py` and selected automatically based on the `ARCHITECTURE` variable.

### 5. Verify Setup

```bash
# Check architecture configuration
python -c "from src.agents.llm import get_architecture; print('Architecture:', get_architecture())"

# Load APPS dataset
python -c "from src.data.task_loader import APPSTaskLoader; print('Tasks:', len(APPSTaskLoader()))"

# Verify graph builds correctly
python -c "from src.graph.graph import build_graph; print('Nodes:', list(build_graph().nodes.keys()))"
```

## Running Experiments

### Using Python

```python
from src.graph.graph import run_graph
from src.data.task_loader import APPSTaskLoader

# Load a task
loader = APPSTaskLoader()
task = loader.get_task(0)

# Run the graph
result = run_graph(
    task_id=task.task_id,
    task_description=task.question,
    test_inputs=task.inputs,
    test_outputs=task.outputs
)

print(f"Test passed: {result['test_passed']}")
print(f"Developer tier: {result['developer_tier']}")
print(f"Escalations: {result['escalations']}")
```

### Switching Architectures

To switch between architectures, change the `ARCHITECTURE` variable in `.env`:

```bash
# Edit .env
ARCHITECTURE=A  # or B, or C
```

Or pass it programmatically:

```python
from src.graph.graph import run_graph
from src.agents.llm import Architecture

result = run_graph(
    task_id="test_1",
    task_description="...",
    architecture=Architecture.A
)
```