"""Evaluators for sysml-transform-statemachine-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="SysML v2 State Machine to Executable TypeScript Transformation Evaluation",
    weight=3.0,
    criteria=["code_validity", "state_preservation", "transition_logic", "type_safety", "executability"],
    rubric={
        "code_validity": """
        1.0: Valid TypeScript with no syntax errors, proper class/enum structure, correct method signatures.
        0.5: Minor syntax issues.
        0.0: Major syntax errors or not TypeScript.
        """,
        "state_preservation": """
        1.0: All states from model correctly represented (ready, running, paused, stopped) in enum or similar structure.
        0.5: Most states present but some missing or incorrect.
        0.0: States not properly represented.
        """,
        "transition_logic": """
        1.0: All transitions correctly implemented (ready→running on VehicleStartSignal, running→stopped on VehicleOnSignal, running→paused on VehicleOffSignal, paused→running on VehicleOffSignal, paused→stopped on VehicleOffSignal, stopped→done on VehicleOffSignal) with proper state guards.
        0.5: Most transitions present but some logic errors.
        0.0: Transitions not correctly implemented.
        """,
        "type_safety": """
        1.0: Proper TypeScript types for states, signals/events, and return values ensuring type safety at compile time.
        0.5: Some typing but not comprehensive.
        0.0: No meaningful type safety.
        """,
        "executability": """
        1.0: Code can be instantiated and executed - constructor sets initial state, methods can be called to trigger transitions, state changes are observable.
        0.5: Partially executable but missing some functionality.
        0.0: Cannot be executed or missing critical methods.
        """
    }
)
