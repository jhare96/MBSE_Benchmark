"""Evaluators for sysml-req-derivation-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="Requirement Derivation Evaluation",
    weight=2.5,
    criteria=["derivation_quality", "traceability", "sysml_syntax"],
    rubric={
        "derivation_quality": """
        1.0: Derives logical, relevant component requirements for all three components (Compressor, Temperature Sensor, Control Unit) that properly decompose system requirements. Includes proper SysML v2 syntax.
        0.5: Derives requirements for 2 components or requirements are partially relevant, or has minor syntax issues.
        0.0: Poor or missing derivations.
        """,
        "traceability": """
        1.0: Includes explicit derive relationships linking component requirements back to system requirements (e.g., derive from TemperatureRegulationReqDef, CoolingFunctionReqDef, PerformanceReqDef).
        0.5: Some traceability but incomplete or unclear.
        0.0: No traceability.
        """,
        "sysml_syntax": """
        1.0: Uses proper SysML v2 syntax for requirement def, attributes, constraints, and derive relationships. No major syntax errors that would prevent parsing.
        0.5: Mostly correct syntax with minor issues.
        0.0: Significant syntax errors.
        """
    }
)
