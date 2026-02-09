"""Evaluators for sysml-req-coverage-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="Requirement Coverage Analysis Evaluation",
    weight=2.5,
    criteria=["coverage_accuracy", "gap_identification", "suggestions_quality"],
    rubric={
        "coverage_accuracy": """
        1.0: Correctly identifies satisfied vs unsatisfied requirements. Recognizes TemperatureRegulationReq and CoolingFunctionReq as satisfied, and correctly identifies unsatisfied requirements.
        0.5: Mostly correct but misses some satisfied/unsatisfied categorizations.
        0.0: Significant errors in categorization.
        """,
        "gap_identification": """
        1.0: Clearly identifies all gaps in coverage with specific requirement names that lack satisfy relationships.
        0.5: Identifies some gaps but misses several.
        0.0: Poor gap identification.
        """,
        "suggestions_quality": """
        1.0: Provides logical, specific component suggestions for unsatisfied requirements (e.g., suggests Compressor for cooling, Heater for heating, Sensor for performance monitoring).
        0.5: Provides suggestions but they are generic or partially incorrect.
        0.0: No meaningful suggestions.
        """
    }
)
