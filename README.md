# Architectures for Code Development with LLMs

Comparative analysis of single-agent vs multi-agent LLM architectures for code generation tasks.

## Project Overview

This project evaluates the effectiveness of different LLM architectures in software engineering tasks, comparing:
- **Single-Agent Baseline**: One LLM generating complete code solutions
- **Multi-Agent System**: Multiple specialized agents with distinct roles (planning, development, review, testing)

## Research Questions

1. Which architectures produce higher-quality and more maintainable code?
2. How do agent coordination strategies impact correctness?
3. Does modular role separation improve code generation?

## Team

**Course**: Architectures for Code Development with LLMs  
**Instructor**: Prof. Riccardo Coppola  
**Group**: LLM4SE-group-15

## Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

## Project Structure

```
├── tasks/              # Programming tasks dataset
├── src/
│   ├── agents/         # Agent implementations
│   ├── evaluation/     # Evaluation framework
│   └── utils/          # Utilities
├── results/            # Experimental results
└── docs/               # Documentation
```

## License

MIT
