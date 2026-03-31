"""Evaluators for sysml-analyze-constraints-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="SysML v2 Constraint Analysis Evaluation",
    weight=2.0,
    criteria=["constraint_understanding", "violation_examples", "clarity", "completeness"],
    rubric={
        "constraint_understanding": """
        1.0: Correctly interprets all constraint expressions (e.g., abs(actualTemperature - setTemperature) <= 1 means temperature must stay within 1 degree, responseTime <= maxResponseTime means quick response required).
        0.5: Understands most constraints but misinterprets some.
        0.0: Fundamentally misunderstands constraint semantics.
        """,
        "violation_examples": """
        1.0: Provides concrete, realistic violation scenarios for each constraint (e.g., 'temperature at 25°C when set to 22°C violates the 1-degree tolerance').
        0.5: Some violation examples but not for all constraints or examples are vague.
        0.0: No meaningful violation examples.
        """,
        "clarity": """
        1.0: Explanations are clear, concise, and use plain language accessible to non-experts.
        0.5: Explanations understandable but verbose or slightly confusing.
        0.0: Explanations unclear or too technical.
        """,
        "completeness": """
        1.0: Analyzes all 17 requirement definitions in the HVAC model.
        0.5: Covers most requirements (12-16).
        0.0: Covers fewer than half of the requirements.
        """
    }
)
