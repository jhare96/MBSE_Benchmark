"""Evaluators for sysml-constraint-syntax-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="SysML v2 Constraint Syntax Validation Evaluation",
    weight=1.5,
    criteria=["constraint_understanding", "expression_validity", "explanation_quality"],
    rubric={
        "constraint_understanding": """
        1.0: Correctly understands all 8 constraints' purposes (temperature regulation, cooling, air quality, response time, interface status, safety, power, reliability).
        0.5: Understands most but misinterprets 2-3 constraints.
        0.0: Fundamentally misunderstands what the constraints verify.
        """,
        "expression_validity": """
        1.0: Correctly classifies all 8 constraints - VALID: TemperatureReq (abs() with comparison), AirQualityReq (&& operators), SafetyReq (|| operator), ReliabilityReq (>= comparison). INVALID: CoolingReq (missing operand after <=), ResponseTimeReq (dangling &&), InterfaceReq (= vs ==), PowerReq (missing closing brace).
        0.5: Gets 5-7 classifications correct.
        0.0: Gets fewer than 5 correct.
        """,
        "explanation_quality": """
        1.0: For each INVALID constraint, clearly explains the specific error (missing operand, wrong operator, unclosed brace).
        0.5: Identifies errors but explanations are vague or incomplete.
        0.0: Does not explain errors or gives wrong explanations.
        """
    }
)
