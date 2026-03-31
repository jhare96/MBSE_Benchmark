"""Evaluators for sysml-advanced-quality-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="SysML v2 Model Quality Assessment Evaluation",
    weight=3.0,
    criteria=["assessment_thoroughness", "scoring_justification", "issue_identification", "recommendations_quality"],
    rubric={
        "assessment_thoroughness": """
        1.0: Evaluates all 5 quality dimensions (naming, documentation, modularity, completeness, complexity) with detailed analysis of each.
        0.5: Evaluates most dimensions but some analysis is superficial.
        0.0: Missing evaluations or very superficial analysis.
        """,
        "scoring_justification": """
        1.0: Each score is well-justified with specific examples from the model. Justifications are clear and objective.
        0.5: Scores are justified but examples are vague or limited.
        0.0: Scores lack proper justification.
        """,
        "issue_identification": """
        1.0: Identifies concrete, specific issues with clear examples (e.g., 'typo in line 49: awakake should be awake', 'undocumented ports in VerbalExchange').
        0.5: Identifies some issues but they are vague or generic.
        0.0: Fails to identify specific issues.
        """,
        "recommendations_quality": """
        1.0: Provides actionable, prioritized recommendations that would meaningfully improve the model.
        0.5: Recommendations are generic or not clearly actionable.
        0.0: No useful recommendations provided.
        """
    }
)
