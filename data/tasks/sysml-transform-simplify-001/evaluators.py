"""Evaluators for sysml-transform-simplify-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="SysML v2 Model Simplification - Black Box Abstraction Evaluation",
    weight=2.0,
    criteria=["simplification_quality", "interface_preservation", "usability", "abstraction_level"],
    rubric={
        "simplification_quality": """
        1.0: Removes internal implementation details (nested parts, internal attributes, implementation-specific connections) while keeping essential structure.
        0.5: Some simplification but retains unnecessary details.
        0.0: No meaningful simplification or removes too much.
        """,
        "interface_preservation": """
        1.0: All external ports, interfaces, and public APIs preserved exactly as in original model.
        0.5: Most interfaces preserved but minor elements missing.
        0.0: External interfaces changed or removed.
        """,
        "usability": """
        1.0: Result can be imported and used as a library - clear what inputs/outputs are available, suitable for integration with other models.
        0.5: Usable but not ideal for external consumption.
        0.0: Cannot be used as a library reference.
        """,
        "abstraction_level": """
        1.0: Appropriate black-box abstraction - shows what system does without exposing how it works internally.
        0.5: Abstraction present but level inconsistent.
        0.0: Still shows too much internal detail or abstracted too much.
        """
    }
)
