"""Evaluators for sysml-generate-calc-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="SysML v2 Calculation Definition Generation Evaluation",
    weight=2.0,
    criteria=["calc_structure", "type_correctness", "computation_logic"],
    rubric={
        "calc_structure": """
        1.0: All three calculations defined with proper calc def syntax, in parameters, and return statements (FuelConsumption, TotalMass, Range).
        0.5: Calculations present but some missing elements.
        0.0: Fewer than 2 calculations or wrong structure.
        """,
        "type_correctness": """
        1.0: All parameters and returns use appropriate ISQ types (LengthValue, VolumeValue, MassValue) per specification.
        0.5: Types mostly correct but some inappropriate choices.
        0.0: Types missing or fundamentally wrong.
        """,
        "computation_logic": """
        1.0: Calculation expressions are logically correct (consumption = fuel/distance, total = sum, range = capacity/rate).
        0.5: Logic partially correct but some errors.
        0.0: Computation logic incorrect or missing.
        """
    }
)
