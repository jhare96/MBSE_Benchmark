"""
SysML v2 AST Node Types

Defines the Abstract Syntax Tree node types for the SysML v2 parser.

Reference: SysML v2 Language Specification
https://github.com/Systems-Modeling/SysML-v2-Release
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Optional


class Direction(Enum):
    """Port or parameter direction."""

    IN = auto()
    OUT = auto()
    INOUT = auto()


class Visibility(Enum):
    """Visibility modifier."""

    PUBLIC = auto()
    PRIVATE = auto()
    PROTECTED = auto()


@dataclass
class SourceLocation:
    """Source location information for an AST node."""

    line: int
    column: int
    end_line: int = 0
    end_column: int = 0

    def __repr__(self) -> str:
        return f"{self.line}:{self.column}"


@dataclass
class ASTNode:
    """Base class for all AST nodes."""

    location: Optional[SourceLocation] = None

    def accept(self, visitor: "ASTVisitor") -> Any:
        """Accept a visitor for traversal."""
        method_name = f"visit_{type(self).__name__}"
        method = getattr(visitor, method_name, visitor.visit_default)
        return method(self)


@dataclass
class CommentNode(ASTNode):
    """A comment (block or line)."""

    text: str = ""
    is_block: bool = False
    is_doc: bool = False


@dataclass
class ImportNode(ASTNode):
    """An import statement."""

    path: str = ""
    is_public: bool = False
    is_private: bool = False
    alias: Optional[str] = None
    is_wildcard: bool = False


@dataclass
class TypeReference(ASTNode):
    """A reference to a type."""

    name: str = ""
    qualified_name: Optional[str] = None
    multiplicity: Optional[str] = None


@dataclass
class Multiplicity(ASTNode):
    """Multiplicity specification like [0..*] or [1]."""

    lower: int = 1
    upper: Optional[int] = 1  # None means unbounded (*)
    is_ordered: bool = False
    is_nonunique: bool = False

    def __str__(self) -> str:
        if self.lower == self.upper:
            return f"[{self.lower}]"
        upper_str = "*" if self.upper is None else str(self.upper)
        return f"[{self.lower}..{upper_str}]"


@dataclass
class AttributeNode(ASTNode):
    """An attribute definition or usage."""

    name: str = ""
    type_ref: Optional[TypeReference] = None
    default_value: Optional[str] = None
    multiplicity: Optional[Multiplicity] = None
    is_readonly: bool = False
    is_derived: bool = False


@dataclass
class PortNode(ASTNode):
    """A port usage."""

    name: str = ""
    type_ref: Optional[TypeReference] = None
    direction: Optional[Direction] = None
    multiplicity: Optional[Multiplicity] = None
    is_conjugated: bool = False


@dataclass
class PortDefNode(ASTNode):
    """A port definition."""

    name: str = ""
    parent: Optional[str] = None
    attributes: list[AttributeNode] = field(default_factory=list)
    direction: Optional[Direction] = None
    doc: Optional[str] = None


@dataclass
class PartNode(ASTNode):
    """A part usage."""

    name: str = ""
    type_ref: Optional[TypeReference] = None
    multiplicity: Optional[Multiplicity] = None


@dataclass
class PartDefNode(ASTNode):
    """A part definition."""

    name: str = ""
    parent: Optional[str] = None
    is_abstract: bool = False
    is_individual: bool = False
    attributes: list[AttributeNode] = field(default_factory=list)
    ports: list[PortNode] = field(default_factory=list)
    parts: list[PartNode] = field(default_factory=list)
    actions: list["ActionNode"] = field(default_factory=list)
    states: list["StateNode"] = field(default_factory=list)
    connections: list["ConnectionNode"] = field(default_factory=list)
    doc: Optional[str] = None


@dataclass
class ConnectionNode(ASTNode):
    """A connection between elements."""

    name: Optional[str] = None
    source: str = ""
    target: str = ""
    via: Optional[str] = None


@dataclass
class BindingNode(ASTNode):
    """A binding connector."""

    source: str = ""
    target: str = ""


@dataclass
class ActionNode(ASTNode):
    """An action usage."""

    name: str = ""
    type_ref: Optional[TypeReference] = None
    inputs: list[AttributeNode] = field(default_factory=list)
    outputs: list[AttributeNode] = field(default_factory=list)
    body: list[ASTNode] = field(default_factory=list)


@dataclass
class ActionDefNode(ASTNode):
    """An action definition."""

    name: str = ""
    parent: Optional[str] = None
    is_abstract: bool = False
    inputs: list[AttributeNode] = field(default_factory=list)
    outputs: list[AttributeNode] = field(default_factory=list)
    body: list[ASTNode] = field(default_factory=list)
    doc: Optional[str] = None


@dataclass
class StateNode(ASTNode):
    """A state usage."""

    name: str = ""
    type_ref: Optional[TypeReference] = None
    is_initial: bool = False
    entry_action: Optional[str] = None
    exit_action: Optional[str] = None
    do_action: Optional[str] = None
    substates: list["StateNode"] = field(default_factory=list)
    transitions: list["TransitionNode"] = field(default_factory=list)


@dataclass
class StateDefNode(ASTNode):
    """A state definition."""

    name: str = ""
    parent: Optional[str] = None
    is_abstract: bool = False
    states: list[StateNode] = field(default_factory=list)
    transitions: list["TransitionNode"] = field(default_factory=list)
    doc: Optional[str] = None


@dataclass
class TransitionNode(ASTNode):
    """A transition between states."""

    name: Optional[str] = None
    source: str = ""
    target: str = ""
    trigger: Optional[str] = None
    guard: Optional[str] = None
    effect: Optional[str] = None


@dataclass
class RequirementNode(ASTNode):
    """A requirement usage."""

    name: str = ""
    type_ref: Optional[TypeReference] = None
    id: Optional[str] = None
    text: Optional[str] = None
    subject: Optional[str] = None
    constraints: list["ConstraintNode"] = field(default_factory=list)


@dataclass
class RequirementDefNode(ASTNode):
    """A requirement definition."""

    name: str = ""
    parent: Optional[str] = None
    id: Optional[str] = None
    text: Optional[str] = None
    subject: Optional[str] = None
    attributes: list[AttributeNode] = field(default_factory=list)
    constraints: list["ConstraintNode"] = field(default_factory=list)
    doc: Optional[str] = None


@dataclass
class ConstraintNode(ASTNode):
    """A constraint usage."""

    name: str = ""
    type_ref: Optional[TypeReference] = None
    expression: Optional[str] = None


@dataclass
class ConstraintDefNode(ASTNode):
    """A constraint definition."""

    name: str = ""
    parent: Optional[str] = None
    parameters: list[AttributeNode] = field(default_factory=list)
    expression: Optional[str] = None
    doc: Optional[str] = None


@dataclass
class ItemNode(ASTNode):
    """An item usage."""

    name: str = ""
    type_ref: Optional[TypeReference] = None
    multiplicity: Optional[Multiplicity] = None


@dataclass
class ItemDefNode(ASTNode):
    """An item definition."""

    name: str = ""
    parent: Optional[str] = None
    is_abstract: bool = False
    attributes: list[AttributeNode] = field(default_factory=list)
    doc: Optional[str] = None


@dataclass
class InterfaceNode(ASTNode):
    """An interface usage."""

    name: str = ""
    type_ref: Optional[TypeReference] = None
    ends: list[str] = field(default_factory=list)


@dataclass
class InterfaceDefNode(ASTNode):
    """An interface definition."""

    name: str = ""
    parent: Optional[str] = None
    ends: list[str] = field(default_factory=list)
    doc: Optional[str] = None


@dataclass
class AllocationNode(ASTNode):
    """An allocation usage."""

    name: str = ""
    source: str = ""
    target: str = ""


@dataclass
class AllocationDefNode(ASTNode):
    """An allocation definition."""

    name: str = ""
    parent: Optional[str] = None
    source: Optional[str] = None
    target: Optional[str] = None
    doc: Optional[str] = None


@dataclass
class UseCaseNode(ASTNode):
    """A use case usage."""

    name: str = ""
    type_ref: Optional[TypeReference] = None
    actors: list[str] = field(default_factory=list)
    includes: list[str] = field(default_factory=list)
    extends: list[str] = field(default_factory=list)


@dataclass
class UseCaseDefNode(ASTNode):
    """A use case definition."""

    name: str = ""
    parent: Optional[str] = None
    actors: list[str] = field(default_factory=list)
    includes: list[str] = field(default_factory=list)
    extends: list[str] = field(default_factory=list)
    doc: Optional[str] = None


@dataclass
class CalcNode(ASTNode):
    """A calculation usage."""

    name: str = ""
    type_ref: Optional[TypeReference] = None
    expression: Optional[str] = None


@dataclass
class CalcDefNode(ASTNode):
    """A calculation definition."""

    name: str = ""
    parent: Optional[str] = None
    parameters: list[AttributeNode] = field(default_factory=list)
    result_type: Optional[TypeReference] = None
    expression: Optional[str] = None
    doc: Optional[str] = None


@dataclass
class ViewNode(ASTNode):
    """A view usage."""

    name: str = ""
    type_ref: Optional[TypeReference] = None


@dataclass
class ViewDefNode(ASTNode):
    """A view definition."""

    name: str = ""
    parent: Optional[str] = None
    doc: Optional[str] = None


@dataclass
class ViewpointNode(ASTNode):
    """A viewpoint usage."""

    name: str = ""
    type_ref: Optional[TypeReference] = None


@dataclass
class ViewpointDefNode(ASTNode):
    """A viewpoint definition."""

    name: str = ""
    parent: Optional[str] = None
    concerns: list[str] = field(default_factory=list)
    doc: Optional[str] = None


@dataclass
class SatisfyNode(ASTNode):
    """A satisfy relationship."""

    name: Optional[str] = None
    requirement: str = ""
    subject: str = ""


@dataclass
class PackageNode(ASTNode):
    """A package definition."""

    name: str = ""
    is_library: bool = False
    is_standard: bool = False
    imports: list[ImportNode] = field(default_factory=list)
    members: list[ASTNode] = field(default_factory=list)
    doc: Optional[str] = None


@dataclass
class ModelNode(ASTNode):
    """The root node of a SysML v2 model."""

    packages: list[PackageNode] = field(default_factory=list)
    imports: list[ImportNode] = field(default_factory=list)
    members: list[ASTNode] = field(default_factory=list)


class ASTVisitor:
    """Base class for AST visitors."""

    def visit_default(self, node: ASTNode) -> Any:
        """Default visit method for unhandled node types."""
        return None

    def visit_children(self, node: ASTNode) -> list:
        """Visit all children of a node."""
        results = []
        for attr_name in dir(node):
            if attr_name.startswith("_"):
                continue
            attr = getattr(node, attr_name)
            if isinstance(attr, ASTNode):
                results.append(attr.accept(self))
            elif isinstance(attr, list):
                for item in attr:
                    if isinstance(item, ASTNode):
                        results.append(item.accept(self))
        return results


class ASTPrinter(ASTVisitor):
    """Visitor that prints the AST in a readable format."""

    def __init__(self, indent: int = 2):
        self.indent = indent
        self.level = 0

    def _print(self, text: str) -> str:
        prefix = " " * (self.level * self.indent)
        return f"{prefix}{text}"

    def visit_default(self, node: ASTNode) -> str:
        lines = [self._print(f"{type(node).__name__}:")]
        self.level += 1

        for attr_name in ["name", "type_ref", "parent", "text", "expression"]:
            if hasattr(node, attr_name):
                value = getattr(node, attr_name)
                if value is not None:
                    lines.append(self._print(f"{attr_name}: {value}"))

        for child in self.visit_children(node):
            if child:
                lines.append(child)

        self.level -= 1
        return "\n".join(lines)
