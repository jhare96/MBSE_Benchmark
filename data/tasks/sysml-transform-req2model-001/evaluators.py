"""Evaluators for sysml-transform-req2model-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="Natural Language Requirements to SysML v2 Model Transformation Evaluation",
    weight=2.5,
    criteria=["requirement_coverage", "id_preservation", "constraint_extraction", "semantic_accuracy", "sysml_syntax_validity"],
    rubric={
        "requirement_coverage": """
        1.0: All 10 requirements (REQ-001 through REQ-010) converted to requirement defs.
        0.7: 8-9 requirements covered.
        0.5: 6-7 requirements covered.
        0.0: Fewer than 6 requirements.
        """,
        "id_preservation": """
        1.0: All requirement IDs accurately preserved in names or metadata (e.g., NavigationSystemReq001 or <'REQ-001'>).
        0.5: Most IDs preserved but some missing or incorrect.
        0.0: IDs not preserved.
        """,
        "constraint_extraction": """
        1.0: Quantitative values correctly extracted as attributes with appropriate types (e.g., ±2 meters → Distance, 100ms → Time, 20% → Percentage) and expressed as constraints.
        0.5: Some values extracted but types or constraints incomplete.
        0.0: No proper constraint extraction.
        """,
        "semantic_accuracy": """
        1.0: Constraints accurately represent requirement logic (e.g., 'at least 1 kilometer' → range >= 1000[m], 'drops below 20%' → batteryLevel < 20).
        0.5: Constraints present but logic partially incorrect.
        0.0: Constraints don't match requirements.
        """,
        "sysml_syntax_validity": """
        1.0: Valid SysML v2 syntax with proper package structure, attribute declarations, and require constraint blocks.
        0.5: Minor syntax errors.
        0.0: Major syntax errors or not SysML v2.
        """
    }
)
