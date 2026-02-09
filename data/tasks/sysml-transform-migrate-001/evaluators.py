"""Evaluators for sysml-transform-migrate-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="SysML v2 Model Pattern Migration and Modernization Evaluation",
    weight=2.5,
    criteria=["pattern_improvement", "semantic_preservation", "syntax_correctness", "best_practices"],
    rubric={
        "pattern_improvement": """
        1.0: Successfully modernizes patterns - PowerConnection becomes interface def with proper ends, direct assignments become redefinitions, PowerPort gets conjugation (~), redundant connections become bind statements.
        0.5: Some patterns updated but not all.
        0.0: No meaningful pattern updates.
        """,
        "semantic_preservation": """
        1.0: Model behavior identical after migration - same power flow, same relationships, same component structure. No functional changes.
        0.5: Minor semantic differences but mostly preserved.
        0.0: Significant semantic changes or broken functionality.
        """,
        "syntax_correctness": """
        1.0: All modernized patterns use correct SysML v2 syntax (interface def with 'end' statements, 'attribute redefines' syntax, '~' for conjugation, 'bind' statement syntax).
        0.5: Mostly correct but minor syntax issues.
        0.0: Incorrect syntax for modern patterns.
        """,
        "best_practices": """
        1.0: Result follows current SysML v2 best practices and conventions, improvements are appropriate and consistent throughout model.
        0.5: Some best practices followed but inconsistent.
        0.0: Does not follow best practices.
        """
    }
)
