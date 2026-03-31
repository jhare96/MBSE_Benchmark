"""Evaluators for sysml-state-complex-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="SysML v2 Complex State Machine Analysis Evaluation",
    weight=2.5,
    criteria=["parallel_understanding", "action_identification", "guard_recognition", "completeness"],
    rubric={
        "parallel_understanding": """
        1.0: Correctly identifies both parallel regions (operatingStates and healthStates) with their respective states. Understands that they run concurrently.
        0.5: Identifies parallel structure but misses details or doesn't explain concurrent nature.
        0.0: Fails to recognize parallel regions.
        """,
        "action_identification": """
        1.0: Correctly identifies all entry actions (performSelfTest, initializeSystems, runDiagnostics), exit action (applyParkingBrake), and do activities (providePower, senseTemperature, runDiagnostics).
        0.5: Identifies most actions but misses some or categorizes incorrectly.
        0.0: Misses majority of actions or completely incorrect.
        """,
        "guard_recognition": """
        1.0: Identifies the guard condition 'if (selfTestPassed)' on the starting→on transition.
        0.5: Mentions guard conditions but incorrectly.
        0.0: Does not identify guard conditions.
        """,
        "completeness": """
        1.0: Provides comprehensive analysis covering all states in both regions (operatingStates: off, starting, on; healthStates: normal, degraded, maintenance) and all transitions between them.
        0.5: Analysis covers most elements but missing significant details.
        0.0: Incomplete or superficial analysis.
        """
    }
)
