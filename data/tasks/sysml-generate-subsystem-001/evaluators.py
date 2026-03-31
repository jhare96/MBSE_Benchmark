"""Evaluators for sysml-generate-subsystem-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="SysML v2 Complete Subsystem Generation Evaluation",
    weight=3.0,
    criteria=["completeness", "syntax_validity", "architecture_quality", "requirement_integration"],
    rubric={
        "completeness": """
        1.0: All required elements present (3 part defs with attributes, port defs, subsystem part with connections, 2 requirements).
        0.5: Most elements present but some missing.
        0.0: Major elements missing.
        """,
        "syntax_validity": """
        1.0: All SysML v2 syntax valid (package, imports, part def, port def, connect statements).
        0.5: Minor syntax errors.
        0.0: Major syntax errors.
        """,
        "architecture_quality": """
        1.0: Components properly structured with ports, connections make sense (GPS→Calculator→Display), subsystem integrates parts correctly.
        0.5: Structure present but connections incomplete or illogical.
        0.0: Poor or no architectural structure.
        """,
        "requirement_integration": """
        1.0: Two requirements properly defined with constraints (accuracy within 5m, calculation within 2s) using ISQ types.
        0.5: Requirements present but constraints weak or incomplete.
        0.0: Requirements missing or not integrated.
        """
    }
)
