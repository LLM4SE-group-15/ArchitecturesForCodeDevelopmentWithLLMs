# A2: Architectures for Code Development with LLMs

Comparative analysis of single-agent vs multi-agent LLM architectures for code generation.

## Setup

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1          # Windows
pip install -r requirements.txt
cp .env.example .env                  # Configure HF_TOKEN and ARCHITECTURE
```

## Architectures

Set `ARCHITECTURE` in `.env`:

| Value | Description |
|-------|-------------|
| `A` | Single-agent baseline (Qwen-7B) |
| `B` | Multi-agent, single-model (Qwen-7B for all roles) |
| `C` | Multi-agent, multi-model (specialized models per role) |

## Project Structure

```
src/
├── agents/          # LLM calls (client.py, llm.py)
├── graph/           # LangGraph workflow (nodes.py, graph.py, state.py)
├── data/            # Dataset loading (task_loader.py)
└── models/          # Prompts and response models
```

---

## Docs

See `docs/` for detailed architecture documentation.
