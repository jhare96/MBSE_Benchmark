"""Evaluators for sysml-transform-notation-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="SysML v2 to JSON Schema Translation Evaluation",
    weight=3.0,
    criteria=["semantic_preservation", "json_schema_validity", "type_mapping", "constraint_translation"],
    rubric={
        "semantic_preservation": """
        1.0: All SysML semantic relationships preserved in JSON Schema (ModelElement → Datatype → Integer/Boolean hierarchy, Format composition).
        0.5: Most relationships preserved but some missing.
        0.0: Semantic relationships lost.
        """,
        "json_schema_validity": """
        1.0: Valid JSON Schema Draft 7+ with $schema declaration, correct definitions structure, all required fields.
        0.5: Valid but missing some JSON Schema best practices.
        0.0: Invalid JSON Schema.
        """,
        "type_mapping": """
        1.0: Correct mappings - part def → object with properties, String → string type, Real → number, Boolean → boolean, specializes → allOf, [1] → required.
        0.5: Most mappings correct but some errors.
        0.0: Major mapping errors.
        """,
        "constraint_translation": """
        1.0: SysML constraints correctly translated to JSON Schema constraints (e.g., 'base_format.id == 1' → const or enum, minimum_value/maximum_value → minimum/maximum).
        0.5: Some constraints translated but incomplete.
        0.0: Constraints not translated.
        """
    }
)
