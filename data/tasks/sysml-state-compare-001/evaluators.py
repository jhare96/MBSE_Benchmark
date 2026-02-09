"""Evaluators for sysml-state-compare-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="SysML v2 State Machine Comparison Evaluation",
    weight=3.0,
    criteria=["comparison_thoroughness", "equivalence_analysis", "scenario_quality", "structural_understanding"],
    rubric={
        "comparison_thoroughness": """
        1.0: Correctly identifies all state differences (hovering in A, waiting in B) and all transition differences (emergency→idle in B only, flying→hovering vs flying→waiting).
        0.5: Identifies most differences but misses some details.
        0.0: Fails to identify major differences.
        """,
        "equivalence_analysis": """
        1.0: Correctly determines that machines are NOT behaviorally equivalent due to: (1) different intermediate state names (hovering vs waiting) which may have different semantics, and (2) emergency→idle transition in B but not in A. Explains reasoning clearly.
        0.5: Correct determination but weak or incomplete reasoning.
        0.0: Incorrect determination or no reasoning.
        """,
        "scenario_quality": """
        1.0: Provides valid input sequence that demonstrates difference, such as [StartupSignal, TakeoffSignal, LandSignal, TakeoffSignal] showing hovering vs waiting, or [StartupSignal, TakeoffSignal, EmergencySignal, ResetSignal] showing emergency→landed→idle vs emergency→idle. Clearly explains the different paths.
        0.5: Scenario provided but explanation unclear or incomplete.
        0.0: No scenario or invalid scenario.
        """,
        "structural_understanding": """
        1.0: Demonstrates understanding of state machine structure, recognizes that state names matter (hovering vs waiting suggests different semantics), and identifies that both reachability and state semantics affect equivalence.
        0.5: Basic structural understanding but misses nuances.
        0.0: Poor understanding of state machine concepts.
        """
    }
)
