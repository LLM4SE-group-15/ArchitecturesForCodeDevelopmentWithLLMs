import time
from src.data.task_loader import APPSTaskLoader
from src.graph.graph import run_graph
from src.agents.llm import Architecture

ARCH = Architecture.B

SEED_FIXED = 0

def run_sample_tasks(
    per_level: int = 5,
    split: str = "test",
    difficulties: tuple[str, ...] = ("introductory","interview","competition"),
    shuffle: bool = True,
):
    loader = APPSTaskLoader(split=split)
    if shuffle:
        loader._dataset = loader.dataset.shuffle(seed=SEED_FIXED)

    tasks = []
    for diff in difficulties:
        tasks.extend(loader.load_by_difficulty(diff, limit=per_level))

    results = []
    total = len(tasks)
    logger.info("Loaded %s tasks (%s per difficulty: %s)", total, per_level, ", ".join(difficulties))

    for idx, task in enumerate(tasks, 1):
        logger.info("Running %s/%s %s (%s)", idx, total, task.task_id, task.difficulty)
        start = time.time()
        state = run_graph(
            task_id=task.task_id,
            task_description=task.question,
            test_inputs=task.inputs,
            test_outputs=task.outputs,
            architecture=ARCH,
        )

        print("State:", state)
        print()

        elapsed = time.time() - start
        record = {
            "task_id": task.task_id,
            "difficulty": task.difficulty,
            "architecture": str(ARCH.value),
            "test_passed": state["test_passed"],
            "developer_tier": state.get("developer_tier"),
            "escalations": state["escalations"],
            "story_points_initial": state.get("story_points_initial"),
            "story_points_final": state.get("story_points_current"),
            "elapsed_seconds": elapsed,
        }
        results.append(record)
        logger.info(
            "Finished %s | pass=%s tier=%s escalations=%s elapsed=%.1fs",
            task.task_id,
            state["test_passed"],
            record["developer_tier"],
            record["escalations"],
            elapsed,
        )
        with open(LOG_DIR / "architecture_B.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    return results

sample_results = run_sample_tasks(per_level=5, difficulties=("introductory","interview","competition"), shuffle=True)
sample_results