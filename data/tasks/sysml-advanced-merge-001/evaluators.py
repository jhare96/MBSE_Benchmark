"""Evaluators for sysml-advanced-merge-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="SysML v2 Model Merge and Integration Evaluation",
    weight=3.5,
    criteria=["merge_completeness", "conflict_resolution", "integration_quality", "assumptions_documented", "syntactic_validity"],
    rubric={
        "merge_completeness": """
        1.0: Successfully merges all elements from both models. All structural and behavioral definitions are present and integrated.
        0.5: Merges most elements but some are missing or not integrated.
        0.0: Only includes elements from one model or fails to integrate them.
        """,
        "conflict_resolution": """
        1.0: Identifies and resolves all naming conflicts and type mismatches appropriately. Solutions are clear and well-justified.
        0.5: Resolves some conflicts but misses others or solutions are suboptimal.
        0.0: Ignores conflicts or creates invalid resolutions.
        """,
        "integration_quality": """
        1.0: Behavioral elements are properly connected to structural elements using appropriate SysML v2 constructs (perform, state allocations, etc.). Connections are semantically correct.
        0.5: Some integration but relationships are incomplete or incorrect.
        0.0: No meaningful integration between structure and behavior.
        """,
        "assumptions_documented": """
        1.0: All assumptions and integration decisions are clearly documented with comments. Explains why specific choices were made.
        0.5: Some documentation but key decisions are not explained.
        0.0: No documentation of assumptions.
        """,
        "syntactic_validity": """
        1.0: Output is valid SysML v2 syntax that could be parsed. Proper package structure, imports, and element definitions.
        0.5: Mostly valid but has some minor syntax issues.
        0.0: Invalid syntax or not SysML v2.
        """
    }
)
