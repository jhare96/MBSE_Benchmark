"""Evaluators for sysml-generate-variation-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="SysML v2 Specialization and Variation Generation Evaluation",
    weight=2.5,
    criteria=["specialization_correctness", "variation_syntax", "model_coherence"],
    rubric={
        "specialization_correctness": """
        1.0: All specializations use :> correctly (Sedan, SUV, Truck :> ElectricVehicle) with appropriate additional attributes.
        0.5: Specializations present but some incorrect or missing specific attributes.
        0.0: Specialization syntax wrong or not used.
        """,
        "variation_syntax": """
        1.0: Variation point defined with proper syntax (variation batteryType) and two variants (StandardBattery, ExtendedRangeBattery).
        0.5: Variation present but incomplete or incorrect syntax.
        0.0: No variation or fundamentally wrong.
        """,
        "model_coherence": """
        1.0: Base type has common attributes (batteryCapacity, range, weight), specializations add vehicle-specific attributes, variation fits logically.
        0.5: Model mostly coherent but some inconsistencies.
        0.0: Model incoherent or attributes misplaced.
        """
    }
)
