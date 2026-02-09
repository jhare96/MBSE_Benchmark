"""Example evaluators - demonstrates multiple Eval instances."""

import sys
from pathlib import Path
import re

# mbse_bench is now a package
from mbse_bench.evaluation import Eval, EvaluationResult, EvaluationContext, CriterionScore
from mbse_bench.models import Task


class FileCreatedEval(Eval):
    """Check if requirements.txt was created."""
    
    name = "File Created"
    weight = 1.0
    
    async def evaluate(self, response: str, task: Task, context: EvaluationContext) -> EvaluationResult:
        """Check if the required file exists."""
        if "requirements.txt" in context.files_changed:
            return EvaluationResult(
                score=1.0,
                details={
                    "file_created": CriterionScore(
                        name="file_created",
                        score=1.0,
                        feedback="requirements.txt was created"
                    )
                },
                explanation="File created successfully"
            )
        else:
            return EvaluationResult(
                score=0.0,
                details={
                    "file_created": CriterionScore(
                        name="file_created",
                        score=0.0,
                        feedback="requirements.txt was not created"
                    )
                },
                explanation="File not created"
            )


class FormatCheckEval(Eval):
    """Check if requirements follow REQ-XXX format."""
    
    name = "Format Check"
    weight = 2.0
    
    async def evaluate(self, response: str, task: Task, context: EvaluationContext) -> EvaluationResult:
        """Check requirement format."""
        req_file = context.files_changed.get("requirements.txt", "")
        
        if not req_file:
            return EvaluationResult(
                score=0.0,
                details={
                    "format": CriterionScore(
                        name="format",
                        score=0.0,
                        feedback="No requirements file found"
                    )
                },
                explanation="No file to check format"
            )
        
        matches = re.findall(r'REQ-\d{3}:', req_file)
        
        if len(matches) > 0:
            return EvaluationResult(
                score=1.0,
                details={
                    "format": CriterionScore(
                        name="format",
                        score=1.0,
                        feedback=f"Found {len(matches)} requirements in correct format"
                    )
                },
                explanation=f"Format check passed: {len(matches)} requirements"
            )
        else:
            return EvaluationResult(
                score=0.0,
                details={
                    "format": CriterionScore(
                        name="format",
                        score=0.0,
                        feedback="No REQ-XXX format found"
                    )
                },
                explanation="Format check failed"
            )


# Create instances - these will be discovered and run
file_check = FileCreatedEval()
format_check = FormatCheckEval()

# You can create multiple instances with different configurations
format_check_strict = FormatCheckEval()
format_check_strict.name = "Strict Format Check"
format_check_strict.weight = 3.0
