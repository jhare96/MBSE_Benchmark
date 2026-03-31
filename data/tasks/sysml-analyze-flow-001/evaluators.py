"""Evaluators for sysml-analyze-flow-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="SysML v2 Action Flow Tracing Evaluation",
    weight=2.0,
    criteria=["flow_tracing", "sequence_accuracy", "completeness"],
    rubric={
        "flow_tracing": """
        1.0: Correctly traces the cutgrass action flow: start → 'Start Engine' → 'Push mower' → 'Shutoff mower' → done using first/then keywords.
        0.5: Identifies the flow but misses some steps or order.
        0.0: Cannot trace the action flow.
        """,
        "sequence_accuracy": """
        1.0: All action names exactly match the model ('Start Engine', 'Push mower', 'Shutoff mower') and order is correct.
        0.5: Some action names slightly wrong or order partially incorrect.
        0.0: Major errors in action names or sequence.
        """,
        "completeness": """
        1.0: Identifies the cutgrass action, its parent (lawnmower), and all sub-actions. Also notes any other actions in the model.
        0.5: Finds main flow but misses context.
        0.0: Missing major components.
        """
    }
)
