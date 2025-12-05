# Setup Guide

## Prerequisites

- Python 3.10+
- OpenAI API key
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

Edit `.env` and add your API keys:
```
OPENAI_API_KEY=sk-...
LANGCHAIN_API_KEY=lsv2_...
```

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
# Single-agent only
python main.py --architecture single

# Multi-agent only
python main.py --architecture multi
```

## Project Structure

```
.
├── src/
│   ├── agents/          # Agent implementations
│   ├── evaluation/      # Evaluation framework
│   └── utils/           # Utilities
├── tasks/               # Task dataset
├── results/             # Experiment results
├── docs/                # Documentation
├── main.py              # Main execution script
├── requirements.txt     # Dependencies
└── .env                 # Configuration (not in git)
```

## Next Steps

1. Add more tasks to `tasks/` directory
2. Customize agent prompts in `src/utils/prompts.py`
3. Run experiments with `python main.py`
4. Analyze results in `results/` directory
