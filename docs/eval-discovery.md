# Simple Eval Discovery System

## Overview

The evaluation system discovers all `Eval` **instances** in a task's `evaluators.py` file and runs them automatically.

## How It Works

1. **Discover**: System looks for `evaluators.py` in the task directory
2. **Find**: Discovers all variables that are instances of `Eval`
3. **Run**: Calls `evaluate()` on each instance
4. **Aggregate**: Combines results using weighted average

## Creating Evaluators

### Basic Structure

```python
# data/tasks/my-task/evaluators.py

from evaluation import Eval, EvaluationResult, EvaluationContext, CriterionScore
from models import Task

class MyCustomEval(Eval):
    """Description of what this evaluates."""
    
    name = "My Eval"
    weight = 1.0
    
    async def evaluate(self, response: str, task: Task, context: EvaluationContext) -> EvaluationResult:
        # Your evaluation logic here
        score = calculate_score(response)
        
        return EvaluationResult(
            score=score,
            details={
                "criterion": CriterionScore(
                    name="criterion",
                    score=score,
                    feedback="Explanation of score"
                )
            },
            explanation="Overall explanation"
        )

# Create an instance - this will be discovered
my_eval = MyCustomEval()
```

### Multiple Evaluators

Create multiple instances in one file:

```python
class SyntaxEval(Eval):
    name = "Syntax Check"
    weight = 1.0
    
    async def evaluate(self, response, task, context):
        # Check syntax
        pass

class ExtractionEval(Eval):
    name = "Extraction Accuracy"
    weight = 2.0
    
    async def evaluate(self, response, task, context):
        # Check extraction
        pass

# Create instances - these will be discovered
syntax_check = SyntaxEval()
extraction_check = ExtractionEval()

# You can create multiple instances of the same class with different configs
strict_syntax = SyntaxEval()
strict_syntax.name = "Strict Syntax Check"
strict_syntax.weight = 3.0
```

### Key Point: Create Instances!

The discovery system finds **instances**, not classes. You must create objects:

```python
# ✅ Correct - instances are discovered
my_eval = MyEval()
another_eval = AnotherEval()

# ❌ Wrong - classes alone won't be discovered
class MyEval(Eval):
    pass
# Missing: my_eval = MyEval()
```

### Using LLM Judge

For LLM-based evaluation, create instances of `LLMJudgmentEval`:

```python
from evaluation import LLMJudgmentEval, RUBRIC_TEMPLATES

# Create an instance with custom criteria
quality_eval = LLMJudgmentEval(
    name="Quality Check",
    weight=1.0,
    criteria=["accuracy", "completeness", "clarity"],
    rubric={
        "accuracy": "Score 1.0 if all elements are correct...",
        "completeness": "Score 1.0 if nothing is missing...",
        "clarity": "Score 1.0 if well-structured..."
    },
    config=None,  # Will be injected by runner
    client=None   # Will be injected by runner
)

# Or use default rubrics
simple_eval = LLMJudgmentEval(
    config=None,
    client=None
)
```

### Accessing Context

The `EvaluationContext` provides:

- `context.original_files` - Files before AI modifications
- `context.modified_files` - Files after AI modifications
- `context.files_changed` - Only the changed files
- `context.task_prompt` - The task prompt

Example:

```python
class FileCheckEval(Eval):
    name = "File Check"
    weight = 1.0
    
    async def evaluate(self, response, task, context):
        # Check if specific file was created
        if "output.txt" in context.files_changed:
            return EvaluationResult(score=1.0, details={}, explanation="File created")
        return EvaluationResult(score=0.0, details={}, explanation="File not created")
```

## Creating Multiple Instances

You can create multiple instances of the same class with different configurations:

```python
class ThresholdEval(Eval):
    def __init__(self, threshold: float, name: str = "Threshold Check"):
        self.name = name
        self.weight = 1.0
        self.threshold = threshold
    
    async def evaluate(self, response, task, context):
        score = calculate_score(response)
        return EvaluationResult(
            score=1.0 if score >= self.threshold else 0.0,
            details={},
            explanation=f"Score {score} vs threshold {self.threshold}"
        )

# Create multiple instances with different thresholds
lenient_check = ThresholdEval(threshold=0.5, name="Lenient Check")
strict_check = ThresholdEval(threshold=0.9, name="Strict Check")
```

## Fallback Behavior

If no `evaluators.py` file exists or no Eval classes are found, the system falls back to the default `LLMJudgmentEval`.

## Example: Complete Task Evaluator

```python
# data/tasks/sysml-extract-parts-001/evaluators.py

from evaluation import Eval, LLMJudgmentEval, EvaluationResult, CriterionScore
import json

class SyntaxEval(Eval):
    """Validate SysML syntax."""
    name = "Syntax Validation"
    weight = 1.0
    
    async def evaluate(self, response, task, context):
        from sysmlv2_parser import parse_sysml
        result = parse_sysml(response)
        
        if result.valid:
            return EvaluationResult(
                score=1.0,
                details={"syntax": CriterionScore(
                    name="syntax",
                    score=1.0,
                    feedback="Valid SysML v2 syntax"
                )},
                explanation="Syntax check passed"
            )
        else:
            return EvaluationResult(
                score=0.0,
                details={"syntax": CriterionScore(
                    name="syntax",
                    score=0.0,
                    feedback=f"{len(result.errors)} syntax errors"
                )},
                explanation="Syntax check failed"
            )


class ExtractionEval(Eval):
    """Check extracted parts."""
    name = "Part Extraction"
    weight = 2.0
    
    async def evaluate(self, response, task, context):
        from sysmlv2_parser import extract_parts
        
        expected_parts = ["GeneralOrder", "SalesOrder", "MaterialOrder"]
        
        try:
            actual = extract_parts(response)
            actual_names = {p["name"] for p in actual}
            
            matched = sum(1 for name in expected_parts if name in actual_names)
            score = matched / len(expected_parts)
            
            return EvaluationResult(
                score=score,
                details={"extraction": CriterionScore(
                    name="extraction",
                    score=score,
                    feedback=f"{matched}/{len(expected_parts)} parts extracted"
                )},
                explanation=f"Extraction: {score:.0%}"
            )
        except Exception as e:
            return EvaluationResult(
                score=0.0,
                details={"extraction": CriterionScore(
                    name="extraction",
                    score=0.0,
                    feedback=f"Extraction failed: {e}"
                )},
                explanation="Extraction failed"
            )


class QualityEval(LLMJudgmentEval):
    """LLM judges code quality."""
    name = "Code Quality"
    weight = 0.5
    criteria = ["clarity", "idiomaticity"]
    rubric = {
        "clarity": "Code is well-structured and readable",
        "idiomaticity": "Follows SysML v2 best practices"
    }
```

## Benefits

✅ **Simple** - Just create Eval classes, no registration needed
✅ **Flexible** - Mix deterministic and LLM-based evaluation
✅ **Composable** - Multiple independent evaluators per task
✅ **Weighted** - Each Eval has its own weight
✅ **Discoverable** - Automatically found and executed

## Task Structure

```
data/tasks/my-task/
├── task.json              # Task definition
├── evaluators.py          # Your Eval classes (auto-discovered)
├── files/                 # Input files
└── expected/              # Expected outputs (optional)
```

No changes needed to task.json - the system automatically looks for `evaluators.py`.
