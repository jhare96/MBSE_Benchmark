"""Evaluators for sysml-analyze-individuals-001 task."""
from dataclasses import field
from mbse_bench.evaluation import LLMJudgmentEval

# LLM judge evaluation with task-specific criteria
llm_judge = LLMJudgmentEval(
    name="SysML v2 Definitions vs Individuals Analysis Evaluation",
    weight=1.5,
    criteria=["definition_vs_instance", "relationship_understanding", "sysml_v2_concepts", "completeness"],
    rubric={
        "definition_vs_instance": """
        1.0: Correctly identifies definitions (Person, Child, Adoption_Certificate, Administrative_Document, etc.) vs usages (adult, judge, woman, man, child, adoptiveParent_1, adoptiveParent_2). Understands that 'part def' creates a type while 'part name : Type' creates an instance.
        0.5: Some confusion between definitions and usages.
        0.0: Cannot distinguish definitions from instances.
        """,
        "relationship_understanding": """
        1.0: Correctly traces typing: judge :> adult, adult : Person, child : Child. Understands :> for subsetting/specialization and : for typing.
        0.5: Some relationships correct but others wrong.
        0.0: Does not understand typing relationships.
        """,
        "sysml_v2_concepts": """
        1.0: Demonstrates understanding of SysML v2 concepts: connection def for associations (Child connects mother and father), redefinition syntax (:>>), multiplicity notation ([1], [*]).
        0.5: Partial understanding.
        0.0: Does not understand SysML v2 semantics.
        """,
        "completeness": """
        1.0: Identifies all major definitions and usages in the Family package.
        0.5: Most elements found.
        0.0: Missing many elements.
        """
    }
)
