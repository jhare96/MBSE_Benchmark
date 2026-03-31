"""Evaluators for sysml-extract-interfaces-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="SysML v2 Interface Extraction Evaluation",
    weight=1.5,
    criteria=["completeness", "json_validity", "endpoint_accuracy"],
    rubric={
        "completeness": """
        1.0: Extracts the VerbalCommunication interface def and all 4 interface usages (verbalAdultCommunicationActionWoman, verbalAdultCommunicationActionMan, verbalParentingCommunicationActionWoman, and one more).
        0.5: Finds the interface def but misses some usages.
        0.0: Misses the interface def.
        """,
        "json_validity": """
        1.0: Valid JSON array with correct object structure including 'name' and 'ends' fields.
        0.5: Valid JSON but minor structural issues.
        0.0: Invalid JSON.
        """,
        "endpoint_accuracy": """
        1.0: Correctly identifies both ends of VerbalCommunication: communicationPartnerA (VerbalExchange, not conjugate) and communicationPartnerB (~VerbalExchange, conjugate). Understands ~ prefix means conjugate.
        0.5: Identifies ends but conjugate flag incorrect.
        0.0: Wrong end names or types.
        """
    }
)
