"""Evaluators for sysml-invalid-keywords-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="SysML v2 Invalid Keywords Detection Evaluation",
    weight=1.5,
    criteria=["error_count", "correction_accuracy", "sysml_v2_knowledge"],
    rubric={
        "error_count": """
        1.0: Identifies all 10 keyword errors.
        0.5: Identifies 6-9 errors.
        0.0: Identifies fewer than 6 errors or reports many false positives.
        """,
        "correction_accuracy": """
        1.0: All corrections are correct - 'packge'→'package', 'imprt'→'import', 'prt'→'part', 'atribute'→'attribute', 'partdef'→'part def' (two words), 'dfe'→'def', 'specliaizes'→'specializes', 'asert'→'assert', 'constrant'→'constraint', 'packege'→'package'.
        0.5: Most corrections correct but 2-3 wrong.
        0.0: Majority of corrections wrong.
        """,
        "sysml_v2_knowledge": """
        1.0: Demonstrates understanding that 'part def' is two words in SysML v2, recognizes all valid keyword spellings, and doesn't flag correct keywords as errors.
        0.5: Some confusion about valid keywords.
        0.0: Poor understanding of SysML v2 keywords.
        """
    }
)
