"""Evaluators for sysml-generate-messages-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="SysML v2 Signal and Message Definition Generation Evaluation",
    weight=2.0,
    criteria=["signal_structure", "port_correctness", "message_flow"],
    rubric={
        "signal_structure": """
        1.0: All three signals defined as attribute defs with proper payload attributes (StartCommand, StopCommand, StatusReport).
        0.5: Signals present but some missing or incomplete.
        0.0: Fewer than 2 signals or wrong structure.
        """,
        "port_correctness": """
        1.0: Port definitions specify correct signal types with proper directionality (ControllerPort sends commands/receives status, DevicePort opposite).
        0.5: Ports defined but some signals or directions incorrect.
        0.0: Ports missing or fundamentally wrong.
        """,
        "message_flow": """
        1.0: Message statements correctly show communication flow (Controller sends StartCommand to Device, Device sends StatusReport to Controller).
        0.5: Message flow present but incomplete or partially incorrect.
        0.0: No message statements or completely wrong.
        """
    }
)
