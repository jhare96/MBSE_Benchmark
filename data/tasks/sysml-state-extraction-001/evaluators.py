"""Evaluators for sysml-state-extraction-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="SysML v2 State Machine Extraction Evaluation",
    weight=2.0,
    criteria=["state_completeness", "transition_accuracy", "diagram_quality", "ambiguity_detection"],
    rubric={
        "state_completeness": """
        1.0: All 4 states identified (ready, running, paused, stopped) with correct initial state.
        0.5: 3 states found or missing initial state designation.
        0.0: Fewer than 3 states found.
        """,
        "transition_accuracy": """
        1.0: All transitions correctly identified with proper from-state, trigger (VehicleStartSignal, VehicleOnSignal, VehicleOffSignal), and to-state. Notes ambiguity in paused state having two transitions with same trigger.
        0.5: Most transitions correct but missing some or has minor errors.
        0.0: Majority of transitions incorrect or missing.
        """,
        "diagram_quality": """
        1.0: Clear ASCII diagram showing all states and transitions with proper flow direction.
        0.5: Diagram present but unclear or missing some elements.
        0.0: No diagram or completely incorrect.
        """,
        "ambiguity_detection": """
        1.0: Identifies that paused state has two outgoing transitions on VehicleOffSignal (ambiguity/non-determinism).
        0.5: Partial recognition of issues.
        0.0: No analysis of potential issues.
        """
    }
)
