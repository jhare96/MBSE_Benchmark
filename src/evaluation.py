from dataclasses import dataclass, field
from openai import AsyncOpenAI
from pydantic import BaseModel, Field, computed_field
from typing import Optional
from filesystem import FileSystem
from models import Task, LlmJudgeConfig


class CriterionScore(BaseModel):
    """Score for a single evaluation criterion."""
    name: str
    score: float = Field(ge=0.0, le=1.0)
    feedback: str = ""

@dataclass
class EvaluationResult:
    """Result of an evaluation."""
    score: float  # 0-1 normalized
    details: dict[str, CriterionScore] = field(default_factory=dict)
    explanation: str | None = None


class LLMEvaluationResult(BaseModel):
    """Result of an evaluation - also used as the structured output format for the LLM judge."""
    criteria: list[CriterionScore] = Field(
        description="Scores and feedback for each evaluation criterion"
    )
    explanation: str = Field(
        description="Overall assessment of the response"
    )

    @computed_field
    @property
    def score(self) -> float:
        """Average score across all criteria (0-1 normalized)."""
        if not self.criteria:
            return 0.0
        return sum(c.score for c in self.criteria) / len(self.criteria)

    @classmethod
    def error(cls, message: str) -> "LLMEvaluationResult":
        """Create an error result."""
        return cls(criteria=[], explanation=message)
    
    def to_evaluation_result(self) -> EvaluationResult:
        details = {c.name: c for c in self.criteria}
        return EvaluationResult(
            score=self.score,
            details=details,
            explanation=self.explanation
        )

@dataclass
class EvaluationContext:
    original_files: dict[str, str] | None
    modified_files: dict[str, str] | None
    task_prompt: str | None
    files_changed: dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        for name, content in self.modified_files.items():
            original_content = self.original_files.get(name, "")
            if original_content != content:
                self.files_changed[name] = content


class EvaluationStrategy:
    """
    A class to define evaluation strategies for the MBSE benchmark.

    Attributes:
        type (str): The type of evaluation strategy.
    """
    type: str

    async def evaluate(self, response: str, task: Task, context: EvaluationContext) -> EvaluationResult:
        pass


class LLMJudgmentStrategy(EvaluationStrategy):
    """
    A class to define evaluation strategies based on LLM judgments.

    Attributes:
        type (str): The type of evaluation strategy.
        config (LlmJudgeConfig): Configuration for the LLM judge.
    """
    type: str = "llm_judgment"

    def __init__(self, config: LlmJudgeConfig, client: AsyncOpenAI):
        self.config = config
        self.client = client

    async def evaluate(self, response: str, task: Task, context: EvaluationContext) -> EvaluationResult:
        """Evaluate a response using an LLM as a judge."""
        criteria = task.evaluation.criteria or ["accuracy", "completeness", "clarity"]
        prompt = self._build_prompt(response, task, criteria, context)
        
        for _ in range(self.config.max_attempts):
            try:
                result = await self.client.beta.chat.completions.parse(
                    model=self.config.model_id,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert evaluator for AI benchmark tasks."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=self.config.max_tokens,
                    response_format=LLMEvaluationResult,
                    temperature=self.config.temperature,
                )

                parsed = result.choices[0].message.parsed
                if parsed is not None:
                    return parsed.to_evaluation_result()

            except Exception as error:
                return LLMEvaluationResult.error(f"LLM judge failed: {str(error)}").to_evaluation_result()

        if parsed is None:
            return LLMEvaluationResult.error("LLM judge returned no parsed response").to_evaluation_result()

    def _build_prompt(
        self,
        response: str,
        task: Task,
        criteria: list[str],
        context: EvaluationContext | None
    ) -> str:
        """Build the evaluation prompt for the LLM judge."""
        rubric = task.evaluation.rubric or {}

        prompt = f"""You are evaluating an AI response for a benchmark task.

## Task Information
- **Name**: {task.name}
- **Description**: {task.description}
- **Prompt given to AI**: {task.prompt}
"""

        if context and context.original_files and len(context.original_files) > 0:
            prompt += "\n## Original Files (provided to AI)\n"
            for path, content in context.original_files.items():
                prompt += f"\n### {path}\n```\n{content}\n```\n"

        if context and context.files_changed and len(context.files_changed) > 0:
            prompt += "\n## Modified Files (after AI changes)\n"
            for path, content in context.files_changed.items():
                prompt += f"\n### {path}\n```\n{content}\n```\n"

        prompt += f"\n## AI Response\n{response}\n"

        prompt += """
## Evaluation Criteria and Rubric
Score each criterion from 0.0 to 1.0 based on the rubric:
"""
        for c in criteria:
            rubric_text = rubric.get(c, "Evaluate based on quality and correctness.")
            prompt += f"\n### {c}\n{rubric_text}\n"

        return prompt


def create_llm_judge_strategy(config: LlmJudgeConfig, client: AsyncOpenAI) -> EvaluationStrategy:
    """Factory function to create an LLMJudgmentStrategy."""
    return LLMJudgmentStrategy(config, client)


def get_evaluation_strategy(strategy_type: str, llm_judge_config: Optional[LlmJudgeConfig], client: AsyncOpenAI) -> EvaluationStrategy:
    """Factory function to get the appropriate evaluation strategy."""
    if strategy_type == "llm-judge":
        return create_llm_judge_strategy(llm_judge_config, client)
    else:
        raise ValueError(f"Unknown evaluation strategy type: {strategy_type}")


def evaluate_task(task: Task, response: str, context: EvaluationContext, client: AsyncOpenAI) -> EvaluationResult:
    """Evaluate a task response using the specified evaluation strategy."""
    strategy = get_evaluation_strategy(task.evaluation.type, task.llm_judge_config, client)
    return strategy.evaluate(response, task, context)