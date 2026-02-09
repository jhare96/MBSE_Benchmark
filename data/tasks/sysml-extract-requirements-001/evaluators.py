"""Evaluators for sysml-extract-requirements-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="SysML v2 Requirement Extraction Evaluation",
    weight=2.0,
    criteria=["completeness", "structure_accuracy", "constraint_extraction"],
    rubric={
        "completeness": """
        1.0: All 17 requirement definitions extracted: TemperatureRegulationReqDef, CoolingFunctionReqDef, HeatingFunctionReqDef, DefrostingReqDef, AirQualityControlReqDef, UserInterfaceReqDef, PerformanceReqDef, ReliabilityReqDef, PowerConsumptionReqDef, NoiseLevelsReqDef, ElectricalSystemInterfaceReqDef, EngineInterfaceReqDef, UserInterfaceAccessibilityReqDef, TestingReqDef, UserFeedbackReqDef, GlossaryReqDef, ReferencesReqDef.
        0.5: 12-16 requirements extracted.
        0.0: Fewer than 12 requirements.
        """,
        "structure_accuracy": """
        1.0: Each object has correct 'name', 'doc', 'attributes', and 'constraint' fields with proper values. Doc text accurately extracted from /* */ comments.
        0.5: Structure mostly correct but some fields missing or malformed.
        0.0: Incorrect structure.
        """,
        "constraint_extraction": """
        1.0: Constraint expressions accurately extracted, e.g., 'abs(actualTemperature - setTemperature) <= 1' for TemperatureRegulationReqDef.
        0.5: Most constraints correct but some truncated or modified.
        0.0: Constraints missing or wrong.
        """
    }
)
