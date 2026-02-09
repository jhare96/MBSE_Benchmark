"""Evaluators for sysml-generate-individual-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="SysML v2 Individual Definition Generation Evaluation",
    weight=2.0,
    criteria=["individual_syntax", "specialization_correct", "attribute_binding"],
    rubric={
        "individual_syntax": """
        1.0: Individual definitions use proper individual def syntax and individual part usages in Fleet.
        0.5: Individual syntax attempted but some errors.
        0.0: Does not use individual def or fundamentally wrong syntax.
        """,
        "specialization_correct": """
        1.0: Both Vehicle_001 and Vehicle_002 correctly specialize Vehicle_Type_A using :> syntax.
        0.5: Specialization present but incorrect or incomplete.
        0.0: No specialization or wrong approach.
        """,
        "attribute_binding": """
        1.0: Each individual has specific attribute values bound (VIN123/VIN456, dates as specified).
        0.5: Some attributes bound but incomplete or incorrect values.
        0.0: No attribute binding or all values wrong.
        """
    }
)
