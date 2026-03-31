"""Evaluators for sysml-analyze-variations-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="SysML v2 Variation Point Analysis Evaluation",
    weight=2.0,
    criteria=["variation_identification", "variant_description", "difference_explanation", "completeness"],
    rubric={
        "variation_identification": """
        1.0: Correctly identifies the adoption_certificate variation point (with its 3 variants).
        0.5: Partially identifies the variation point or mischaracterizes it.
        0.0: Cannot identify the adoption_certificate variation point.
        """,
        "variant_description": """
        1.0: For adoption_certificate: correctly describes TypeB1 (adoption with woman as parent1), TypeB2 (adoption with man as parent1), and TypeC (adoption with both adoptive parents).
        0.5: Describes the variants but with some inaccuracies or missing details.
        0.0: Variants not properly described.
        """,
        "difference_explanation": """
        1.0: Clearly explains what differs among the adoption_certificate variants: they differ in which adults serve as the adoptive parents and how parent roles are assigned.
        0.5: Some differences are explained but not all or not clearly.
        0.0: No meaningful difference explanation.
        """,
        "completeness": """
        1.0: Covers the adoption_certificate variation point and all three variants with their relevant attributes and relationships.
        0.5: Most relevant content covered, but some aspects of variants or their attributes are missing.
        0.0: Major omissions.
        """
    }
)
