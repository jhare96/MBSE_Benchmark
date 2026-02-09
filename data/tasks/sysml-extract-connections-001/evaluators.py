"""Evaluators for sysml-extract-connections-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="SysML v2 Connection Extraction Evaluation",
    weight=1.5,
    criteria=["completeness", "json_validity", "connection_accuracy"],
    rubric={
        "completeness": """
        1.0: Extracts all ~25 connect statements including AngleProductionLine internal chain (materialIn→Heating, Heating→Bending, Bending→Cutting, Cutting→Drilling, Drilling→Grinding, Grinding→Polishing, Polishing→productOut), Manufacturer internal connections, and external connections (Customer↔Manufacturer, Supplier↔Manufacturer).
        0.5: Extracts 15-24 connections.
        0.0: Extracts fewer than 15 connections.
        """,
        "json_validity": """
        1.0: Valid JSON array with objects containing 'source' and 'target' fields.
        0.5: Valid JSON but inconsistent structure.
        0.0: Invalid JSON.
        """,
        "connection_accuracy": """
        1.0: Source and target references exactly match the model syntax (e.g., 'Heating.productOut' not 'heating.output').
        0.5: Most references correct but some have naming errors.
        0.0: Many references incorrect or fabricated.
        """
    }
)
