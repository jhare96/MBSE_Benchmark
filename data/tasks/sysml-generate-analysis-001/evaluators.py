"""Evaluators for sysml-generate-analysis-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="SysML v2 Analysis Case Generation Evaluation",
    weight=3.0,
    criteria=["analysis_structure", "objective_definition", "parameter_completeness", "action_flow"],
    rubric={
        "analysis_structure": """
        1.0: Analysis def with proper structure (subject, objective, parameters, actions, return).
        0.5: Analysis present but some structural elements missing.
        0.0: Not using analysis def or fundamentally wrong structure.
        """,
        "objective_definition": """
        1.0: Objective references temperature requirements with clear goal for thermal analysis.
        0.5: Objective present but vague or not linked to requirements.
        0.0: No objective or meaningless.
        """,
        "parameter_completeness": """
        1.0: All three input parameters defined with ISQ types (ambientTemperature, powerDissipation, airflowRate) plus return value.
        0.5: Most parameters present but some missing or wrong types.
        0.0: Parameters missing or incorrect.
        """,
        "action_flow": """
        1.0: Action steps represent logical analysis workflow (calculate heat transfer, simulate temperature, verify limits) that make sense for thermal analysis.
        0.5: Actions present but flow illogical or incomplete.
        0.0: No actions or meaningless steps.
        """
    }
)
