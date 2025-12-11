# A2: Architectures for Code Development with LLMs

Comparative analysis of single-agent vs multi-agent LLM architectures for code generation tasks.

## Project overview
- ***A (Application)***: projects in which you will analyze the
effectiveness of the application of LLMs in various Software Engineering tasks.
- Responsible: prof. Riccardo Coppola

**Project Track:** 
- LLMs can generate code, but single-prompt interactions often fail on long or complex development tasks Multi-agent architectures may improve quality by splitting responsibilities (design, planning, writing, reviewing, debugging).

**Task Selection**
Select 10-20 programming tasks from:
- Public datasets (HumanEval, MBPP, CodeNet subsets)
- Past course assignments
- Open-source code snippets

**System Implementation**
- Single-Agent Baseline: One LLM generating complete code solutions
- Multi-Agent System: ≥2 specialized agents with distinct roles (e.g., planning, development, review, testing)

**Evaluation Metrics**
Choose at least one evaluation method:
- Functional correctness (unit tests or provided test suites)
- Static code quality metrics (complexity, maintainability indices)
- Debugging performance (fault detection and fixing capabilities)
- Readability and maintainability assessment

This project evaluates the effectiveness of different LLM architectures in software engineering tasks, comparing:
- **Single-Agent Baseline**: One LLM generating complete code solutions
- **Multi-Agent System**: Multiple specialized agents with distinct roles (planning, development, review, testing)

### Research Questions

1. Which architectures produce higher-quality and more maintainable code?
2. How do agent coordination strategies impact correctness?
3. Does modular role separation improve code generation?
