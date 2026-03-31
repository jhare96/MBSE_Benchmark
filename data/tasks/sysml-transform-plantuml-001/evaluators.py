"""Evaluators for sysml-transform-plantuml-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="SysML v2 to PlantUML Diagram Transformation Evaluation",
    weight=2.0,
    criteria=["plantuml_validity", "relationship_mapping", "visual_clarity", "completeness"],
    rubric={
        "plantuml_validity": """
        1.0: Valid PlantUML code that starts with @startuml, ends with @enduml, uses correct syntax for classes, stereotypes, and relationships.
        0.5: Mostly valid but minor syntax issues.
        0.0: Invalid PlantUML that won't render.
        """,
        "relationship_mapping": """
        1.0: Correct PlantUML relationships - part def → class with <<part def>>, :> → <|--, part usages → *--, attributes as class members with types.
        0.5: Most relationships correct but some mapping errors.
        0.0: Major relationship mapping errors.
        """,
        "visual_clarity": """
        1.0: Diagram would render clearly with logical layout, readable labels, appropriate use of stereotypes and grouping.
        0.5: Renders but layout or labels could be clearer.
        0.0: Confusing or unreadable diagram.
        """,
        "completeness": """
        1.0: All major elements from model included (all part defs, key relationships, important attributes).
        0.5: Most elements included but some notable omissions.
        0.0: Many elements missing.
        """
    }
)
