"""Evaluators for sysml-advanced-patterns-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="SysML v2 Modeling Pattern Recognition Evaluation",
    weight=3.0,
    criteria=["pattern_identification", "evidence_quality", "benefit_analysis", "completeness"],
    rubric={
        "pattern_identification": """
        1.0: Correctly identifies all 5 patterns (or correctly identifies their absence) with clear understanding of each pattern's characteristics.
        0.5: Identifies most patterns but misses some or has partial understanding.
        0.0: Fails to identify major patterns present in the model.
        """,
        "evidence_quality": """
        1.0: Provides specific, concrete evidence for each pattern with element names and examples from the model (e.g., 'Engine definition at line 46, engine usage at line 19').
        0.5: Provides some evidence but it is vague or incomplete.
        0.0: Claims patterns exist without providing evidence.
        """,
        "benefit_analysis": """
        1.0: Clearly explains the benefits of each identified pattern in the context of this specific model. Shows understanding of why patterns matter.
        0.5: Generic benefits that could apply to any model.
        0.0: No benefit analysis provided.
        """,
        "completeness": """
        1.0: Analyzes all 5 requested patterns. For missing patterns, provides recommendations for how they could be added.
        0.5: Analyzes most patterns but skips some.
        0.0: Only analyzes 1-2 patterns.
        """
    }
)
