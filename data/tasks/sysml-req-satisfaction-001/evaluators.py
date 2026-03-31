"""Evaluators for sysml-req-satisfaction-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="Requirement Satisfaction Identification Evaluation",
    weight=2.0,
    criteria=["relationship_identification", "constraint_analysis", "verification_insight"],
    rubric={
        "relationship_identification": """
        1.0: Correctly identifies all three satisfy relationships: vehicleMassRequirement satisfied by vehicle_b, vehicleFuelEconomyRequirement satisfied by vehicle_b, torqueGenerationRequirement satisfied by vehicle_b.engine.
        0.5: Identifies 2 out of 3 relationships.
        0.0: Identifies fewer than 2.
        """,
        "constraint_analysis": """
        1.0: Correctly analyzes constraints - mass constraint FAILS (calculated mass ~2410kg > 2000kg), fuel economy FAILS (14.5 < 15.0), torque PASSES (320 >= 300).
        0.5: Correctly analyzes 2 out of 3 constraints.
        0.0: Fewer than 2 correct.
        """,
        "verification_insight": """
        1.0: Shows clear calculation/reasoning for each constraint verification with specific values from the model.
        0.5: Provides reasoning but lacks specific values or calculations.
        0.0: No meaningful verification reasoning.
        """
    }
)
