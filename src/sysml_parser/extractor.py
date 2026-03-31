"""
SysML v2 Element Extractor

Extracts structured information from SysML v2 models for comparison and analysis.

Reference: SysML v2 Language Specification
https://github.com/Systems-Modeling/SysML-v2-Release
"""

from dataclasses import dataclass, field
from typing import Optional
import re

from .parser import SysMLParser
from .ast_nodes import (
    ModelNode,
    PackageNode,
    PartDefNode,
    PartNode,
    PortDefNode,
    PortNode,
    AttributeNode,
    ActionDefNode,
    ActionNode,
    StateDefNode,
    StateNode,
    TransitionNode,
    RequirementDefNode,
    RequirementNode,
    ConnectionNode,
    ItemDefNode,
    ItemNode,
    Direction,
)


@dataclass
class PackageInfo:
    """Extracted package information."""

    name: str
    imports: list[str] = field(default_factory=list)


@dataclass
class PartDefInfo:
    """Extracted part definition information."""

    name: str
    parent: Optional[str] = None
    attributes: list[str] = field(default_factory=list)
    ports: list[str] = field(default_factory=list)
    actions: list[str] = field(default_factory=list)
    parts: list[str] = field(default_factory=list)


@dataclass
class PartInfo:
    """Extracted part usage information."""

    name: str
    type: Optional[str] = None
    multiplicity: Optional[str] = None


@dataclass
class PortDefInfo:
    """Extracted port definition information."""

    name: str
    direction: Optional[str] = None
    attributes: list[str] = field(default_factory=list)


@dataclass
class PortInfo:
    """Extracted port usage information."""

    name: str
    type: Optional[str] = None
    direction: Optional[str] = None


@dataclass
class AttributeInfo:
    """Extracted attribute information."""

    name: str
    type: Optional[str] = None
    default_value: Optional[str] = None


@dataclass
class ConnectionInfo:
    """Extracted connection information."""

    name: Optional[str] = None
    source: str = ""
    target: str = ""


@dataclass
class RequirementInfo:
    """Extracted requirement information."""

    name: str
    id: Optional[str] = None
    text: Optional[str] = None
    parent: Optional[str] = None


@dataclass
class StateInfo:
    """Extracted state information."""

    name: str
    is_initial: bool = False
    parent: Optional[str] = None
    entry_action: Optional[str] = None
    exit_action: Optional[str] = None
    do_action: Optional[str] = None


@dataclass
class TransitionInfo:
    """Extracted transition information."""

    name: Optional[str] = None
    source: str = ""
    target: str = ""
    trigger: Optional[str] = None
    guard: Optional[str] = None


@dataclass
class ActionInfo:
    """Extracted action information."""

    name: str
    parent: Optional[str] = None
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)


@dataclass
class ItemDefInfo:
    """Extracted item definition information."""

    name: str
    parent: Optional[str] = None
    attributes: list[str] = field(default_factory=list)


@dataclass
class ExtractedModel:
    """Complete extracted model information."""

    packages: list[PackageInfo] = field(default_factory=list)
    part_defs: list[PartDefInfo] = field(default_factory=list)
    parts: list[PartInfo] = field(default_factory=list)
    port_defs: list[PortDefInfo] = field(default_factory=list)
    ports: list[PortInfo] = field(default_factory=list)
    attributes: list[AttributeInfo] = field(default_factory=list)
    connections: list[ConnectionInfo] = field(default_factory=list)
    requirements: list[RequirementInfo] = field(default_factory=list)
    states: list[StateInfo] = field(default_factory=list)
    transitions: list[TransitionInfo] = field(default_factory=list)
    actions: list[ActionInfo] = field(default_factory=list)
    item_defs: list[ItemDefInfo] = field(default_factory=list)


