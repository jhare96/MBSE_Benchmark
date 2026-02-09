"""Shared types to avoid circular imports between tasks and evaluation modules."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class LlmJudgeConfig:
    """Configuration for the LLM judge."""
    model_id: str
    max_tokens: int = 1024
    temperature: float = 0.0
    max_attempts: int = 3

@dataclass
class Task:
    """A benchmark task definition."""
    id: str
    type: str
    name: str
    description: str
    prompt: str
    max_tokens: int
    task_dir: str
    metadata: dict
    llm_judge_config: Optional[LlmJudgeConfig] = None
