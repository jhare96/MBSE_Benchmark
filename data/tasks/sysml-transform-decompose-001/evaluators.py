"""Evaluators for sysml-transform-decompose-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="SysML v2 Model Decomposition into Multiple Packages Evaluation",
    weight=2.5,
    criteria=["proper_decomposition", "correct_imports", "semantic_preservation", "organization_quality", "sysml_syntax_validity"],
    rubric={
        "proper_decomposition": """
        1.0: Clean separation - Definitions package has all part/port/interface/connection/item/attribute defs, Actions package has action/use case defs, States package has state defs, Model package has part usages and model instances.
        0.5: Mostly separated but some elements misplaced.
        0.0: Poor separation or elements in wrong packages.
        """,
        "correct_imports": """
        1.0: All four packages have correct import statements where needed (e.g., Model imports from Definitions, Actions, States using proper syntax like 'import Definitions::*;').
        0.5: Some imports present but incomplete or syntax errors.
        0.0: Missing or incorrect imports causing unresolved references.
        """,
        "semantic_preservation": """
        1.0: All functionality identical after decomposition - Person definition works the same, Family relationships preserved, use cases intact.
        0.5: Most functionality preserved but minor issues.
        0.0: Semantic changes or broken functionality.
        """,
        "organization_quality": """
        1.0: Logical, maintainable organization that improves code clarity and follows package separation best practices.
        0.5: Organized but could be improved.
        0.0: Poor organization or confusing structure.
        """,
        "sysml_syntax_validity": """
        1.0: All four output files are valid SysML v2 with proper package syntax.
        0.5: Minor syntax errors in one or two files.
        0.0: Major syntax errors across files.
        """
    }
)
