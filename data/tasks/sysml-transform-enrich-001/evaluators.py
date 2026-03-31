"""Evaluators for sysml-transform-enrich-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="SysML v2 Model Enrichment with Documentation Evaluation",
    weight=1.5,
    criteria=["documentation_quality", "structure_preservation", "completeness", "technical_accuracy"],
    rubric={
        "documentation_quality": """
        1.0: Clear, concise, technically accurate doc strings for all part defs, port defs explaining purpose and role. Professional quality comments explaining relationships.
        0.5: Documentation present but could be clearer or more complete.
        0.0: Poor or missing documentation.
        """,
        "structure_preservation": """
        1.0: All original element names, types, and relationships exactly preserved - no changes to structure, only additions of documentation/metadata.
        0.5: Minor unintended changes to structure.
        0.0: Significant structural changes.
        """,
        "completeness": """
        1.0: Every part def, port def has doc string; sensible default values added to numeric attributes; complex relationships have explanatory comments; appropriate metadata annotations.
        0.5: Most elements documented but some gaps.
        0.0: Many elements lack documentation.
        """,
        "technical_accuracy": """
        1.0: Documentation correctly describes what each element does based on the model context and typical networking/internet concepts.
        0.5: Mostly accurate but some descriptions unclear or slightly wrong.
        0.0: Inaccurate or misleading documentation.
        """
    }
)
