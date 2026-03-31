"""Evaluators for sysml-transform-refactor-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="SysML v2 Model Refactoring - Extract Port Definitions Evaluation",
    weight=2.0,
    criteria=["semantic_preservation", "correct_imports", "proper_separation", "sysml_syntax_validity"],
    rubric={
        "semantic_preservation": """
        1.0: All functionality identical after refactoring - all port definitions (ForcePort) properly separated and referenced correctly in both packages.
        0.5: Most functionality preserved but minor issues in references.
        0.0: Semantic changes or broken references.
        """,
        "correct_imports": """
        1.0: LawnmowerModel package correctly imports PortDefinitions with proper syntax (e.g., import PortDefinitions::*; or import PortDefinitions::ForcePort;).
        0.5: Import present but syntax issues or incomplete.
        0.0: Missing or incorrect imports.
        """,
        "proper_separation": """
        1.0: Clean separation - all port defs in PortDefinitions package, all other definitions (Engine, Wheel, etc.) in LawnmowerModel, no duplicate definitions.
        0.5: Mostly separated but some misplaced elements.
        0.0: Poor separation or elements in wrong packages.
        """,
        "sysml_syntax_validity": """
        1.0: Both output files are valid SysML v2 with proper package syntax and no errors.
        0.5: Minor syntax errors in one file.
        0.0: Major syntax errors or invalid SysML v2.
        """
    }
)
