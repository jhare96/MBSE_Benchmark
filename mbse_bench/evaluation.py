from dataclasses import dataclass, field
from openai import AsyncOpenAI
from pydantic import BaseModel, Field, computed_field
from typing import Optional
from mbse_bench.filesystem import FileSystem
from mbse_bench.models import Task, LlmJudgeConfig

RUBRIC_TEMPLATES = {
    "syntax_validity": """
        Score 1.0 if:
        - Valid SysML v2 syntax
        - No parse errors
        - Proper structure
        
        Score 0.0 if:
        - Parse errors
        - Invalid syntax
    """,

    "stdlib_usage": """
        Score 1.0 if:
        - Appropriate use of standard library features
        - No reinventing the wheel
        Score 0.5 if:
        - Some use of stdlib but also some custom implementations where stdlib would suffice
        Score 0.0 if:
        - No use of stdlib when it would be appropriate
        """,
    
    "completeness": """
        Score 1.0 if all requirements from the task prompt are addressed.
        Score proportional to the percentage of requirements met.
        Score 0.0 if major requirements are missing.
    """,
    
    "clarity": """
        Score 1.0 if:
        - Code is well-organized
        - Names are descriptive
        - Structure is logical
        
        Score 0.5 if acceptable but could be clearer.
        Score 0.0 if confusing or poorly structured.
    """
}


class CriterionScore(BaseModel):
    """Score for a single evaluation criterion."""
    name: str
    score: float = Field(ge=0.0, le=1.0)
    feedback: str = ""

@dataclass
class EvaluationResult:
    """Result of an evaluation."""
    weight: float # relative weight of this evaluation in the overall score calculation
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
    
    def to_evaluation_result(self, weight: float) -> EvaluationResult:
        details = {c.name: c for c in self.criteria}
        return EvaluationResult(
            score=self.score,
            details=details,
            explanation=self.explanation,
            weight=weight
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


class Eval:
    """
    A class to define evaluation strategies for the MBSE benchmark.

    Attributes:
        name (str): The name of the evaluation strategy.
        weight (float): The weight of this evaluation in the overall score.
    """
    name: str
    weight: float

    async def evaluate(self, response: str, task: Task, context: EvaluationContext) -> EvaluationResult:
        pass

@dataclass
class LLMJudgmentEval(Eval):
    """
    A class to define evaluation strategies based on LLM judgments.

    Attributes:
        name (str): The name of the evaluation strategy.
        weight (float): The weight of this evaluation in the overall score.
        criteria (list[str]): The evaluation criteria to be used by the LLM judge.
        rubric (dict[str, str]): A rubric providing guidance for each criterion.
        config (LlmJudgeConfig): Configuration for the LLM judge.
        client (AsyncOpenAI): The OpenAI client to use for making API calls.
    """
    name: str = "LLM Judgment"
    weight: float = 1.0
    criteria: list[str] = field(default_factory=lambda: list(RUBRIC_TEMPLATES.keys()))
    rubric: dict[str, str] = field(default_factory=lambda: RUBRIC_TEMPLATES.copy())
    config: LlmJudgeConfig = None
    client: AsyncOpenAI = None


    async def evaluate(self, response: str, task: Task, context: EvaluationContext) -> EvaluationResult:
        """Evaluate a response using an LLM as a judge."""
        prompt = self._build_prompt(response, task, context)
        
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
                    return parsed.to_evaluation_result(self.weight)

            except Exception as error:
                return LLMEvaluationResult.error(f"LLM judge failed: {str(error)}").to_evaluation_result(self.weight)

        if parsed is None:
            return LLMEvaluationResult.error("LLM judge returned no parsed response").to_evaluation_result(self.weight)

    def _build_prompt(
        self,
        response: str,
        task: Task,
        context: EvaluationContext | None
    ) -> str:
        """Build the evaluation prompt for the LLM judge."""

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
        for c in self.criteria:
            rubric_text = self.rubric.get(c, "Evaluate based on quality and correctness.")
            prompt += f"\n### {c}\n{rubric_text}\n"

        return prompt


def discover_evals(evaluator_path: str) -> list[Eval]:
    """
    Discover all Eval instances in an evaluators.py file.
    
    Args:
        evaluator_path: Path to evaluators.py file
        
    Returns:
        List of Eval instances found in the module
    """
    import importlib.util
    from pathlib import Path
    
    path = Path(evaluator_path)
    if not path.exists():
        return []
    
    # Load module dynamically
    spec = importlib.util.spec_from_file_location("evaluators", path)
    if spec is None or spec.loader is None:
        return []
    
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Find all Eval instances (not classes, actual objects)
    eval_instances = []
    for name in dir(module):
        # Skip private/magic attributes
        if name.startswith('_'):
            continue
        
        obj = getattr(module, name)
        
        # Check if it's an instance of Eval
        if isinstance(obj, Eval):
            eval_instances.append(obj)
    
    return eval_instances


async def evaluate_task(task: Task, response: str, context: EvaluationContext, client: AsyncOpenAI) -> list[EvaluationResult]:
    """
    Evaluate a task response by discovering and running all Eval instances in evaluators.py.
    
    If evaluators.py exists, discovers all Eval instances and runs each one.
    Falls back to default LLM judge if no evaluators.py or no Evals found.
    
    Returns:
        List of EvaluationResult, one per Eval instance
    """
    from pathlib import Path
    
    # Try to find evaluators.py in task directory
    evaluator_path = Path(task.task_dir) / "evaluators.py"
    
    # Discover Eval instances
    eval_instances = discover_evals(str(evaluator_path))
    
    if not eval_instances:
        # Fallback to default LLM judge
        default_eval = LLMJudgmentEval(
            config=task.llm_judge_config,
            client=client
        )
        result = await default_eval.evaluate(response, task, context)
        return [result]
    
    # Run all discovered Evals
    results = []
    for eval_instance in eval_instances:
        try:
            # Run evaluation
            if isinstance(eval_instance, LLMJudgmentEval):
                eval_instance.config = task.llm_judge_config
                eval_instance.client = client
            
            result = await eval_instance.evaluate(response, task, context)
            results.append(result)
        except Exception as e:
            print(f"Warning: Failed to run eval {eval_instance.name}: {e}")
            # Add error result
            results.append(EvaluationResult(
                weight=eval_instance.weight,
                score=0.0,
                details={},
                explanation=f"Eval {eval_instance.name} failed: {str(e)}"
            ))
    
    return results