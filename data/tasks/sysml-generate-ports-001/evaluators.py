"""Evaluators for sysml-generate-ports-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="SysML v2 Port and Interface Generation Evaluation",
    weight=1.5,
    criteria=["port_structure", "interface_correctness", "syntax_validity"],
    rubric={
        "port_structure": """
        1.0: Port definitions include correct in/out items with proper types (SensorPort outputs temperature and humidity, ControlPort accepts setpoint).
        0.5: Ports defined but some items missing or incorrect direction.
        0.0: Port structure fundamentally incorrect or missing.
        """,
        "interface_correctness": """
        1.0: Interface definition correctly connects two port ends (sensor and controller) using proper SysML v2 syntax.
        0.5: Interface present but incomplete or one end missing.
        0.0: No interface or completely incorrect structure.
        """,
        "syntax_validity": """
        1.0: All SysML v2 syntax is valid (package, imports, port def, interface def keywords used correctly).
        0.5: Minor syntax errors that don't prevent understanding.
        0.0: Major syntax errors or invalid SysML v2 code.
        """
    }
)
