"""Evaluators for sysml-analyze-dependencies-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="SysML v2 Package Dependency Analysis Evaluation",
    weight=1.5,
    criteria=["dependency_identification", "graph_accuracy", "circular_detection", "completeness"],
    rubric={
        "dependency_identification": """
        1.0: Correctly identifies ForestFireObservationDrone imports Drone_SharedAssetsSuperset::** and any other import statements.
        0.5: Finds some imports but misses others or misidentifies the imported package.
        0.0: Cannot identify import dependencies.
        """,
        "graph_accuracy": """
        1.0: Dependency graph correctly shows direction of dependencies (importing package depends on imported package).
        0.5: Graph present but direction unclear or some edges wrong.
        0.0: No graph or completely incorrect.
        """,
        "circular_detection": """
        1.0: Correctly identifies whether circular dependencies exist (none in this model).
        0.5: Attempts detection but with errors.
        0.0: Does not address circular dependencies.
        """,
        "completeness": """
        1.0: Identifies the ForestFireObservationDrone package and all its imports, plus references to external types (Drone, DroneEngine, BatteryCapacityKind, etc.).
        0.5: Finds main package but misses some cross-references.
        0.0: Missing major elements.
        """
    }
)
