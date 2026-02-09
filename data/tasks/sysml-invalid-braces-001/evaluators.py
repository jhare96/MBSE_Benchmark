"""Evaluators for sysml-invalid-braces-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="SysML v2 Missing Braces Detection Evaluation",
    weight=1.0,
    criteria=["error_detection", "location_accuracy", "fix_suggestion"],
    rubric={
        "error_detection": """
        1.0: Identifies exactly 2 missing closing braces. Does not claim 'NO ERRORS FOUND'.
        0.5: Identifies 1 of 2 missing braces.
        0.0: Claims no errors or identifies wrong errors.
        """,
        "location_accuracy": """
        1.0: Correctly locates both errors - (1) Missing closing brace for 'state def StopWatch' and (2) Missing closing brace for 'package StopWatchStates'.
        0.5: One location correct.
        0.0: Both locations wrong.
        """,
        "fix_suggestion": """
        1.0: Suggests adding two closing braces '}' at the end of the file, one for StopWatch and one for the package.
        0.5: Suggests fix but with wrong placement.
        0.0: No fix suggested or completely wrong fix.
        """
    }
)
