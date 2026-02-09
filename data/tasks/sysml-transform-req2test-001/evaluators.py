"""Evaluators for sysml-transform-req2test-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="SysML v2 Requirements to Verification Cases Transformation Evaluation",
    weight=3.0,
    criteria=["verification_completeness", "traceability", "test_logic", "constraint_mapping", "sysml_syntax_validity"],
    rubric={
        "verification_completeness": """
        1.0: Verification case created for each of the 17 HVAC requirements with proper structure (test setup, procedure, acceptance criteria).
        0.7: 14-16 verification cases.
        0.5: 10-13 verification cases.
        0.0: Fewer than 10.
        """,
        "traceability": """
        1.0: Each verification case has explicit 'verify' relationship linking back to its requirement (e.g., verify requirement HVACSystemRequirements::TemperatureRegulationReqDef).
        0.5: Some traceability but links incomplete or incorrect.
        0.0: No traceability links.
        """,
        "test_logic": """
        1.0: Test procedures are realistic and would actually verify the requirement (e.g., for temperature regulation: set target temp, measure actual, compare). Includes setup/preconditions.
        0.5: Procedures present but not fully realistic or missing setup.
        0.0: Test procedures missing or nonsensical.
        """,
        "constraint_mapping": """
        1.0: Acceptance criteria correctly derived from requirement constraints (e.g., abs(actualTemperature - setTemperature) <= 1 becomes verification constraint checking same condition).
        0.5: Some criteria present but not accurately mapped.
        0.0: Criteria don't match requirement constraints.
        """,
        "sysml_syntax_validity": """
        1.0: Valid SysML v2 verification package with proper verification def syntax, attribute declarations, assert constraints, verify relationships.
        0.5: Minor syntax errors.
        0.0: Major syntax errors or invalid SysML v2.
        """
    }
)