class SysMLExtractor:
    """
    Extracts structured information from SysML v2 source code.

    This extractor can use either the parser-based approach (recommended)
    or a regex-based fallback for simple extraction.

    Example:
        >>> extractor = SysMLExtractor("package Vehicle { part engine : Engine; }")
        >>> model = extractor.extract()
        >>> print(model.parts[0].name)
        engine
    """

    def __init__(self, source: str, use_parser: bool = True):
        """
        Initialize the extractor with source code.

        Args:
            source: The SysML v2 source code to extract from.
            use_parser: If True, use the parser for extraction. If False, use regex.
        """
        self.source = source
        self.use_parser = use_parser

    def extract(self) -> ExtractedModel:
        """
        Extract structured information from the source code.

        Returns:
            An ExtractedModel containing all extracted elements.
        """
        if self.use_parser:
            return self._extract_with_parser()
        else:
            return self._extract_with_regex()

    def _extract_with_parser(self) -> ExtractedModel:
        """Extract using the parser and AST walking."""
        parser = SysMLParser(self.source)
        ast = parser.parse()

        model = ExtractedModel()
        self._walk_node(ast, model)
        return model

    def _walk_node(self, node, model: ExtractedModel) -> None:
        """Recursively walk the AST and extract information."""
        if isinstance(node, ModelNode):
            for pkg in node.packages:
                self._walk_node(pkg, model)
            for member in node.members:
                self._walk_node(member, model)

        elif isinstance(node, PackageNode):
            imports = [imp.path for imp in node.imports]
            model.packages.append(PackageInfo(name=node.name, imports=imports))
            for member in node.members:
                self._walk_node(member, model)

        elif isinstance(node, PartDefNode):
            part_def = PartDefInfo(
                name=node.name,
                parent=node.parent,
                attributes=[attr.name for attr in node.attributes],
                ports=[port.name for port in node.ports],
                parts=[part.name for part in node.parts],
                actions=[action.name for action in node.actions],
            )
            model.part_defs.append(part_def)

            # Also extract nested elements
            for attr in node.attributes:
                self._walk_node(attr, model)
            for port in node.ports:
                self._walk_node(port, model)
            for part in node.parts:
                self._walk_node(part, model)
            for action in node.actions:
                self._walk_node(action, model)
            for state in node.states:
                self._walk_node(state, model)
            for conn in node.connections:
                self._walk_node(conn, model)

        elif isinstance(node, PartNode):
            type_name = node.type_ref.name if node.type_ref else None
            mult = str(node.multiplicity) if node.multiplicity else None
            model.parts.append(PartInfo(name=node.name, type=type_name, multiplicity=mult))

        elif isinstance(node, PortDefNode):
            direction = self._direction_to_str(node.direction)
            model.port_defs.append(
                PortDefInfo(
                    name=node.name,
                    direction=direction,
                    attributes=[attr.name for attr in node.attributes],
                )
            )

        elif isinstance(node, PortNode):
            type_name = node.type_ref.name if node.type_ref else None
            direction = self._direction_to_str(node.direction)
            model.ports.append(PortInfo(name=node.name, type=type_name, direction=direction))

        elif isinstance(node, AttributeNode):
            type_name = node.type_ref.name if node.type_ref else None
            model.attributes.append(
                AttributeInfo(name=node.name, type=type_name, default_value=node.default_value)
            )

        elif isinstance(node, ConnectionNode):
            model.connections.append(
                ConnectionInfo(name=node.name, source=node.source, target=node.target)
            )

        elif isinstance(node, RequirementDefNode):
            model.requirements.append(
                RequirementInfo(name=node.name, id=node.id, text=node.doc, parent=node.parent)
            )

        elif isinstance(node, RequirementNode):
            model.requirements.append(RequirementInfo(name=node.name, id=node.id))

        elif isinstance(node, StateDefNode):
            for state in node.states:
                self._walk_node(state, model)
            for trans in node.transitions:
                self._walk_node(trans, model)

        elif isinstance(node, StateNode):
            model.states.append(
                StateInfo(
                    name=node.name,
                    is_initial=node.is_initial,
                    entry_action=node.entry_action,
                    exit_action=node.exit_action,
                    do_action=node.do_action,
                )
            )
            for substate in node.substates:
                self._walk_node(substate, model)
            for trans in node.transitions:
                self._walk_node(trans, model)

        elif isinstance(node, TransitionNode):
            model.transitions.append(
                TransitionInfo(
                    name=node.name,
                    source=node.source,
                    target=node.target,
                    trigger=node.trigger,
                    guard=node.guard,
                )
            )

        elif isinstance(node, ActionDefNode):
            model.actions.append(
                ActionInfo(
                    name=node.name,
                    parent=node.parent,
                    inputs=[inp.name for inp in node.inputs],
                    outputs=[out.name for out in node.outputs],
                )
            )

        elif isinstance(node, ActionNode):
            model.actions.append(
                ActionInfo(
                    name=node.name,
                    inputs=[inp.name for inp in node.inputs],
                    outputs=[out.name for out in node.outputs],
                )
            )

        elif isinstance(node, ItemDefNode):
            model.item_defs.append(
                ItemDefInfo(
                    name=node.name,
                    parent=node.parent,
                    attributes=[attr.name for attr in node.attributes],
                )
            )

    def _direction_to_str(self, direction: Optional[Direction]) -> Optional[str]:
        """Convert Direction enum to string."""
        if direction is None:
            return None
        return direction.name.lower()

    def _extract_with_regex(self) -> ExtractedModel:
        """Extract using regex patterns (fallback method)."""
        model = ExtractedModel()
        source = self._remove_comments(self.source)

        # Extract packages
        model.packages = self._extract_packages_regex(source)

        # Extract part definitions
        model.part_defs = self._extract_part_defs_regex(source)

        # Extract parts
        model.parts = self._extract_parts_regex(source)

        # Extract port definitions
        model.port_defs = self._extract_port_defs_regex(source)

        # Extract ports
        model.ports = self._extract_ports_regex(source)

        # Extract attributes
        model.attributes = self._extract_attributes_regex(source)

        # Extract connections
        model.connections = self._extract_connections_regex(source)

        # Extract requirements
        model.requirements = self._extract_requirements_regex(source)

        # Extract states
        model.states = self._extract_states_regex(source)

        # Extract transitions
        model.transitions = self._extract_transitions_regex(source)

        # Extract actions
        model.actions = self._extract_actions_regex(source)

        # Extract item definitions
        model.item_defs = self._extract_item_defs_regex(source)

        return model

    def _remove_comments(self, source: str) -> str:
        """Remove comments from source code."""
        # Remove block comments
        source = re.sub(r"/\*[\s\S]*?\*/", "", source)
        # Remove line comments
        source = re.sub(r"//.*$", "", source, flags=re.MULTILINE)
        return source

    def _extract_packages_regex(self, source: str) -> list[PackageInfo]:
        """Extract packages using regex."""
        packages = []
        pattern = r"\bpackage\s+(\w+)\s*\{"
        for match in re.finditer(pattern, source):
            name = match.group(1)
            # Find imports within package
            start = match.end()
            end = self._find_matching_brace(source, start - 1)
            content = source[start:end]
            imports = re.findall(r"\bimport\s+([^;]+);", content)
            packages.append(PackageInfo(name=name, imports=[i.strip() for i in imports]))
        return packages

    def _extract_part_defs_regex(self, source: str) -> list[PartDefInfo]:
        """Extract part definitions using regex."""
        part_defs = []
        pattern = r"\bpart\s+def\s+(\w+)(?:\s*:>\s*(\w+))?\s*\{?"
        for match in re.finditer(pattern, source):
            name = match.group(1)
            parent = match.group(2)
            part_defs.append(PartDefInfo(name=name, parent=parent))
        return part_defs

    def _extract_parts_regex(self, source: str) -> list[PartInfo]:
        """Extract parts using regex."""
        parts = []
        pattern = r"\bpart\s+(?!def\b)(\w+)\s*(?::\s*(\w+))?(?:\s*\[([^\]]+)\])?"
        for match in re.finditer(pattern, source):
            name = match.group(1)
            part_type = match.group(2)
            mult = match.group(3)
            parts.append(PartInfo(name=name, type=part_type, multiplicity=mult))
        return parts

    def _extract_port_defs_regex(self, source: str) -> list[PortDefInfo]:
        """Extract port definitions using regex."""
        port_defs = []
        pattern = r"\bport\s+def\s+(\w+)\s*\{?"
        for match in re.finditer(pattern, source):
            name = match.group(1)
            port_defs.append(PortDefInfo(name=name))
        return port_defs

    def _extract_ports_regex(self, source: str) -> list[PortInfo]:
        """Extract ports using regex."""
        ports = []
        pattern = r"\b(in|out|inout)?\s*port\s+(?!def\b)(\w+)(?:\s*:\s*~?(\w+))?"
        for match in re.finditer(pattern, source):
            direction = match.group(1)
            name = match.group(2)
            port_type = match.group(3)
            ports.append(PortInfo(name=name, type=port_type, direction=direction))
        return ports

    def _extract_attributes_regex(self, source: str) -> list[AttributeInfo]:
        """Extract attributes using regex."""
        attributes = []
        pattern = r"\battribute\s+(\w+)(?:\s*:\s*(\w+))?(?:\s*=\s*([^;{]+))?"
        for match in re.finditer(pattern, source):
            name = match.group(1)
            attr_type = match.group(2)
            default = match.group(3)
            attributes.append(
                AttributeInfo(name=name, type=attr_type, default_value=default.strip() if default else None)
            )
        return attributes

    def _extract_connections_regex(self, source: str) -> list[ConnectionInfo]:
        """Extract connections using regex."""
        connections = []
        pattern = r"\bconnect\s+(?:(\w+)\s+)?(\S+)\s+to\s+(\S+)"
        for match in re.finditer(pattern, source):
            name = match.group(1)
            src = match.group(2)
            target = match.group(3).rstrip(";")
            connections.append(ConnectionInfo(name=name, source=src, target=target))
        return connections

    def _extract_requirements_regex(self, source: str) -> list[RequirementInfo]:
        """Extract requirements using regex."""
        requirements = []
        pattern = r"\brequirement\s+(?:def\s+)?(?:<'([^']+)'>\s+)?(\w+)(?:\s*:>\s*(\w+))?"
        for match in re.finditer(pattern, source):
            req_id = match.group(1)
            name = match.group(2)
            parent = match.group(3)
            requirements.append(RequirementInfo(name=name, id=req_id, parent=parent))
        return requirements

    def _extract_states_regex(self, source: str) -> list[StateInfo]:
        """Extract states using regex."""
        states = []
        pattern = r"\b(first\s+)?state\s+(?:def\s+)?(\w+)(?:\s*:>\s*(\w+))?"
        for match in re.finditer(pattern, source):
            is_initial = match.group(1) is not None
            name = match.group(2)
            parent = match.group(3)
            states.append(StateInfo(name=name, is_initial=is_initial, parent=parent))
        return states

    def _extract_transitions_regex(self, source: str) -> list[TransitionInfo]:
        """Extract transitions using regex."""
        transitions = []
        pattern = r"\btransition\s+(?:(\w+)\s+)?(?:first\s+)?(\w+)\s+(?:accept\s+(\w+)\s+)?(?:\[([^\]]+)\]\s+)?then\s+(\w+)"
        for match in re.finditer(pattern, source):
            name = match.group(1)
            src = match.group(2)
            trigger = match.group(3)
            guard = match.group(4)
            target = match.group(5)
            transitions.append(
                TransitionInfo(name=name, source=src, target=target, trigger=trigger, guard=guard)
            )

        # Also match succession
        succ_pattern = r"\bsuccession\s+(\w+)\s+then\s+(\w+)"
        for match in re.finditer(succ_pattern, source):
            src = match.group(1)
            target = match.group(2)
            transitions.append(TransitionInfo(source=src, target=target))

        return transitions

    def _extract_actions_regex(self, source: str) -> list[ActionInfo]:
        """Extract actions using regex."""
        actions = []
        pattern = r"\baction\s+(?:def\s+)?(\w+)(?:\s*:>\s*(\w+))?"
        for match in re.finditer(pattern, source):
            name = match.group(1)
            parent = match.group(2)
            actions.append(ActionInfo(name=name, parent=parent))
        return actions

    def _extract_item_defs_regex(self, source: str) -> list[ItemDefInfo]:
        """Extract item definitions using regex."""
        item_defs = []
        pattern = r"\bitem\s+def\s+(\w+)(?:\s+specializes\s+(\w+)|(?:\s*:>\s*(\w+)))?"
        for match in re.finditer(pattern, source):
            name = match.group(1)
            parent = match.group(2) or match.group(3)
            item_defs.append(ItemDefInfo(name=name, parent=parent))
        return item_defs

    def _find_matching_brace(self, source: str, start: int) -> int:
        """Find the matching closing brace."""
        count = 1
        pos = start + 1
        in_string = False
        string_char = ""

        while pos < len(source) and count > 0:
            char = source[pos]

            if in_string:
                if char == string_char and source[pos - 1] != "\\":
                    in_string = False
            else:
                if char in ('"', "'"):
                    in_string = True
                    string_char = char
                elif char == "{":
                    count += 1
                elif char == "}":
                    count -= 1

            pos += 1

        return pos


def extract(source: str, use_parser: bool = True) -> ExtractedModel:
    """
    Convenience function to extract SysML v2 elements from source code.

    Args:
        source: The SysML v2 source code to extract from.
        use_parser: If True, use the parser. If False, use regex.

    Returns:
        An ExtractedModel containing all extracted elements.
    """
    extractor = SysMLExtractor(source, use_parser=use_parser)
    return extractor.extract()


def extract_part_def_names(source: str) -> list[str]:
    """Extract just the names of part definitions."""
    model = extract(source)
    return [p.name for p in model.part_defs]


def extract_port_def_names(source: str) -> list[str]:
    """Extract just the names of port definitions."""
    model = extract(source)
    return [p.name for p in model.port_defs]


def extract_requirement_names(source: str) -> list[str]:
    """Extract just the names of requirements."""
    model = extract(source)
    return [r.name for r in model.requirements]


def extract_state_names(source: str) -> list[str]:
    """Extract just the names of states."""
    model = extract(source)
    return [s.name for s in model.states]


def extract_action_names(source: str) -> list[str]:
    """Extract just the names of actions."""
    model = extract(source)
    return [a.name for a in model.actions]
