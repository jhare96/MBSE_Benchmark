"""Evaluators for sysml-generate-states-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="SysML v2 State Machine Generation Evaluation",
    weight=2.5,
    criteria=["state_completeness", "transition_accuracy", "syntax_validity", "timing_correctness"],
    rubric={
        "state_completeness": """
        1.0: All four states defined (Red, Yellow, Green, Emergency) with proper state def syntax.
        0.5: States present but some missing or incomplete.
        0.0: Fewer than 3 states or wrong structure.
        """,
        "transition_accuracy": """
        1.0: All transitions correct (Red→Green, Green→Yellow, Yellow→Red, any→Emergency) with proper source and target.
        0.5: Most transitions correct but some missing or wrong.
        0.0: Transitions fundamentally incorrect or mostly missing.
        """,
        "syntax_validity": """
        1.0: All SysML v2 state machine syntax valid (state def, transition, first, accept, then keywords).
        0.5: Minor syntax errors.
        0.0: Major syntax errors preventing interpretation.
        """,
        "timing_correctness": """
        1.0: Time events correctly specified (after 30s, 25s, 5s) and EmergencySignal event for emergency transition.
        0.5: Timing present but some values incorrect.
        0.0: No timing or completely wrong.
        """
    }
)
