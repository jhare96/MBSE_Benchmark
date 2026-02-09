"""Task loading and management."""

import json
import pathlib

from mbse_bench.models import Task, LlmJudgeConfig


def load_task(task_dir: str, llm_judge_config: LlmJudgeConfig | None = None) -> Task:
    """Loads a task from the specified directory."""
    task_file = pathlib.Path(task_dir) / "task.json"
    with open(task_file, "r") as f:
        task_json = json.load(f)
        evaluate_config = EvaluationTask(**task_json['evaluation'])

        task_data = {
            'id': task_json['id'],
            'type': task_json['type'],
            'name': task_json['name'],
            'description': task_json['description'],
            'prompt': task_json['prompt'],
            'task_dir': task_dir,
            'evaluation': evaluate_config,
            'llm_judge_config': llm_judge_config,
            'max_tokens': task_json.get('MaxTokens', None),
            'metadata': task_json.get('metadata', {}),
        }
        return Task(**task_data)
    

def load_llm_judge_config() -> LlmJudgeConfig:
    """Loads the LLM judge configuration from the benchmark.json file."""
    parent_dir = pathlib.Path(__file__).parent.parent
    benchmark_json = parent_dir / "config" / "benchmark.json"
    with open(benchmark_json, "r") as f:
        config_json = json.load(f)
        llm_judge_config = config_json.get("llmJudge", None)
        if llm_judge_config is not None:
            return LlmJudgeConfig(
                model_id=llm_judge_config["modelId"],
                max_tokens=llm_judge_config["maxTokens"],
                temperature=llm_judge_config["temperature"],
                max_attempts=llm_judge_config["maxAttempts"],
            )
        else:
            raise ValueError("LLM judge configuration not found in benchmark.json")

def load_all_tasks() -> list[Task]:
    """Loads all tasks from the data/tasks directory."""
    parent_dir = pathlib.Path(__file__).parent.parent
    tasks_dir = parent_dir / "data" / "tasks"

    llm_judge_config = load_llm_judge_config()
    task_files = tasks_dir.glob("*/task.json")
    tasks = []
    for task_file in task_files:
        try:
            tasks.append(load_task(str(task_file.parent), llm_judge_config))
        except Exception as e:
            print(f"Failed to load task from {task_file.parent}: {e}")
    
    return tasks


def load_tasks_sample() -> list[Task]:
    """Loads a sample of tasks for quick testing."""
    all_tasks = load_all_tasks()
    sample_task = [task for task in all_tasks if task.id == 'sample-task']
    return sample_task + all_tasks[:2]  # Return the sample-task + first two tasks as a sample