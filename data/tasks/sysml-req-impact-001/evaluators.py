"""Evaluators for sysml-req-impact-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="Requirement Change Impact Analysis Evaluation",
    weight=3.0,
    criteria=["impact_completeness", "trace_accuracy", "change_suggestions"],
    rubric={
        "impact_completeness": """
        1.0: Identifies vehicle_b and all its components (body, engine, transmission, axles, fuel tank, driveshaft) as affected. Calculates current mass (2410 kg) and new violation (610 kg over new limit).
        0.5: Identifies some affected components but misses key elements or calculations.
        0.0: Poor impact identification.
        """,
        "trace_accuracy": """
        1.0: Correctly traces satisfy relationship from vehicleMassRequirement to vehicle_b, and understands that all vehicle components contribute to mass.
        0.5: Partial tracing but incomplete.
        0.0: Poor or no tracing.
        """,
        "change_suggestions": """
        1.0: Provides specific, realistic suggestions for mass reduction (e.g., lighter materials for transmission, smaller fuel tank, weight reduction for heavy components like engine/transmission). Considers trade-offs (e.g., engine power vs. mass, fuel capacity vs. range).
        0.5: Provides suggestions but they are generic or lack detail.
        0.0: Poor or no suggestions.
        """
    }
)
