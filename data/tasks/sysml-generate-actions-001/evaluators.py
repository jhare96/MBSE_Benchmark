"""Evaluators for sysml-generate-actions-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="SysML v2 Action Definition Generation Evaluation",
    weight=2.0,
    criteria=["action_structure", "flow_correctness", "composability"],
    rubric={
        "action_structure": """
        1.0: All three actions defined with correct in/out parameters (GrindBeans, BrewCoffee, MakeCoffee).
        0.5: Actions present but parameters incomplete or incorrect.
        0.0: Missing actions or fundamentally wrong structure.
        """,
        "flow_correctness": """
        1.0: Flow connections properly link outputs to inputs (grind output flows to brew input).
        0.5: Flows present but some connections missing or incorrect.
        0.0: No flows or completely incorrect connections.
        """,
        "composability": """
        1.0: MakeCoffee correctly composes the two sub-actions with proper parameter binding and flow connections.
        0.5: Composition attempted but incomplete or partially incorrect.
        0.0: No composition or fundamentally wrong approach.
        """
    }
)
