"""Evaluators for sysml-extract-actions-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="SysML v2 Action Extraction Evaluation",
    weight=1.0,
    criteria=["json_validity", "action_extraction", "parameter_accuracy"],
    rubric={
        "json_validity": """
        1.0: Response is valid JSON with correct array structure containing objects with 'name', 'inputs', and 'outputs' fields.
        0.5: Valid JSON but minor structural issues (e.g., missing optional fields).
        0.0: Invalid JSON or completely wrong structure.
        """,
        "action_extraction": """
        1.0: All 3 action definitions extracted: VehicleStartSignal, VehicleOnSignal, VehicleOffSignal.
        0.5: Found 2 of 3 action definitions.
        0.0: Found fewer than 2 or included non-action elements.
        """,
        "parameter_accuracy": """
        1.0: Correctly identifies that all 3 actions have empty 'inputs' and 'outputs' arrays (no parameters defined).
        0.5: Most parameters correct but some fabricated or missing.
        0.0: Fabricates parameters that don't exist or misses existing ones.
        """
    }
)
