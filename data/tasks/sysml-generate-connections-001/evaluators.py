"""Evaluators for sysml-generate-connections-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="SysML v2 Connection and Binding Generation Evaluation",
    weight=2.5,
    criteria=["connection_correctness", "type_compatibility", "interface_design"],
    rubric={
        "connection_correctness": """
        1.0: Connect statements properly link ports (sensor.dataOut to controller.sensorIn, controller.actuatorOut to actuator.commandIn).
        0.5: Connections present but some incorrect or missing.
        0.0: Connections wrong or missing.
        """,
        "type_compatibility": """
        1.0: Port types are compatible for connections (matching data types, proper in/out directionality).
        0.5: Types mostly compatible but some mismatches.
        0.0: Type incompatibilities prevent proper connections.
        """,
        "interface_design": """
        1.0: Both interfaces defined correctly (SensorInterface, ActuatorInterface) with compatible end types matching connected ports.
        0.5: Interfaces present but incomplete or partially incorrect.
        0.0: Interfaces missing or fundamentally wrong.
        """
    }
)
