"""MBSE Benchmark - A benchmark for evaluating AI models on MBSE tasks."""

__version__ = "0.1.0"

from mbse_bench.evaluation import (
    EvaluationResult,
    EvaluationContext,
    CriterionScore,
    LLMEvaluationResult,
    LLMJudgmentEval,
    Eval,
    RUBRIC_TEMPLATES,
    evaluate_task,
    discover_evals
)

from mbse_bench.models import Task, LlmJudgeConfig
from mbse_bench.filesystem import FileSystem, load_virtual_filesystem
from mbse_bench.tasks import load_task, load_all_tasks, load_llm_judge_config

__all__ = [
    # Evaluation
    'EvaluationResult',
    'EvaluationContext',
    'CriterionScore',
    'LLMEvaluationResult',
    'LLMJudgmentEval',
    'Eval',
    'RUBRIC_TEMPLATES',
    'evaluate_task',
    'discover_evals',
    # Models
    'Task',
    'LlmJudgeConfig',
    # Filesystem
    'FileSystem',
    'load_virtual_filesystem',
    # Tasks
    'load_task',
    'load_all_tasks',
    'load_llm_judge_config',
]
