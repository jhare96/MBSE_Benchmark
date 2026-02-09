"""Evaluators for sysml-semantic-validity-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="SysML v2 Semantic Validity Check Evaluation",
    weight=2.0,
    criteria=["semantic_understanding", "reference_checking", "completeness"],
    rubric={
        "semantic_understanding": """
        1.0: Correctly distinguishes semantic errors (undefined references, type mismatches) from syntax errors. Understands that imports must exist, types must be defined before use, and specializations must reference valid parent types.
        0.5: Some confusion between semantic and syntactic issues.
        0.0: Does not understand semantic validation.
        """,
        "reference_checking": """
        1.0: Identifies undefined references including: UndefinedPackage import, UndefinedType::speed, PowerUnit::watt, RoadInterfacePort, startEngine action, Gasoline, FuelCommand, TorqueValue, TorqueOutput, MotorTorque, MassUnit::kilogram, SportsCar, TurboEngine, AutomaticTransmission, inputPort. Also identifies invalid specialization (FrontAxle :> RearAxle should be :> Axle).
        0.5: Identifies 8-14 of the 17 errors.
        0.0: Identifies fewer than 8 errors or many false positives.
        """,
        "completeness": """
        1.0: Provides specific location and suggested fix for each error (e.g., 'FuelCommand should be FuelCmd').
        0.5: Identifies errors but without context or fixes.
        0.0: Very incomplete analysis.
        """
    }
)
