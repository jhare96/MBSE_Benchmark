"""Evaluators for sysml-generate-requirements-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="SysML v2 Requirement Generation from Natural Language Evaluation",
    weight=2.0,
    criteria=["requirement_completeness", "constraint_correctness", "doc_string_quality"],
    rubric={
        "requirement_completeness": """
        1.0: All three requirements defined (BatteryCapacityReq, ResponseTimeReq, OperatingTempReq) with attributes and constraints.
        0.5: 2 requirements present or some missing elements.
        0.0: Fewer than 2 requirements or missing key components.
        """,
        "constraint_correctness": """
        1.0: Constraint expressions correctly capture requirements (capacity >= 0.8, responseTime <= 100ms, temperature range -20°C to 50°C).
        0.5: Constraints present but logic partially incorrect.
        0.0: No constraints or completely wrong logic.
        """,
        "doc_string_quality": """
        1.0: Doc strings clearly describe each requirement in natural language matching the original specifications.
        0.5: Doc strings present but unclear or incomplete.
        0.0: No documentation or misleading descriptions.
        """
    }
)
