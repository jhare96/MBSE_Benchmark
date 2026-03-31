"""Evaluators for sysml-analyze-crossref-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="SysML v2 Cross-Model Reference Analysis Evaluation",
    weight=2.5,
    criteria=["cross_reference_tracing", "import_understanding", "dependency_mapping", "completeness"],
    rubric={
        "cross_reference_tracing": """
        1.0: Correctly traces that ForestFireObservationDrone uses types from external packages (Drone, DroneEngine, BatteryCapacityKind, PropKind, DroneBatteryVariation). Identifies Drone_BaseArchitecture defines the base Drone part def.
        0.5: Finds some cross-references but misses others.
        0.0: Cannot trace cross-file references.
        """,
        "import_understanding": """
        1.0: Understands import semantics: 'import Drone_SharedAssetsSuperset::**' brings in all elements, 'import RequirementDerivation::*' for requirements. Notes that Drone_BaseArchitecture has no imports.
        0.5: Partial understanding of imports.
        0.0: Does not understand import statements.
        """,
        "dependency_mapping": """
        1.0: Creates accurate dependency map showing: Drone_BaseArchitecture is independent, Drone_SystemArchitecture depends on Drone_BaseArchitecture, both requirement packages reference the architecture.
        0.5: Map partially correct.
        0.0: No meaningful dependency map.
        """,
        "completeness": """
        1.0: Analyzes both provided files, identifies all packages (Drone_BaseArchitecture, Drone_StakeholderRequirements, Drone_SystemArchitecture, Drone_SystemRequirements, ForestFireObservationDrone), and all cross-references.
        0.5: Most content covered.
        0.0: Major omissions.
        """
    }
)
