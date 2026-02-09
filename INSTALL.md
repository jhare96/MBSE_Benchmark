# MBSE Benchmark Installation

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/your-org/MBSE_Benchmark.git
cd MBSE_Benchmark

# Install in development mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### From PyPI (when published)

```bash
pip install mbse-bench
```

## Requirements

- Python 3.10 or higher
- OpenAI API key (for LLM-based evaluations)

## Quick Start

```python
from mbse_bench import load_task, evaluate_task, EvaluationContext
from mbse_bench.filesystem import load_virtual_filesystem
from openai import AsyncOpenAI

# Load a task
task = load_task("data/tasks/sample-task")

# Set up OpenAI client
client = AsyncOpenAI(api_key="your-api-key")

# Create evaluation context
fs = load_virtual_filesystem(task.task_dir)
context = EvaluationContext(
    original_files=fs.snapshot(),
    modified_files=fs.snapshot(),
    task_prompt=task.prompt
)

# Run evaluation
results = await evaluate_task(task, "AI response", context, client)

# Print results
for result in results:
    print(f"Score: {result.score}")
    print(f"Explanation: {result.explanation}")
```
