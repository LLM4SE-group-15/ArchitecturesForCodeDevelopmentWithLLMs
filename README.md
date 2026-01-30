# Multi-Agent Architectures for LLM-Based Code Generation: Evaluating Adaptive Routing and Model Specialization

📄 **For complete project details, methodology, and experimental results, see the full report:**

[![Report](https://img.shields.io/badge/Report-PDF-red?style=for-the-badge&logo=adobe)](./report/main.pdf)

---

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-Inference_API-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/)
[![LangChain](https://img.shields.io/badge/LangChain-Framework-blueviolet?style=for-the-badge)](https://python.langchain.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Orchestration-orange?style=for-the-badge)](https://python.langchain.com/docs/langgraph)
[![LangSmith](https://img.shields.io/badge/LangSmith-Observability-green?style=for-the-badge)](https://smith.langchain.com/)
[![Kaggle](https://img.shields.io/badge/Kaggle-Notebooks-20BEFF?style=for-the-badge&logo=kaggle)](https://www.kaggle.com/)

---

## 📂 Project Structure

```
project/
├── data/                      # HumanEval dataset and experiment logs
├── docs/                      # Detailed method documentation
├── notebook/                  # Jupyter notebooks for experiments
├── report/                    # LaTeX source of the scientific paper
│   └── figures/               # Architecture diagrams and charts
├── src/                       # Source code
│   ├── __init__.py
│   ├── agents/                # LLM interaction layer
│   │   ├── client.py          # HuggingFace API client with retry logic
│   │   └── llm.py             # Architecture & model configurations
│   ├── data/                  # Dataset handling
│   │   └── task_loader.py     # HumanEval task loader
│   ├── evaluation/            # Metrics computation
│   │   └── __init__.py
│   ├── graph/                 # LangGraph state machine
│   │   ├── config.py          # Story points → tier mapping
│   │   ├── graph.py           # Graph builder & runner
│   │   ├── nodes.py           # Agent node implementations
│   │   └── state.py           # GraphState TypedDict definition
│   └── models/                # Prompts & schemas
│       ├── llm_responses.py   # Pydantic response models
│       └── prompts.py         # System/user prompts for all agents
├── tests/                     # Unit tests for the pipeline
├── main.py                    # Entry point
└── requirements.txt           # Dependencies
```

---

## 🚀 Usage

This project is optimized to run in the cloud using **Kaggle Notebooks** for reproducible execution.

### Steps to Run

1.  **Clone the Repository**
    Clone this repository to your local machine or download the zip.

2.  **Import to Kaggle**
    *   Create a new Notebook on [Kaggle](https://www.kaggle.com/).
    *   Upload the project files (specifically the `notebook/` folder contents) into the Kaggle environment.

3.  **Configure Environment**
    *   **Enable GPU**: In the Notebook settings, verify that a GPU (e.g., T4 x2) is enabled.
    *   **Set Secrets**: Add your API keys in the Kaggle "Secrets" menu:
        *   `HF_TOKEN`: Your HuggingFace API key (required).
        *   `LANGSMITH_API_KEY`: Your LangSmith key (optional, for tracing).

4.  **Run the Notebook**
    Select one of the notebooks below and execute the cells.

---

## 📓 Notebooks

The project includes pre-configured notebooks for each architectural experiment:

| Notebook | Description |
|----------|-------------|
| `architecture-a.ipynb` | **Baseline**: Single-agent code generation (Qwen-7B). |
| `architecture-b.ipynb` | **Multi-Agent**: Full pipeline (Plan/Code/Test/Review) using a single model (Qwen-7B). |
| `architecture-c.ipynb` | **Adaptive**: Multi-agent with specialized models (1.5B/7B/32B) routed by difficulty. |
| `architecture-c1.ipynb` | **Always-Large**: Benchmark using the largest model (32B) for all tasks. |
| `ablation-no-s-model.ipynb` | **Ablation Study (C2)**: Removes Tier S to test reliability impact. |
| `*-pr.ipynb` | **Prompt Repetition**: Variants of A, B, and C using the Prompt Repetition technique. |


---

## 📖 Overview

This project presents a systematic empirical comparison of **Multi-Agent Systems (MAS)** for automated code generation using Large Language Models. We evaluate complex agentic pipelines that mimic real-world software engineering processes: **Planning**, **Routing**, **Development**, **Testing**, and **Code Review**.

Our research addresses the following **Research Questions**:

| RQ | Question |
|----|----------|
| **RQ1** | Does a multi-agent pipeline with role separation (Planner, Developer, Tester, Reviewer) improve functional correctness compared to a single-agent approach? |
| **RQ2** | Do specialized models assigned to each role provide measurable benefits over using a single model for all roles? |
| **RQ3** | Can adaptive routing—selecting developer model capacity based on estimated task difficulty—reduce computational cost while maintaining or improving quality? |
| **RQ4** | Does prompt repetition improve code generation accuracy for the models used in this study? |

The study benchmarks performance using the **HumanEval** dataset (164 tasks) across various architectural configurations.

---

## Key Features

### Multi-Agent Orchestration
The system decomposes code generation into **five specialized roles**, each implemented as a node in a LangGraph state machine:
- **Planner**: Analyzes task specifications and estimates difficulty using Scrum-style story points
- **Router**: Directs tasks to appropriately-sized developer models based on difficulty
- **Developer**: Generates implementation code based on task description and feedback
- **Tester**: Executes code against assertion-based tests in a sandboxed Python subprocess (10s timeout)
- **Reviewer**: Analyzes test failures and provides actionable feedback for iteration

### Adaptive Routing
Tasks are dynamically routed to different model capacities based on estimated difficulty:
- **Story Points 1-2** → Tier S (Qwen 1.5B) — Simple tasks
- **Story Points 3-5** → Tier M (Qwen 7B) — Medium complexity
- **Story Point 8** → Tier L (Qwen 32B) — Complex tasks

### Self-Correction Loop
When tests fail, the pipeline doesn't terminate. Instead:
1. The **Reviewer** analyzes error messages and identifies the root cause
2. Actionable feedback is generated for the Developer
3. The Developer receives: previous code + error logs + reviewer feedback
4. A new implementation attempt is made with full context

### Escalation Policy
If a model fails to produce passing code, the system **escalates** to the next tier:
- Tier S fails → Escalate to Tier M
- Tier M fails → Escalate to Tier L
- Maximum 2 escalations allowed per task

---


## 🛠️ Technology Stack

| Category | Technologies |
|----------|-------------|
| **Core** | Python 3.10+, LangGraph, LangChain |
| **LLM Inference** | HuggingFace Inference API (Serverless) |
| **Models** | Qwen2.5-Coder (1.5B, 7B, 32B), Llama-3-8B |
| **Analysis** | Radon (Cyclomatic Complexity) |
| **Observability** | LangSmith (Tracing & Debugging) |

---

## 🏗️ System Architecture

The system is built on a directed cyclic graph architecture using **LangGraph**. It decomposes code generation into specialized roles, moving from a monolithic "black box" approach to an interactive pipeline.

### Architecture Overview
![Architecture Overview](./report/figures/ArchitetureOverview.png)
*Comparison of the four main architectures: A (Single-Agent), B (Multi-Agent Single-Model), C (Adaptive Multi-Model), and C1 (Always-Large).*

---

### Story Points & Tier Routing
![Story Points Routing](./report/figures/StoryPointsTierRouting.png)
*The Planner assigns Fibonacci-based story points (1, 2, 3, 5, 8) to estimate task difficulty. The Router maps these to Developer Tiers (S/M/L), matching model capacity to task complexity.*

---

### Escalation Policy
![Escalation Policy](./report/figures/EscalationPolicy.png)
*When tests fail, the system escalates to the next tier. The escalating Developer receives: previous code, error messages, and Reviewer feedback. Maximum 2 escalations per task.*

---

## 🧩 Architectural Variants

### Architecture A — Single Agent Baseline
![Architecture A](./report/figures/SingleModel.png)
*Baseline configuration: one model (Qwen-7B), one attempt, no retry. The task flows directly to the Developer, code is tested, and the pipeline terminates regardless of result. Establishes the performance floor.*

---

### Architecture B — Multi-Agent Single Model
![Architecture B](./report/figures/MultiAgentSingleModel.png)
*Full multi-agent pipeline using the same model (Qwen-7B) for all roles. Includes Planner, Router, Developer, Tester, and Reviewer with retry loops. Isolates the effect of role separation from model capacity differences.*

---

### Architecture C — Adaptive Multi-Model
![Architecture C](./report/figures/MultiAgentMultiModel.png)
*Multi-agent pipeline with specialized models: Llama-3-8B for Planner/Reviewer, Qwen models (1.5B/7B/32B) for Developers. Tasks are routed based on story point estimates, with escalation on failure.*

---

### Architecture C1 — Always Large
![Architecture C1](./report/figures/MultiAgentAlwaysL.png)
*Multi-agent pipeline that bypasses adaptive routing entirely. All tasks are assigned to the Tier L Developer (Qwen-32B) regardless of estimated difficulty. Serves as the upper-bound reference for accuracy.*

---

### Architecture C2 — Ablation (No Tier S)
Architecture C2 is an **ablation study** that removes Tier S (1.5B model) entirely from the adaptive routing configuration. Tasks estimated as "easy" (Story Points 1-2) are routed directly to Tier M instead.

**Purpose**: To validate whether the smallest model (Qwen-1.5B) is a bottleneck causing cascading failures and context pollution in the adaptive configuration.

**Results**: C2 achieved **72.0% pass rate** (vs. 62.2% for C), with escalations dropping from 152 to 74, confirming that Tier S was the primary source of failures.

---

### Prompt Repetition
![Prompt Repetition](./report/figures/PromptRepetition.png)
*Technique proposed by Leviathan et al. that duplicates user prompts to improve token attention. Tokens in the second occurrence can attend to all tokens in the first. Tested across all architectures (A-PR, B-PR, C-PR).*

---

## 👥 Authors

*   **Ivan Necerini** 
*   **Jacopo Rialti**
*   **Emanuele Romano**
*   **Marco Donatucci**
*   **Ferdinando Del Vecchio**

---
