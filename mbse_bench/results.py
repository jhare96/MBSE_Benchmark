"""Results export functionality."""

import json
import os
from pathlib import Path
from datetime import datetime


def get_version() -> str:
    """Get benchmark version from package.json or generate one."""
    try:
        package_json = Path(__file__).parent.parent / "package.json"
        if package_json.exists():
            with open(package_json) as f:
                data = json.load(f)
                version = data.get("version", "0.1.0")
        else:
            version = "0.1.0"
    except Exception:
        version = "0.1.0"
    
    # Add timestamp: 0.1.0-202601271630
    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    return f"{version}-{timestamp}"


def save_result(
    model_id: str,
    score: float,
    tasks: list[dict],
    duration: float,
    results_dir: str = "data/results"
) -> str:
    """
    Save benchmark results to JSON file.
    
    Args:
        model_id: The model ID (e.g., "gpt-4.1")
        score: Overall score (0-1)
        tasks: List of task results
        duration: Total duration in seconds
        results_dir: Base results directory
    
    Returns:
        Path to the saved file
    """
    version = get_version()
    version_dir = Path(results_dir) / version
    version_dir.mkdir(parents=True, exist_ok=True)
    
    # Serialize task results, converting any non-JSON-serializable objects
    serialized_tasks = []
    for task in tasks:
        task_data = {
            "taskId": task.get("task_id"),
            "score": task.get("score", 0.0),
            "latencyMs": task.get("latency_ms", 0),
        }
        # Skip the results field as it contains non-serializable objects
        serialized_tasks.append(task_data)
    
    # Create result object
    result = {
        "version": version,
        "modelId": model_id,
        "timestamp": datetime.now().isoformat(),
        "score": score,
        "tasks": serialized_tasks,
        "metadata": {
            "duration": duration,
            "tasksCompleted": len([t for t in tasks if "error" not in t]),
            "tasksFailed": len([t for t in tasks if "error" in t]),
        }
    }
    
    # Save to file
    filename = f"{model_id}.json"
    output_path = version_dir / filename
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    
    return str(output_path)
