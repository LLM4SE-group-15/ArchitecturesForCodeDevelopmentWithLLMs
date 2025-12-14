# Setup Guide

## Prerequisites

- Python 3.10+
- An LLM inference backend (local or hosted)
- API keys as needed by your chosen backend
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
venv\Scripts\Activate.ps1
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

Edit `.env` and configure tracing (optional) and model names.

If you use an OpenAI-compatible endpoint (including local servers), set:
```
OPENAI_API_KEY=sk-...
LANGCHAIN_API_KEY=lsv2_...
```

Model configuration for the new experimental setups:

Architecture A (single-agent baseline):
```
BASELINE_MODEL=Qwen/Qwen2.5-Coder-7B-Instruct
```

Architecture B (multi-agent, single-model):
```
PLANNER_MODEL=Qwen/Qwen2.5-Coder-7B-Instruct
DEVELOPER_MODEL=Qwen/Qwen2.5-Coder-7B-Instruct
REVIEWER_MODEL=Qwen/Qwen2.5-Coder-7B-Instruct
```

Note: there is no separate `INTEGRATION_MODEL` in the current single-snippet
workflow — Developers produce a single complete snippet per task.

Architecture C (multi-agent, multi-model hybrid):
```
PLANNER_MODEL=meta-llama/Llama-3.1-8B-Instruct
REVIEWER_MODEL=meta-llama/Llama-3.1-8B-Instruct

DEV_S_MODEL=Qwen/Qwen2.5-Coder-1.5B-Instruct
DEV_M_MODEL=Qwen/Qwen2.5-Coder-7B-Instruct
DEV_L_MODEL=deepseek-ai/DeepSeek-Coder-V2-Instruct
```

Note: the **Tester is not an LLM**; it runs your Python unit tests.

### 5. Verify Setup

```bash
python -c "from src.utils.config import Config; Config.validate(); print('Setup OK!')"
```

## Running Experiments

### Run Both Architectures

```bash
python main.py --tasks-dir tasks --output-dir results
```

### Run Single Architecture

```bash
python main.py --architecture single
python main.py --architecture multi

Planned/experimental flags (depending on your implementation):
- `A`: single-agent baseline
- `B`: multi-agent single-model
- `C`: multi-agent multi-model hybrid (Planner/Reviewer + Dev-S/M/L)
```