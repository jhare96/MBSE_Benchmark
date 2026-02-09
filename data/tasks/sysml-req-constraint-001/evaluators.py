"""Evaluators for sysml-req-constraint-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="Constraint Verification with Calculation Evaluation",
    weight=2.5,
    criteria=["calculation_accuracy", "reasoning_quality", "constraint_verification"],
    rubric={
        "calculation_accuracy": """
        1.0: Correctly calculates total mass as 2410 kg (75+800+875+200+100+200+100+60) and identifies all component masses.
        0.5: Calculation mostly correct but misses one or two components or has minor arithmetic errors.
        0.0: Significant calculation errors.
        """,
        "reasoning_quality": """
        1.0: Clear step-by-step reasoning showing the constraint massActual <= 2000, calculated value 2410 kg, and conclusion that it FAILS because 2410 > 2000.
        0.5: Reasoning present but lacks clarity or specific values.
        0.0: Poor or missing reasoning.
        """,
        "constraint_verification": """
        1.0: Correctly identifies that the constraint FAILS and provides specific evidence (expected values: FAIL, 2410 kg, 2000 kg bound).
        0.5: Identifies failure but lacks specifics.
        0.0: Incorrect conclusion.
        """
    }
)
