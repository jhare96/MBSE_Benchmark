"""Evaluators for sysml-transform-todoc-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="SysML v2 Model to Documentation Transformation Evaluation",
    weight=2.0,
    criteria=["completeness", "accuracy", "documentation_quality", "structure"],
    rubric={
        "completeness": """
        1.0: Documents all packages (FFDS_Core, FFDS_Objectives, FFDS_Variants, FFDS_Configurations), system elements, and objectives with their IDs (OBJ-B1, OBJ-S1, OBJ-S2).
        0.5: Most elements documented but missing some packages or objectives.
        0.0: Major elements missing from documentation.
        """,
        "accuracy": """
        1.0: All IDs, names, and documentation strings accurately transcribed from the model (e.g., ffds system, 'Market Leader', 'Reliable Detection').
        0.5: Minor transcription errors in names or doc strings.
        0.0: Significant inaccuracies or invented content.
        """,
        "documentation_quality": """
        1.0: Clear, well-organized markdown with proper headings, readable explanations of each element's purpose.
        0.5: Adequate but could be clearer or better organized.
        0.0: Poorly written or confusing documentation.
        """,
        "structure": """
        1.0: Follows requested structure (System Overview, Package Structure, Component List, Objectives, Attributes) with clear hierarchy.
        0.5: Has most sections but organization could be improved.
        0.0: Lacks clear structure or missing major sections.
        """
    }
)
