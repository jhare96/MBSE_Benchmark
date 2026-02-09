"""Evaluators for sysml-analyze-specialization-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="SysML v2 Specialization Relationship Analysis Evaluation",
    weight=1.5,
    criteria=["completeness", "accuracy", "hierarchy_clarity"],
    rubric={
        "completeness": """
        1.0: All specialization relationships found (SalesOrder, MaterialOrder, ProductOrder, PurchaseOrder, Inquiry, OrderQuotation, OrderConfirmation all specialize GeneralOrder).
        0.5: Most relationships found but missing 1-2.
        0.0: Missing more than half of the relationships.
        """,
        "accuracy": """
        1.0: All child-parent pairs correctly identified with correct 'kind' (item def).
        0.5: Some relationships have wrong parent or kind.
        0.0: Majority of relationships incorrectly identified.
        """,
        "hierarchy_clarity": """
        1.0: Hierarchy diagram clearly shows GeneralOrder as root with all specializations as children.
        0.5: Hierarchy present but formatting is unclear or incomplete.
        0.0: No hierarchy provided or completely wrong structure.
        """
    }
)
