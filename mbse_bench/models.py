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


@dataclass
class ModelConfig:
    """Configuration for a model to be evaluated."""
    model_id: str
    max_tokens: int = 1024
    temperature: float = 0.0
    supports_tools: bool = True
    supports_responses: bool = False
