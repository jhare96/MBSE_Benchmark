"""
SysML v2 Parser

Parses SysML v2 textual notation into an Abstract Syntax Tree (AST).

Reference: SysML v2 Language Specification
https://github.com/Systems-Modeling/SysML-v2-Release
"""

from dataclasses import dataclass
from typing import Optional

from .lexer import SysMLLexer, Token, TokenType
from .ast_nodes import (
    ASTNode,
    ModelNode,
    PackageNode,
    ImportNode,
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
    ConstraintDefNode,
    ConstraintNode,
    ConnectionNode,
    ItemDefNode,
    ItemNode,
    InterfaceDefNode,
    CalcDefNode,
    AllocationDefNode,
    UseCaseDefNode,
    SatisfyNode,
    CommentNode,
    TypeReference,
    Multiplicity,
    SourceLocation,
    Direction,
)


@dataclass
class ParseError(Exception):
    """An error that occurred during parsing."""

    message: str
    line: int
    column: int

    def __str__(self) -> str:
        return f"Parse error at {self.line}:{self.column}: {self.message}"


class SysMLParser:
    """
    Parser for SysML v2 textual notation.

    Converts a stream of tokens into an Abstract Syntax Tree (AST).

    Example:
        >>> parser = SysMLParser("package Vehicle { part engine : Engine; }")
        >>> model = parser.parse()
        >>> print(model.packages[0].name)
        Vehicle
    """

    def __init__(self, source: str):
        """
        Initialize the parser with source code.

        Args:
            source: The SysML v2 source code to parse.
        """
        self.source = source
        self.lexer = SysMLLexer(source)
        self.tokens: list[Token] = []
        self.pos = 0
        self.errors: list[ParseError] = []

    def _tokenize(self) -> None:
        """Tokenize the source code, filtering whitespace."""
        self.tokens = list(self.lexer.tokenize(include_whitespace=False, include_comments=True))
        self.pos = 0

    def _current(self) -> Token:
        """Return the current token."""
        if self.pos >= len(self.tokens):
            return Token(TokenType.EOF, "", 0, 0)
        return self.tokens[self.pos]

    def _peek(self, offset: int = 1) -> Token:
        """Peek at a token ahead of the current position."""
        pos = self.pos + offset
        if pos >= len(self.tokens):
            return Token(TokenType.EOF, "", 0, 0)
        return self.tokens[pos]

    def _advance(self) -> Token:
        """Advance to the next token and return the current one."""
        token = self._current()
        self.pos += 1
        return token

    def _match(self, *types: TokenType) -> bool:
        """Check if the current token matches any of the given types."""
        return self._current().type in types

    def _expect(self, token_type: TokenType, message: str = "") -> Token:
        """Expect a specific token type and advance, or raise an error."""
        if self._current().type != token_type:
            actual = self._current()
            msg = message or f"Expected {token_type.name}, got {actual.type.name}"
            error = ParseError(msg, actual.line, actual.column)
            self.errors.append(error)
            raise error
        return self._advance()

    def _skip_comments(self) -> list[CommentNode]:
        """Skip comment tokens and return them as nodes."""
        comments = []
        while self._match(TokenType.COMMENT_LINE, TokenType.COMMENT_BLOCK):
            token = self._advance()
            is_block = token.type == TokenType.COMMENT_BLOCK
            text = token.value
            # Extract text content from comment
            if is_block:
                text = text[2:-2].strip() if text.startswith("/*") and text.endswith("*/") else text
            else:
                text = text[2:].strip() if text.startswith("//") else text
            comments.append(
                CommentNode(
                    text=text,
                    is_block=is_block,
                    is_doc=token.value.startswith("/**") or token.value.startswith("/* "),
                    location=SourceLocation(token.line, token.column),
                )
            )
        return comments

    def _location(self, token: Token) -> SourceLocation:
        """Create a SourceLocation from a token."""
        return SourceLocation(token.line, token.column)

    def parse(self) -> ModelNode:
        """
        Parse the source code into an AST.

        Returns:
            The root ModelNode of the AST.

        Raises:
            ParseError: If a syntax error is encountered.
        """
        self._tokenize()
        model = ModelNode()

        while not self._match(TokenType.EOF):
            self._skip_comments()

            if self._match(TokenType.EOF):
                break

            try:
                member = self._parse_member()
                if member:
                    if isinstance(member, PackageNode):
                        model.packages.append(member)
                    elif isinstance(member, ImportNode):
                        model.imports.append(member)
                    else:
                        model.members.append(member)
            except ParseError:
                # Skip to next statement on error
                self._recover()

        return model

    def _recover(self) -> None:
        """Recover from a parse error by skipping to the next statement."""
        while not self._match(TokenType.EOF):
            if self._match(TokenType.SEMICOLON, TokenType.RBRACE):
                self._advance()
                return
            if self._match(
                TokenType.PACKAGE,
                TokenType.PART,
                TokenType.PART_DEF,
                TokenType.PORT_DEF,
                TokenType.IMPORT,
            ):
                return
            self._advance()

    def _parse_member(self) -> Optional[ASTNode]:
        """Parse a top-level or nested member."""
        self._skip_comments()

        token = self._current()

        # Handle modifiers
        is_abstract = False
        is_individual = False
        visibility = None
        is_standard = False
        is_library = False

        while self._match(
            TokenType.ABSTRACT,
            TokenType.INDIVIDUAL,
            TokenType.PRIVATE,
            TokenType.PUBLIC,
            TokenType.PROTECTED,
            TokenType.STANDARD,
            TokenType.LIBRARY,
        ):
            if self._match(TokenType.ABSTRACT):
                is_abstract = True
                self._advance()
            elif self._match(TokenType.INDIVIDUAL):
                is_individual = True
                self._advance()
            elif self._match(TokenType.PRIVATE):
                visibility = "private"
                self._advance()
            elif self._match(TokenType.PUBLIC):
                visibility = "public"
                self._advance()
            elif self._match(TokenType.PROTECTED):
                visibility = "protected"
                self._advance()
            elif self._match(TokenType.STANDARD):
                is_standard = True
                self._advance()
            elif self._match(TokenType.LIBRARY):
                is_library = True
                self._advance()

        token = self._current()

        if self._match(TokenType.PACKAGE):
            return self._parse_package(is_library=is_library, is_standard=is_standard)
        elif self._match(TokenType.PART_DEF):
            return self._parse_part_def(is_abstract=is_abstract, is_individual=is_individual)
        elif self._match(TokenType.PART):
            return self._parse_part()
        elif self._match(TokenType.PORT_DEF):
            return self._parse_port_def()
        elif self._match(TokenType.PORT):
            # Check for direction prefix
            return self._parse_port()
        elif self._match(TokenType.IN, TokenType.OUT, TokenType.INOUT):
            direction = self._parse_direction()
            if self._match(TokenType.PORT):
                return self._parse_port(direction=direction)
            # Could be parameter
            return self._parse_attribute(is_input=direction == Direction.IN, is_output=direction == Direction.OUT)
        elif self._match(TokenType.ATTRIBUTE_DEF):
            return self._parse_attribute_def()
        elif self._match(TokenType.ATTRIBUTE):
            return self._parse_attribute()
        elif self._match(TokenType.ITEM_DEF):
            return self._parse_item_def(is_abstract=is_abstract)
        elif self._match(TokenType.ITEM):
            return self._parse_item()
        elif self._match(TokenType.ACTION_DEF):
            return self._parse_action_def(is_abstract=is_abstract)
        elif self._match(TokenType.ACTION):
            return self._parse_action()
        elif self._match(TokenType.STATE_DEF):
            return self._parse_state_def(is_abstract=is_abstract)
        elif self._match(TokenType.STATE):
            return self._parse_state()
        elif self._match(TokenType.FIRST):
            self._advance()
            if self._match(TokenType.STATE):
                return self._parse_state(is_initial=True)
            # Reset position if not followed by state
            self.pos -= 1
        elif self._match(TokenType.TRANSITION):
            return self._parse_transition()
        elif self._match(TokenType.SUCCESSION):
            return self._parse_succession()
        elif self._match(TokenType.REQUIREMENT_DEF):
            return self._parse_requirement_def()
        elif self._match(TokenType.REQUIREMENT):
            return self._parse_requirement()
        elif self._match(TokenType.CONSTRAINT_DEF):
            return self._parse_constraint_def()
        elif self._match(TokenType.CONSTRAINT):
            return self._parse_constraint()
        elif self._match(TokenType.INTERFACE_DEF):
            return self._parse_interface_def()
        elif self._match(TokenType.CONNECTION_DEF):
            return self._parse_connection_def()
        elif self._match(TokenType.CONNECTION):
            return self._parse_connection()
        elif self._match(TokenType.CONNECT):
            return self._parse_connect()
        elif self._match(TokenType.BIND):
            return self._parse_bind()
        elif self._match(TokenType.CALC_DEF):
            return self._parse_calc_def()
        elif self._match(TokenType.ALLOCATION_DEF):
            return self._parse_allocation_def()
        elif self._match(TokenType.USE_CASE):
            return self._parse_use_case_def()
        elif self._match(TokenType.IMPORT):
            return self._parse_import(is_public=visibility == "public", is_private=visibility == "private")
        elif self._match(TokenType.ALIAS):
            return self._parse_alias()
        elif self._match(TokenType.SATISFY):
            return self._parse_satisfy()
        elif self._match(TokenType.DOC):
            return self._parse_doc()
        elif self._match(TokenType.REF):
            self._advance()
            return self._parse_member()  # Handle ref modifier
        elif self._match(TokenType.PERFORM):
            return self._parse_perform()
        elif self._match(TokenType.EXHIBIT):
            return self._parse_exhibit()
        else:
            # Unknown token, skip
            self._advance()
            return None

    def _parse_direction(self) -> Direction:
        """Parse a direction keyword."""
        if self._match(TokenType.IN):
            self._advance()
            return Direction.IN
        elif self._match(TokenType.OUT):
            self._advance()
            return Direction.OUT
        elif self._match(TokenType.INOUT):
            self._advance()
            return Direction.INOUT
        return Direction.IN

    def _parse_package(self, is_library: bool = False, is_standard: bool = False) -> PackageNode:
        """Parse a package definition."""
        start = self._current()
        self._expect(TokenType.PACKAGE)

        name = self._expect(TokenType.IDENTIFIER).value

        package = PackageNode(
            name=name,
            is_library=is_library,
            is_standard=is_standard,
            location=self._location(start),
        )

        if self._match(TokenType.LBRACE):
            self._advance()

            while not self._match(TokenType.RBRACE, TokenType.EOF):
                member = self._parse_member()
                if member:
                    if isinstance(member, ImportNode):
                        package.imports.append(member)
                    else:
                        package.members.append(member)

            self._expect(TokenType.RBRACE)

        return package

    def _parse_import(self, is_public: bool = False, is_private: bool = False) -> ImportNode:
        """Parse an import statement."""
        start = self._current()
        self._expect(TokenType.IMPORT)

        # Parse the import path
        path_parts = []

        while True:
            if self._match(TokenType.IDENTIFIER):
                path_parts.append(self._advance().value)
            elif self._match(TokenType.STAR):
                path_parts.append("*")
                self._advance()
                break
            else:
                break

            if self._match(TokenType.COLONCOLON):
                path_parts.append("::")
                self._advance()
            else:
                break

        path = "".join(path_parts)
        is_wildcard = path.endswith("*")

        # Optional alias
        alias = None
        if self._match(TokenType.AS):
            self._advance()
            alias = self._expect(TokenType.IDENTIFIER).value

        self._expect(TokenType.SEMICOLON)

        return ImportNode(
            path=path,
            is_public=is_public,
            is_private=is_private,
            alias=alias,
            is_wildcard=is_wildcard,
            location=self._location(start),
        )

    def _parse_type_reference(self) -> Optional[TypeReference]:
        """Parse a type reference."""
        if not self._match(TokenType.IDENTIFIER):
            return None

        name_parts = [self._advance().value]

        while self._match(TokenType.COLONCOLON):
            self._advance()
            if self._match(TokenType.IDENTIFIER):
                name_parts.append(self._advance().value)

        name = name_parts[-1]
        qualified_name = "::".join(name_parts) if len(name_parts) > 1 else None

        # Parse multiplicity if present
        multiplicity = None
        if self._match(TokenType.LBRACKET):
            multiplicity = self._parse_multiplicity_string()

        return TypeReference(name=name, qualified_name=qualified_name, multiplicity=multiplicity)

    def _parse_multiplicity(self) -> Optional[Multiplicity]:
        """Parse a multiplicity specification."""
        if not self._match(TokenType.LBRACKET):
            return None

        self._advance()  # Skip [

        lower = 0
        upper: Optional[int] = 0

        if self._match(TokenType.NUMBER):
            lower = int(self._advance().value)
            upper = lower

            if self._match(TokenType.DOTDOT):
                self._advance()
                if self._match(TokenType.STAR):
                    upper = None
                    self._advance()
                elif self._match(TokenType.NUMBER):
                    upper = int(self._advance().value)
        elif self._match(TokenType.STAR):
            lower = 0
            upper = None
            self._advance()

        self._expect(TokenType.RBRACKET)

        return Multiplicity(lower=lower, upper=upper)

    def _parse_multiplicity_string(self) -> str:
        """Parse a multiplicity specification and return as string."""
        if not self._match(TokenType.LBRACKET):
            return ""

        self._advance()  # Skip [
        parts = []

        while not self._match(TokenType.RBRACKET, TokenType.EOF):
            token = self._advance()
            parts.append(token.value)

        self._expect(TokenType.RBRACKET)

        return "".join(parts)

    def _parse_part_def(self, is_abstract: bool = False, is_individual: bool = False) -> PartDefNode:
        """Parse a part definition."""
        start = self._current()
        self._expect(TokenType.PART_DEF)

        name = self._expect(TokenType.IDENTIFIER).value

        parent = None
        if self._match(TokenType.COLON_GT):
            self._advance()
            parent = self._expect(TokenType.IDENTIFIER).value

        part_def = PartDefNode(
            name=name,
            parent=parent,
            is_abstract=is_abstract,
            is_individual=is_individual,
            location=self._location(start),
        )

        if self._match(TokenType.LBRACE):
            self._advance()

            while not self._match(TokenType.RBRACE, TokenType.EOF):
                self._skip_comments()

                if self._match(TokenType.RBRACE):
                    break

                # Check for doc comment
                if self._match(TokenType.DOC):
                    part_def.doc = self._parse_doc_content()
                    continue

                member = self._parse_member()
                if member:
                    if isinstance(member, AttributeNode):
                        part_def.attributes.append(member)
                    elif isinstance(member, PortNode):
                        part_def.ports.append(member)
                    elif isinstance(member, PartNode):
                        part_def.parts.append(member)
                    elif isinstance(member, ActionNode):
                        part_def.actions.append(member)
                    elif isinstance(member, StateNode):
                        part_def.states.append(member)
                    elif isinstance(member, ConnectionNode):
                        part_def.connections.append(member)

            self._expect(TokenType.RBRACE)

        return part_def

    def _parse_part(self) -> PartNode:
        """Parse a part usage."""
        start = self._current()
        self._expect(TokenType.PART)

        name = self._expect(TokenType.IDENTIFIER).value

        type_ref = None
        if self._match(TokenType.COLON):
            self._advance()
            type_ref = self._parse_type_reference()

        multiplicity = self._parse_multiplicity()

        part = PartNode(
            name=name,
            type_ref=type_ref,
            multiplicity=multiplicity,
            location=self._location(start),
        )

        # Skip body if present
        if self._match(TokenType.LBRACE):
            self._skip_block()
        elif self._match(TokenType.SEMICOLON):
            self._advance()

        return part

    def _parse_port_def(self) -> PortDefNode:
        """Parse a port definition."""
        start = self._current()
        self._expect(TokenType.PORT_DEF)

        name = self._expect(TokenType.IDENTIFIER).value

        parent = None
        if self._match(TokenType.COLON_GT):
            self._advance()
            parent = self._expect(TokenType.IDENTIFIER).value

        port_def = PortDefNode(name=name, parent=parent, location=self._location(start))

        if self._match(TokenType.LBRACE):
            self._advance()

            while not self._match(TokenType.RBRACE, TokenType.EOF):
                self._skip_comments()

                if self._match(TokenType.RBRACE):
                    break

                # Check for direction
                if self._match(TokenType.IN):
                    port_def.direction = Direction.IN
                    self._advance()
                elif self._match(TokenType.OUT):
                    port_def.direction = Direction.OUT
                    self._advance()
                elif self._match(TokenType.INOUT):
                    port_def.direction = Direction.INOUT
                    self._advance()

                member = self._parse_member()
                if member:
                    if isinstance(member, AttributeNode):
                        port_def.attributes.append(member)

            self._expect(TokenType.RBRACE)

        return port_def

    def _parse_port(self, direction: Optional[Direction] = None) -> PortNode:
        """Parse a port usage."""
        start = self._current()
        self._expect(TokenType.PORT)

        name = self._expect(TokenType.IDENTIFIER).value

        type_ref = None
        is_conjugated = False

        if self._match(TokenType.COLON):
            self._advance()
            # Check for conjugated port (~)
            if self._match(TokenType.TILDE):
                is_conjugated = True
                self._advance()
            type_ref = self._parse_type_reference()

        multiplicity = self._parse_multiplicity()

        port = PortNode(
            name=name,
            type_ref=type_ref,
            direction=direction,
            multiplicity=multiplicity,
            is_conjugated=is_conjugated,
            location=self._location(start),
        )

        if self._match(TokenType.SEMICOLON):
            self._advance()
        elif self._match(TokenType.LBRACE):
            self._skip_block()

        return port

    def _parse_attribute_def(self) -> AttributeNode:
        """Parse an attribute definition."""
        start = self._current()
        self._expect(TokenType.ATTRIBUTE_DEF)

        name = self._expect(TokenType.IDENTIFIER).value

        return AttributeNode(name=name, location=self._location(start))

    def _parse_attribute(self, is_input: bool = False, is_output: bool = False) -> AttributeNode:
        """Parse an attribute usage."""
        start = self._current()

        if self._match(TokenType.ATTRIBUTE):
            self._advance()

        name = ""
        if self._match(TokenType.IDENTIFIER):
            name = self._advance().value

        type_ref = None
        if self._match(TokenType.COLON):
            self._advance()
            type_ref = self._parse_type_reference()

        # Redefines
        if self._match(TokenType.COLON_GTGT):
            self._advance()
            if self._match(TokenType.IDENTIFIER):
                self._advance()  # Skip redefined name
                while self._match(TokenType.COLONCOLON):
                    self._advance()
                    if self._match(TokenType.IDENTIFIER):
                        self._advance()

        default_value = None
        if self._match(TokenType.EQUALS):
            self._advance()
            default_value = self._parse_expression_value()

        attr = AttributeNode(
            name=name,
            type_ref=type_ref,
            default_value=default_value,
            location=self._location(start),
        )

        if self._match(TokenType.SEMICOLON):
            self._advance()
        elif self._match(TokenType.LBRACE):
            self._skip_block()

        return attr

    def _parse_expression_value(self) -> str:
        """Parse an expression value until semicolon or brace."""
        parts = []
        brace_depth = 0

        while not self._match(TokenType.EOF):
            if brace_depth == 0 and self._match(TokenType.SEMICOLON):
                break
            if brace_depth == 0 and self._match(TokenType.RBRACE):
                break

            token = self._advance()
            parts.append(token.value)

            if token.type == TokenType.LBRACE:
                brace_depth += 1
            elif token.type == TokenType.RBRACE:
                brace_depth -= 1

        return " ".join(parts).strip()

    def _parse_item_def(self, is_abstract: bool = False) -> ItemDefNode:
        """Parse an item definition."""
        start = self._current()
        self._expect(TokenType.ITEM_DEF)

        name = self._expect(TokenType.IDENTIFIER).value

        parent = None
        if self._match(TokenType.SPECIALIZES):
            self._advance()
            parent = self._expect(TokenType.IDENTIFIER).value
        elif self._match(TokenType.COLON_GT):
            self._advance()
            parent = self._expect(TokenType.IDENTIFIER).value

        item_def = ItemDefNode(
            name=name,
            parent=parent,
            is_abstract=is_abstract,
            location=self._location(start),
        )

        if self._match(TokenType.LBRACE):
            self._advance()

            while not self._match(TokenType.RBRACE, TokenType.EOF):
                member = self._parse_member()
                if isinstance(member, AttributeNode):
                    item_def.attributes.append(member)

            self._expect(TokenType.RBRACE)
        elif self._match(TokenType.SEMICOLON):
            self._advance()

        return item_def

    def _parse_item(self) -> ItemNode:
        """Parse an item usage."""
        start = self._current()
        self._expect(TokenType.ITEM)

        name = self._expect(TokenType.IDENTIFIER).value

        type_ref = None
        if self._match(TokenType.COLON):
            self._advance()
            type_ref = self._parse_type_reference()

        item = ItemNode(name=name, type_ref=type_ref, location=self._location(start))

        if self._match(TokenType.SEMICOLON):
            self._advance()
        elif self._match(TokenType.LBRACE):
            self._skip_block()

        return item

    def _parse_action_def(self, is_abstract: bool = False) -> ActionDefNode:
        """Parse an action definition."""
        start = self._current()
        self._expect(TokenType.ACTION_DEF)

        name = self._expect(TokenType.IDENTIFIER).value

        parent = None
        if self._match(TokenType.COLON_GT):
            self._advance()
            parent = self._expect(TokenType.IDENTIFIER).value

        action_def = ActionDefNode(
            name=name,
            parent=parent,
            is_abstract=is_abstract,
            location=self._location(start),
        )

        if self._match(TokenType.LBRACE):
            self._advance()

            while not self._match(TokenType.RBRACE, TokenType.EOF):
                self._skip_comments()

                if self._match(TokenType.RBRACE):
                    break

                if self._match(TokenType.IN):
                    self._advance()
                    # Parse parameter directly (may or may not have 'attribute' keyword)
                    attr = self._parse_parameter()
                    if attr:
                        action_def.inputs.append(attr)
                elif self._match(TokenType.OUT):
                    self._advance()
                    # Parse parameter directly
                    attr = self._parse_parameter()
                    if attr:
                        action_def.outputs.append(attr)
                else:
                    member = self._parse_member()
                    if member:
                        action_def.body.append(member)

            self._expect(TokenType.RBRACE)

        return action_def

    def _parse_parameter(self) -> Optional[AttributeNode]:
        """Parse a parameter (used in action inputs/outputs)."""
        start = self._current()

        # Skip 'attribute' keyword if present
        if self._match(TokenType.ATTRIBUTE):
            self._advance()

        # Expect identifier for name
        if not self._match(TokenType.IDENTIFIER):
            return None

        name = self._advance().value

        type_ref = None
        if self._match(TokenType.COLON):
            self._advance()
            type_ref = self._parse_type_reference()

        default_value = None
        if self._match(TokenType.EQUALS):
            self._advance()
            default_value = self._parse_expression_value()

        if self._match(TokenType.SEMICOLON):
            self._advance()

        return AttributeNode(
            name=name,
            type_ref=type_ref,
            default_value=default_value,
            location=self._location(start),
        )

    def _parse_action(self) -> ActionNode:
        """Parse an action usage."""
        start = self._current()
        self._expect(TokenType.ACTION)

        name = ""
        if self._match(TokenType.IDENTIFIER):
            name = self._advance().value

        type_ref = None
        if self._match(TokenType.COLON):
            self._advance()
            type_ref = self._parse_type_reference()

        action = ActionNode(name=name, type_ref=type_ref, location=self._location(start))

        if self._match(TokenType.LBRACE):
            self._advance()

            while not self._match(TokenType.RBRACE, TokenType.EOF):
                self._skip_comments()

                if self._match(TokenType.RBRACE):
                    break

                if self._match(TokenType.IN):
                    self._advance()
                    attr = self._parse_parameter()
                    if attr:
                        action.inputs.append(attr)
                elif self._match(TokenType.OUT):
                    self._advance()
                    attr = self._parse_parameter()
                    if attr:
                        action.outputs.append(attr)
                else:
                    member = self._parse_member()
                    if member:
                        action.body.append(member)

            self._expect(TokenType.RBRACE)
        elif self._match(TokenType.SEMICOLON):
            self._advance()

        return action

    def _parse_state_def(self, is_abstract: bool = False) -> StateDefNode:
        """Parse a state definition."""
        start = self._current()
        self._expect(TokenType.STATE_DEF)

        name = self._expect(TokenType.IDENTIFIER).value

        parent = None
        if self._match(TokenType.COLON_GT):
            self._advance()
            parent = self._expect(TokenType.IDENTIFIER).value

        state_def = StateDefNode(
            name=name,
            parent=parent,
            is_abstract=is_abstract,
            location=self._location(start),
        )

        if self._match(TokenType.LBRACE):
            self._advance()

            while not self._match(TokenType.RBRACE, TokenType.EOF):
                member = self._parse_member()
                if member:
                    if isinstance(member, StateNode):
                        state_def.states.append(member)
                    elif isinstance(member, TransitionNode):
                        state_def.transitions.append(member)

            self._expect(TokenType.RBRACE)

        return state_def

    def _parse_state(self, is_initial: bool = False) -> StateNode:
        """Parse a state usage."""
        start = self._current()
        self._expect(TokenType.STATE)

        name = ""
        if self._match(TokenType.IDENTIFIER):
            name = self._advance().value

        type_ref = None
        if self._match(TokenType.COLON):
            self._advance()
            type_ref = self._parse_type_reference()

        state = StateNode(
            name=name,
            type_ref=type_ref,
            is_initial=is_initial,
            location=self._location(start),
        )

        if self._match(TokenType.LBRACE):
            self._advance()

            while not self._match(TokenType.RBRACE, TokenType.EOF):
                self._skip_comments()

                if self._match(TokenType.ENTRY):
                    self._advance()
                    if self._match(TokenType.IDENTIFIER):
                        state.entry_action = self._advance().value
                    elif self._match(TokenType.ACTION):
                        self._advance()
                        if self._match(TokenType.IDENTIFIER):
                            state.entry_action = self._advance().value
                elif self._match(TokenType.EXIT):
                    self._advance()
                    if self._match(TokenType.IDENTIFIER):
                        state.exit_action = self._advance().value
                    elif self._match(TokenType.ACTION):
                        self._advance()
                        if self._match(TokenType.IDENTIFIER):
                            state.exit_action = self._advance().value
                elif self._match(TokenType.DO):
                    self._advance()
                    if self._match(TokenType.IDENTIFIER):
                        state.do_action = self._advance().value
                    elif self._match(TokenType.ACTION):
                        self._advance()
                        if self._match(TokenType.IDENTIFIER):
                            state.do_action = self._advance().value
                else:
                    member = self._parse_member()
                    if member:
                        if isinstance(member, StateNode):
                            state.substates.append(member)
                        elif isinstance(member, TransitionNode):
                            state.transitions.append(member)

            self._expect(TokenType.RBRACE)
        elif self._match(TokenType.SEMICOLON):
            self._advance()

        return state

    def _parse_transition(self) -> TransitionNode:
        """Parse a transition."""
        start = self._current()
        self._expect(TokenType.TRANSITION)

        name = None
        source = ""
        trigger = None
        guard = None
        target = ""

        # Optional name: could be followed by 'first' or directly the source
        if self._match(TokenType.IDENTIFIER):
            first_id = self._advance().value
            # Check if this is the name or source
            if self._match(TokenType.IDENTIFIER):
                # first_id is the name, next is source
                name = first_id
                source = self._advance().value
            elif self._match(TokenType.FIRST):
                # first_id is the name, 'first' keyword follows
                name = first_id
            else:
                # first_id is the source
                source = first_id

        # Handle 'first <source>' syntax
        if self._match(TokenType.FIRST):
            self._advance()
            if self._is_identifier_like():
                source = self._advance().value

        # Optional trigger: accept <trigger>
        if self._match(TokenType.ACCEPT):
            self._advance()
            if self._is_identifier_like():
                trigger = self._advance().value

        # Optional guard: [condition]
        if self._match(TokenType.LBRACKET):
            self._advance()
            guard_parts = []
            while not self._match(TokenType.RBRACKET, TokenType.EOF):
                guard_parts.append(self._advance().value)
            self._expect(TokenType.RBRACKET)
            guard = " ".join(guard_parts)

        # Target: then <target>
        if self._match(TokenType.THEN):
            self._advance()
            if self._is_identifier_like():
                target = self._advance().value

        transition = TransitionNode(
            name=name,
            source=source,
            target=target,
            trigger=trigger,
            guard=guard,
            location=self._location(start),
        )

        if self._match(TokenType.SEMICOLON):
            self._advance()
        elif self._match(TokenType.LBRACE):
            self._skip_block()

        return transition

    def _parse_succession(self) -> TransitionNode:
        """Parse a succession."""
        start = self._current()
        self._expect(TokenType.SUCCESSION)

        source = ""
        if self._match(TokenType.IDENTIFIER):
            source = self._advance().value

        target = ""
        if self._match(TokenType.THEN):
            self._advance()
            if self._match(TokenType.IDENTIFIER):
                target = self._advance().value

        if self._match(TokenType.SEMICOLON):
            self._advance()

        return TransitionNode(source=source, target=target, location=self._location(start))

    def _parse_requirement_def(self) -> RequirementDefNode:
        """Parse a requirement definition."""
        start = self._current()
        self._expect(TokenType.REQUIREMENT_DEF)

        # Optional ID: <'REQ-001'>
        req_id = None
        if self._match(TokenType.LT):
            self._advance()
            if self._match(TokenType.STRING):
                req_id = self._advance().value.strip("'\"")
            self._expect(TokenType.GT)

        name = self._expect(TokenType.IDENTIFIER).value

        parent = None
        if self._match(TokenType.COLON_GT):
            self._advance()
            parent = self._expect(TokenType.IDENTIFIER).value

        req_def = RequirementDefNode(
            name=name,
            parent=parent,
            id=req_id,
            location=self._location(start),
        )

        if self._match(TokenType.LBRACE):
            self._advance()

            while not self._match(TokenType.RBRACE, TokenType.EOF):
                self._skip_comments()

                if self._match(TokenType.DOC):
                    req_def.doc = self._parse_doc_content()
                elif self._match(TokenType.REQUIRE, TokenType.CONSTRAINT):
                    member = self._parse_member()
                    if isinstance(member, ConstraintNode):
                        req_def.constraints.append(member)
                else:
                    member = self._parse_member()
                    if isinstance(member, AttributeNode):
                        req_def.attributes.append(member)

            self._expect(TokenType.RBRACE)

        return req_def

    def _parse_requirement(self) -> RequirementNode:
        """Parse a requirement usage."""
        start = self._current()
        self._expect(TokenType.REQUIREMENT)

        # Optional ID
        req_id = None
        if self._match(TokenType.LT):
            self._advance()
            if self._match(TokenType.STRING):
                req_id = self._advance().value.strip("'\"")
            self._expect(TokenType.GT)

        name = ""
        if self._match(TokenType.IDENTIFIER):
            name = self._advance().value

        type_ref = None
        if self._match(TokenType.COLON):
            self._advance()
            type_ref = self._parse_type_reference()

        req = RequirementNode(name=name, type_ref=type_ref, id=req_id, location=self._location(start))

        if self._match(TokenType.LBRACE):
            self._skip_block()
        elif self._match(TokenType.SEMICOLON):
            self._advance()

        return req

    def _parse_constraint_def(self) -> ConstraintDefNode:
        """Parse a constraint definition."""
        start = self._current()
        self._expect(TokenType.CONSTRAINT_DEF)

        name = self._expect(TokenType.IDENTIFIER).value

        constraint_def = ConstraintDefNode(name=name, location=self._location(start))

        if self._match(TokenType.LBRACE):
            self._advance()

            expression_parts = []
            while not self._match(TokenType.RBRACE, TokenType.EOF):
                token = self._advance()
                if token.type not in (TokenType.COMMENT_LINE, TokenType.COMMENT_BLOCK):
                    expression_parts.append(token.value)

            constraint_def.expression = " ".join(expression_parts).strip()
            self._expect(TokenType.RBRACE)

        return constraint_def

    def _parse_constraint(self) -> ConstraintNode:
        """Parse a constraint usage."""
        start = self._current()
        self._expect(TokenType.CONSTRAINT)

        name = ""
        if self._match(TokenType.IDENTIFIER):
            name = self._advance().value

        type_ref = None
        if self._match(TokenType.COLON):
            self._advance()
            type_ref = self._parse_type_reference()

        constraint = ConstraintNode(name=name, type_ref=type_ref, location=self._location(start))

        if self._match(TokenType.LBRACE):
            self._advance()

            expression_parts = []
            while not self._match(TokenType.RBRACE, TokenType.EOF):
                token = self._advance()
                if token.type not in (TokenType.COMMENT_LINE, TokenType.COMMENT_BLOCK):
                    expression_parts.append(token.value)

            constraint.expression = " ".join(expression_parts).strip()
            self._expect(TokenType.RBRACE)
        elif self._match(TokenType.SEMICOLON):
            self._advance()

        return constraint

    def _parse_interface_def(self) -> InterfaceDefNode:
        """Parse an interface definition."""
        start = self._current()
        self._expect(TokenType.INTERFACE_DEF)

        name = self._expect(TokenType.IDENTIFIER).value

        interface_def = InterfaceDefNode(name=name, location=self._location(start))

        if self._match(TokenType.LBRACE):
            self._skip_block()

        return interface_def

    def _parse_connection_def(self) -> ConnectionNode:
        """Parse a connection definition."""
        start = self._current()
        self._expect(TokenType.CONNECTION_DEF)

        name = ""
        if self._match(TokenType.IDENTIFIER):
            name = self._advance().value

        connection = ConnectionNode(name=name, location=self._location(start))

        if self._match(TokenType.LBRACE):
            self._skip_block()

        return connection

    def _parse_connection(self) -> ConnectionNode:
        """Parse a connection usage."""
        start = self._current()
        self._expect(TokenType.CONNECTION)

        name = ""
        if self._match(TokenType.IDENTIFIER):
            name = self._advance().value

        connection = ConnectionNode(name=name, location=self._location(start))

        if self._match(TokenType.LBRACE):
            self._skip_block()
        elif self._match(TokenType.SEMICOLON):
            self._advance()

        return connection

    def _parse_connect(self) -> ConnectionNode:
        """Parse a connect statement."""
        start = self._current()
        self._expect(TokenType.CONNECT)

        source = self._parse_qualified_path()

        target = ""
        if self._match(TokenType.TO):
            self._advance()
            target = self._parse_qualified_path()

        if self._match(TokenType.SEMICOLON):
            self._advance()

        return ConnectionNode(source=source, target=target, location=self._location(start))

    def _parse_qualified_path(self) -> str:
        """Parse a qualified path like a.b.c, accepting keywords as identifiers."""
        parts = []

        # Accept identifier or keyword tokens as path segments
        while self._is_identifier_like():
            parts.append(self._advance().value)
            if self._match(TokenType.DOT):
                parts.append(".")
                self._advance()
            else:
                break

        return "".join(parts)

    def _is_identifier_like(self) -> bool:
        """Check if current token can be used as an identifier in a path."""
        token = self._current()
        if token.type == TokenType.IDENTIFIER:
            return True
        # Allow keywords that can be used as identifiers in paths
        keyword_types = {
            TokenType.IN, TokenType.OUT, TokenType.INOUT,
            TokenType.PART, TokenType.PORT, TokenType.ATTRIBUTE,
            TokenType.ITEM, TokenType.ACTION, TokenType.STATE,
            TokenType.FIRST, TokenType.ENTRY, TokenType.EXIT, TokenType.DO,
        }
        return token.type in keyword_types

    def _parse_bind(self) -> ConnectionNode:
        """Parse a bind statement."""
        start = self._current()
        self._expect(TokenType.BIND)

        source = ""
        if self._match(TokenType.IDENTIFIER):
            source = self._advance().value
            while self._match(TokenType.DOT):
                self._advance()
                if self._match(TokenType.IDENTIFIER):
                    source += "." + self._advance().value

        target = ""
        if self._match(TokenType.EQUALS):
            self._advance()
            if self._match(TokenType.IDENTIFIER):
                target = self._advance().value
                while self._match(TokenType.DOT):
                    self._advance()
                    if self._match(TokenType.IDENTIFIER):
                        target += "." + self._advance().value

        if self._match(TokenType.SEMICOLON):
            self._advance()

        return ConnectionNode(source=source, target=target, location=self._location(start))

    def _parse_calc_def(self) -> CalcDefNode:
        """Parse a calculation definition."""
        start = self._current()
        self._expect(TokenType.CALC_DEF)

        name = self._expect(TokenType.IDENTIFIER).value

        calc_def = CalcDefNode(name=name, location=self._location(start))

        if self._match(TokenType.LBRACE):
            self._skip_block()

        return calc_def

    def _parse_allocation_def(self) -> AllocationDefNode:
        """Parse an allocation definition."""
        start = self._current()
        self._expect(TokenType.ALLOCATION_DEF)

        name = self._expect(TokenType.IDENTIFIER).value

        alloc_def = AllocationDefNode(name=name, location=self._location(start))

        if self._match(TokenType.LBRACE):
            self._skip_block()

        return alloc_def

    def _parse_use_case_def(self) -> UseCaseDefNode:
        """Parse a use case definition."""
        start = self._current()
        self._expect(TokenType.USE_CASE)

        name = ""
        if self._match(TokenType.IDENTIFIER):
            name = self._advance().value

        use_case_def = UseCaseDefNode(name=name, location=self._location(start))

        if self._match(TokenType.LBRACE):
            self._skip_block()

        return use_case_def

    def _parse_satisfy(self) -> SatisfyNode:
        """Parse a satisfy relationship."""
        start = self._current()
        self._expect(TokenType.SATISFY)

        name = None
        if self._match(TokenType.IDENTIFIER):
            first_id = self._advance().value
            if self._match(TokenType.COLON):
                name = first_id
                self._advance()

        requirement = ""
        if self._match(TokenType.IDENTIFIER):
            requirement = self._advance().value

        subject = ""
        if self._match(TokenType.BY):
            self._advance()
            if self._match(TokenType.IDENTIFIER):
                subject = self._advance().value
                while self._match(TokenType.DOT):
                    self._advance()
                    if self._match(TokenType.IDENTIFIER):
                        subject += "." + self._advance().value

        satisfy = SatisfyNode(
            name=name,
            requirement=requirement,
            subject=subject,
            location=self._location(start),
        )

        if self._match(TokenType.LBRACE):
            self._skip_block()
        elif self._match(TokenType.SEMICOLON):
            self._advance()

        return satisfy

    def _parse_doc(self) -> CommentNode:
        """Parse a doc comment."""
        start = self._current()
        self._expect(TokenType.DOC)

        text = self._parse_doc_content()

        return CommentNode(text=text, is_doc=True, location=self._location(start))

    def _parse_doc_content(self) -> str:
        """Parse the content of a doc comment."""
        self._expect(TokenType.DOC)

        if self._match(TokenType.COMMENT_BLOCK):
            token = self._advance()
            text = token.value
            # Extract text from /* ... */
            if text.startswith("/*"):
                text = text[2:]
            if text.endswith("*/"):
                text = text[:-2]
            return text.strip()

        return ""

    def _parse_alias(self) -> ImportNode:
        """Parse an alias declaration."""
        start = self._current()
        self._expect(TokenType.ALIAS)

        alias = ""
        if self._match(TokenType.IDENTIFIER):
            alias = self._advance().value

        path = ""
        if self._match(TokenType.FOR):
            self._advance()
            path_parts = []
            while self._match(TokenType.IDENTIFIER):
                path_parts.append(self._advance().value)
                if self._match(TokenType.COLONCOLON):
                    path_parts.append("::")
                    self._advance()
                else:
                    break
            path = "".join(path_parts)

        if self._match(TokenType.SEMICOLON):
            self._advance()

        return ImportNode(path=path, alias=alias, location=self._location(start))

    def _parse_perform(self) -> ActionNode:
        """Parse a perform statement."""
        start = self._current()
        self._expect(TokenType.PERFORM)

        name = ""
        if self._match(TokenType.IDENTIFIER):
            name = self._advance().value

        if self._match(TokenType.SEMICOLON):
            self._advance()

        return ActionNode(name=name, location=self._location(start))

    def _parse_exhibit(self) -> StateNode:
        """Parse an exhibit statement."""
        start = self._current()
        self._expect(TokenType.EXHIBIT)

        name = ""
        if self._match(TokenType.IDENTIFIER):
            name = self._advance().value

        if self._match(TokenType.SEMICOLON):
            self._advance()

        return StateNode(name=name, location=self._location(start))

    def _skip_block(self) -> None:
        """Skip a block enclosed in braces."""
        if not self._match(TokenType.LBRACE):
            return

        self._advance()  # Skip opening brace
        depth = 1

        while depth > 0 and not self._match(TokenType.EOF):
            if self._match(TokenType.LBRACE):
                depth += 1
            elif self._match(TokenType.RBRACE):
                depth -= 1
            self._advance()


def parse(source: str) -> ModelNode:
    """
    Convenience function to parse SysML v2 source code.

    Args:
        source: The SysML v2 source code to parse.

    Returns:
        The root ModelNode of the AST.
    """
    parser = SysMLParser(source)
    return parser.parse()
