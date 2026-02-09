"""Evaluators for sysml-analyze-topology-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="SysML v2 Connection Topology Analysis Evaluation",
    weight=2.5,
    criteria=["topology_understanding", "pattern_recognition", "flow_direction", "completeness"],
    rubric={
        "topology_understanding": """
        1.0: Correctly identifies the three main actors (Customer, Manufacturer, Supplier) and Manufacturer's internal structure (Sales, Production, Storage, Dispatch, Procurement, ProductionScheduling).
        0.5: Identifies main structure but misses some components.
        0.0: Does not understand the topology.
        """,
        "pattern_recognition": """
        1.0: Identifies AngleProductionLine as a linear chain (Heating→Bending→Cutting→Drilling→Grinding→Polishing) and Manufacturer as the central hub connecting Customer and Supplier.
        0.5: Identifies some patterns but misses important ones.
        0.0: Cannot recognize patterns.
        """,
        "flow_direction": """
        1.0: Correctly interprets port directions (in/out, ~PortDef for conjugate) to determine flow direction. Identifies bidirectional communication between Customer and Manufacturer.
        0.5: Some flow directions correct but others wrong.
        0.0: Does not understand flow direction.
        """,
        "completeness": """
        1.0: Documents all major connections including internal Manufacturer connections and external connections to Customer/Supplier.
        0.5: Most connections documented.
        0.0: Missing many connections.
        """
    }
)
