"""Evaluators for sysml-transform-typescript-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="SysML v2 to TypeScript Interface Transformation Evaluation",
    weight=2.0,
    criteria=["typescript_validity", "type_mapping", "documentation", "semantic_preservation"],
    rubric={
        "typescript_validity": """
        1.0: Valid TypeScript that compiles without errors - proper interface syntax, correct type annotations, valid extends clauses.
        0.5: Mostly valid but minor TypeScript syntax errors.
        0.0: Invalid TypeScript with major syntax errors.
        """,
        "type_mapping": """
        1.0: Correct mappings - part def → interface, String → string, Real/Integer → number, Boolean → boolean, specializes → extends, [1] → required (non-optional), [*] → Type[].
        0.5: Most mappings correct but some errors.
        0.0: Major type mapping errors.
        """,
        "documentation": """
        1.0: JSDoc comments above each interface with clear descriptions, @property tags where appropriate.
        0.5: Some documentation but incomplete or not following JSDoc conventions.
        0.0: No meaningful documentation.
        """,
        "semantic_preservation": """
        1.0: All SysML relationships preserved in TypeScript (ModelElement as base, Datatype extends ModelElement, specific types extend Datatype).
        0.5: Most relationships preserved but some missing.
        0.0: Semantic relationships lost.
        """
    }
)
