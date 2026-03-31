"""Evaluators for sysml-extract-hierarchy-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="SysML v2 Hierarchy Extraction Evaluation",
    weight=2.0,
    criteria=["hierarchy_completeness", "relationship_accuracy", "structure_clarity"],
    rubric={
        "hierarchy_completeness": """
        1.0: All 18 parts included: factoryContext, Manufacturer, Customer, Supplier, Production, Storage, Sales, Procurement, ProductionScheduling, Dispatch, ProductionControl, AngleProductionLine, Heating, Bending, Cutting, Drilling, Grinding, Polishing.
        0.5: 12-17 parts included.
        0.0: Fewer than 12 parts.
        """,
        "relationship_accuracy": """
        1.0: All containment relationships correct - factoryContext contains {Manufacturer, Customer, Supplier}; Manufacturer contains {Production, Storage, Sales, Procurement, ProductionScheduling, Dispatch}; Production contains {ProductionControl, AngleProductionLine}; AngleProductionLine contains {Heating, Bending, Cutting, Drilling, Grinding, Polishing}.
        0.5: Most relationships correct but 1-3 parts misplaced.
        0.0: Major structural errors.
        """,
        "structure_clarity": """
        1.0: Hierarchy clearly shows 4 nesting levels with proper indentation or JSON structure.
        0.5: Structure present but formatting unclear.
        0.0: No hierarchical structure shown.
        """
    }
)
