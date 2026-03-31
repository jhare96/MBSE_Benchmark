"""
SysML v2 Syntax Validator

Validates SysML v2 textual notation for syntax correctness.

Reference: SysML v2 Language Specification
https://github.com/Systems-Modeling/SysML-v2-Release
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional
import re


class Severity(Enum):
    """Severity level of a syntax issue."""

    ERROR = auto()
    WARNING = auto()
    INFO = auto()


@dataclass
class SysMLSyntaxError:
    """A syntax error or warning found during validation."""

    line: int
    column: int
    message: str
    severity: Severity = Severity.ERROR

    def __str__(self) -> str:
        sev = self.severity.name.lower()
        return f"{sev} at {self.line}:{self.column}: {self.message}"


# Alias for backwards compatibility
SyntaxError = SysMLSyntaxError


@dataclass
class ValidationResult:
    """Result of syntax validation."""

    valid: bool
    errors: list[SyntaxError] = field(default_factory=list)
    warnings: list[SyntaxError] = field(default_factory=list)
    elements: dict = field(default_factory=dict)

    def __str__(self) -> str:
        if self.valid:
            return "Validation passed"
        return f"Validation failed: {len(self.errors)} errors, {len(self.warnings)} warnings"


# SysML v2 keywords
SYSML_V2_KEYWORDS = frozenset([
    "package",
    "part",
    "part def",
    "port",
    "port def",
    "attribute",
    "attribute def",
    "item",
    "item def",
    "action",
    "action def",
    "state",
    "state def",
    "requirement",
    "requirement def",
    "constraint",
    "constraint def",
    "interface",
    "interface def",
    "connection",
    "connection def",
    "import",
    "alias",
    "in",
    "out",
    "inout",
    "specializes",
    "subsets",
    "redefines",
    "ref",
    "connect",
    "bind",
    "flow",
    "stream",
    "message",
    "transition",
    "accept",
    "then",
    "first",
    "entry",
    "exit",
    "do",
    "calc",
    "calc def",
    "analysis",
    "case",
    "use case",
    "variation",
    "variant",
    "abstract",
    "individual",
    "assert",
    "assume",
    "require",
    "satisfy",
    "doc",
    "comment",
    "about",
    "allocation",
    "allocation def",
    "exhibit",
    "expose",
    "perform",
    "send",
    "rendering",
    "rendering def",
    "view",
    "view def",
    "viewpoint",
    "viewpoint def",
    "concern",
    "concern def",
    "stakeholder",
    "metadata",
    "metadata def",
    "occurrence",
    "occurrence def",
    "succession",
    "if",
    "else",
    "while",
    "loop",
    "for",
    "merge",
    "decide",
    "join",
    "fork",
    "filter",
])

# Valid definition starters
VALID_DEF_STARTERS = frozenset([
    "package",
    "part def",
    "part",
    "port def",
    "port",
    "attribute def",
    "attribute",
    "item def",
    "item",
    "action def",
    "action",
    "state def",
    "state",
    "requirement def",
    "requirement",
    "constraint def",
    "constraint",
    "interface def",
    "interface",
    "connection def",
    "connection",
    "calc def",
    "calc",
    "use case",
    "case",
    "variation",
    "variant",
    "abstract",
    "individual",
    "allocation def",
    "allocation",
    "view def",
    "view",
    "viewpoint def",
    "viewpoint",
    "rendering def",
    "rendering",
    "concern def",
    "concern",
    "stakeholder",
    "occurrence def",
    "occurrence",
    "metadata def",
    "metadata",
    "import",
    "alias",
    "comment",
    "doc",
    "ref",
    "exhibit",
    "perform",
    "assert",
    "assume",
    "satisfy",
    "expose",
    "bind",
    "connect",
    "flow",
    "succession",
    "transition",
    "accept",
    "send",
    "if",
    "else",
    "while",
    "loop",
    "for",
    "merge",
    "decide",
    "join",
    "fork",
    "filter",
    "entry",
    "exit",
    "do",
    "first",
    "then",
    "private",
    "public",
    "protected",
    "standard",
    "library",
])


class SysMLValidator:
    """
    Validates SysML v2 textual notation for syntax correctness.

    Example:
        >>> validator = SysMLValidator("package Vehicle { part engine : Engine; }")
        >>> result = validator.validate()
        >>> print(result.valid)
        True
    """

    def __init__(self, source: str):
        """
        Initialize the validator with source code.

        Args:
            source: The SysML v2 source code to validate.
        """
        self.source = source
        self.lines = source.split("\n")

    def validate(self) -> ValidationResult:
        """
        Validate the source code.

        Returns:
            A ValidationResult containing any errors and warnings.
        """
        errors: list[SyntaxError] = []
        warnings: list[SyntaxError] = []

        # Validate brace matching
        brace_errors = self._validate_brace_matching()
        errors.extend([e for e in brace_errors if e.severity == Severity.ERROR])
        warnings.extend([e for e in brace_errors if e.severity == Severity.WARNING])

        # Validate keywords
        keyword_errors = self._validate_keywords()
        errors.extend([e for e in keyword_errors if e.severity == Severity.ERROR])
        warnings.extend([e for e in keyword_errors if e.severity == Severity.WARNING])

        # Validate structure
        structure_errors = self._validate_structure()
        errors.extend([e for e in structure_errors if e.severity == Severity.ERROR])
        warnings.extend([e for e in structure_errors if e.severity == Severity.WARNING])

        # Count elements
        elements = self._count_elements()

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            elements=elements,
        )

    def _validate_brace_matching(self) -> list[SyntaxError]:
        """Validate that braces are properly matched."""
        errors: list[SyntaxError] = []
        stack: list[tuple[str, int, int]] = []  # (char, line, column)

        matching = {"{": "}", "(": ")", "[": "]"}
        opening = set(matching.keys())
        closing = {v: k for k, v in matching.items()}

        in_string = False
        in_block_comment = False
        string_char = ""

        for line_idx, line in enumerate(self.lines):
            col = 0
            while col < len(line):
                char = line[col]
                next_char = line[col + 1] if col + 1 < len(line) else ""

                # Handle block comments
                if not in_string and char == "/" and next_char == "*":
                    in_block_comment = True
                    col += 2
                    continue
                if in_block_comment and char == "*" and next_char == "/":
                    in_block_comment = False
                    col += 2
                    continue
                if in_block_comment:
                    col += 1
                    continue

                # Handle line comments
                if not in_string and char == "/" and next_char == "/":
                    break

                # Handle strings
                if char in ('"', "'"):
                    # Check if escaped
                    backslash_count = 0
                    for i in range(col - 1, -1, -1):
                        if line[i] == "\\":
                            backslash_count += 1
                        else:
                            break
                    is_escaped = backslash_count % 2 == 1

                    if not is_escaped:
                        if not in_string:
                            in_string = True
                            string_char = char
                        elif char == string_char:
                            in_string = False

                    col += 1
                    continue

                if in_string:
                    col += 1
                    continue

                # Check braces
                if char in opening:
                    stack.append((char, line_idx + 1, col + 1))
                elif char in closing:
                    expected_opening = closing[char]
                    if not stack:
                        errors.append(
                            SyntaxError(
                                line=line_idx + 1,
                                column=col + 1,
                                message=f"Unexpected closing '{char}' without matching opening brace",
                                severity=Severity.ERROR,
                            )
                        )
                    else:
                        last = stack.pop()
                        if last[0] != expected_opening:
                            errors.append(
                                SyntaxError(
                                    line=line_idx + 1,
                                    column=col + 1,
                                    message=f"Mismatched brace: expected '{matching[last[0]]}' but found '{char}'",
                                    severity=Severity.ERROR,
                                )
                            )

                col += 1

        # Check for unclosed braces
        for unclosed in stack:
            errors.append(
                SyntaxError(
                    line=unclosed[1],
                    column=unclosed[2],
                    message=f"Unclosed '{unclosed[0]}'",
                    severity=Severity.ERROR,
                )
            )

        return errors

    def _validate_keywords(self) -> list[SyntaxError]:
        """Validate that keywords are used correctly."""
        errors: list[SyntaxError] = []
        in_block_comment = False

        def_pattern = re.compile(r"^\s*(\w+(?:\s+\w+)?)\s+(\w+)\s*(?:\{|:>|;)")

        for line_idx, line in enumerate(self.lines):
            # Handle block comments
            processed_line = ""
            i = 0
            while i < len(line):
                if not in_block_comment:
                    start = line.find("/*", i)
                    if start == -1:
                        processed_line += line[i:]
                        break
                    processed_line += line[i:start]
                    in_block_comment = True
                    i = start + 2
                else:
                    end = line.find("*/", i)
                    if end == -1:
                        i = len(line)
                    else:
                        in_block_comment = False
                        i = end + 2

            # Skip if inside block comment
            if in_block_comment and len(processed_line.strip()) == 0:
                continue

            # Remove line comments
            comment_idx = processed_line.find("//")
            if comment_idx >= 0:
                processed_line = processed_line[:comment_idx]

            # Skip empty lines
            if len(processed_line.strip()) == 0:
                continue

            # Check for unknown keywords in definitions
            match = def_pattern.match(processed_line)
            if match:
                keyword = match.group(1).lower()
                if keyword not in VALID_DEF_STARTERS and keyword not in SYSML_V2_KEYWORDS:
                    if "{" in processed_line or ":>" in processed_line:
                        errors.append(
                            SyntaxError(
                                line=line_idx + 1,
                                column=processed_line.find(match.group(1)) + 1,
                                message=f"Unknown keyword or definition type: '{match.group(1)}'",
                                severity=Severity.WARNING,
                            )
                        )

        return errors

    def _validate_structure(self) -> list[SyntaxError]:
        """Validate structural aspects of the code."""
        errors: list[SyntaxError] = []
        in_block_comment = False

        for line_idx, line in enumerate(self.lines):
            # Handle block comments
            processed_line = ""
            i = 0
            while i < len(line):
                if not in_block_comment:
                    start = line.find("/*", i)
                    if start == -1:
                        processed_line += line[i:]
                        break
                    processed_line += line[i:start]
                    in_block_comment = True
                    i = start + 2
                else:
                    end = line.find("*/", i)
                    if end == -1:
                        i = len(line)
                    else:
                        in_block_comment = False
                        i = end + 2

            if in_block_comment and len(processed_line.strip()) == 0:
                continue

            # Remove line comments
            comment_idx = processed_line.find("//")
            if comment_idx >= 0:
                processed_line = processed_line[:comment_idx]

            # Check import statements
            import_match = re.match(r"^\s*import\s+(.+)$", processed_line)
            if import_match:
                import_path = import_match.group(1).strip()
                if not import_path.endswith(";"):
                    errors.append(
                        SyntaxError(
                            line=line_idx + 1,
                            column=len(processed_line),
                            message="Import statement must end with semicolon",
                            severity=Severity.ERROR,
                        )
                    )
                if "::" not in import_path and not import_path.startswith("*"):
                    errors.append(
                        SyntaxError(
                            line=line_idx + 1,
                            column=processed_line.find("import") + 1,
                            message="Import path should use '::' separator",
                            severity=Severity.WARNING,
                        )
                    )

        return errors

    def _count_elements(self) -> dict:
        """Count the number of each element type in the source."""
        source = self._remove_comments()

        return {
            "packages": len(re.findall(r"\bpackage\s+\w+", source)),
            "part_defs": len(re.findall(r"\bpart\s+def\s+\w+", source)),
            "parts": len(re.findall(r"\bpart\s+(?!def\b)\w+", source)),
            "port_defs": len(re.findall(r"\bport\s+def\s+\w+", source)),
            "ports": len(re.findall(r"\bport\s+(?!def\b)\w+", source)),
            "actions": len(re.findall(r"\b(?:action\s+def|action)\s+\w+", source)),
            "states": len(re.findall(r"\b(?:state\s+def|state)\s+\w+", source)),
            "requirements": len(re.findall(r"\b(?:requirement\s+def|requirement)\s+\w+", source)),
            "constraints": len(re.findall(r"\b(?:constraint\s+def|constraint)\s+\w+", source)),
            "connections": len(re.findall(r"\b(?:connect|connection)\s+\w+", source)),
        }

    def _remove_comments(self) -> str:
        """Remove comments from the source code."""
        source = self.source
        source = re.sub(r"/\*[\s\S]*?\*/", "", source)
        source = re.sub(r"//.*$", "", source, flags=re.MULTILINE)
        return source


def validate(source: str) -> ValidationResult:
    """
    Convenience function to validate SysML v2 source code.

    Args:
        source: The SysML v2 source code to validate.

    Returns:
        A ValidationResult containing validation results.
    """
    validator = SysMLValidator(source)
    return validator.validate()


def is_valid(source: str) -> bool:
    """
    Check if SysML v2 source code is syntactically valid.

    Args:
        source: The SysML v2 source code to check.

    Returns:
        True if the source is valid, False otherwise.
    """
    return validate(source).valid
