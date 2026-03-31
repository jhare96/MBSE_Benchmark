"""Evaluators for sysml-generate-usecase-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="SysML v2 Use Case Definition Generation Evaluation",
    weight=2.0,
    criteria=["usecase_structure", "actor_definition", "objective_clarity"],
    rubric={
        "usecase_structure": """
        1.0: All three use cases defined with proper use case def syntax (ArmSystem, DetectIntrusion, NotifyAuthorities).
        0.5: Use cases present but some missing or incomplete.
        0.0: Fewer than 2 use cases or wrong structure.
        """,
        "actor_definition": """
        1.0: Each use case correctly defines both subject and actor roles per specification (e.g., ArmSystem has Homeowner actor and SecurityPanel subject).
        0.5: Actors and subjects present but some roles incorrect.
        0.0: Missing or fundamentally wrong actor/subject assignments.
        """,
        "objective_clarity": """
        1.0: Each use case includes clear objective documentation describing its purpose.
        0.5: Objectives present but vague or incomplete.
        0.0: No objectives or meaningless descriptions.
        """
    }
)
