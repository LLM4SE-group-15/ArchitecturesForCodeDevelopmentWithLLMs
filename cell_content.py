import time
import json
import logging
from pathlib import Path
from src.data.task_loader import HumanEvalTaskLoader
from src.graph.graph import run_graph
from src.agents.llm import Architecture

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("humaneval_benchmark")

LOG_DIR = Path("results")
LOG_DIR.mkdir(exist_ok=True)

ARCH = Architecture.B
SEED_FIXED = 0


def run_humaneval_benchmark(
    limit: int = 10,
    offset: int = 0,
):
    """
    Run benchmark on HumanEval tasks.
    
    Args:
        limit: Number of tasks to run
        offset: Starting index in the dataset
    """
    loader = HumanEvalTaskLoader()
    tasks = loader.load_tasks(limit=limit, offset=offset)

    results = []
    total = len(tasks)
    logger.info("Loaded %s tasks from HumanEval", total)

    for idx, task in enumerate(tasks, 1):
        logger.info("Running %s/%s %s", idx, total, task.task_id)
        start = time.time()
        
        state = run_graph(
            task_id=task.task_id,
            task_description=task.prompt,
            test_code=task.test,
            entry_point=task.entry_point,
            architecture=ARCH,
        )

        elapsed = time.time() - start
        record = {
            "task_id": task.task_id,
            "entry_point": task.entry_point,
            "architecture": str(ARCH.value),
            "test_passed": state["test_passed"],
            "developer_tier": state.get("developer_tier"),
            "escalations": state["escalations"],
            "story_points_initial": state.get("story_points_initial"),
            "story_points_final": state.get("story_points_current"),
            "elapsed_seconds": elapsed,
        }
        results.append(record)
        
        status = "PASS" if state["test_passed"] else "FAIL"
        logger.info(
            "Finished %s | %s | tier=%s escalations=%s elapsed=%.1fs",
            task.task_id,
            status,
            record["developer_tier"],
            record["escalations"],
            elapsed,
        )
        
        # Save incrementally
        with open(LOG_DIR / f"humaneval_{ARCH.value}.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    
    # Summary
    passed = sum(1 for r in results if r["test_passed"])
    logger.info("Summary: %s/%s passed (%.1f%%)", passed, total, 100 * passed / total if total > 0 else 0)
    
    return results


if __name__ == "__main__":
    sample_results = run_humaneval_benchmark(limit=10, offset=0)
    print(sample_results)
