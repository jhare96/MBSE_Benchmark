"""
SysML v2 Lexer (Tokenizer)

Tokenizes SysML v2 textual notation into a stream of tokens for parsing.

Reference: SysML v2 Language Specification
https://github.com/Systems-Modeling/SysML-v2-Release
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Iterator
import re


class TokenType(Enum):
    """Token types for SysML v2 textual notation."""

    # Keywords - Definitions
    PACKAGE = auto()
    PART = auto()
    PART_DEF = auto()
    PORT = auto()
    PORT_DEF = auto()
    ATTRIBUTE = auto()
    ATTRIBUTE_DEF = auto()
    ITEM = auto()
    ITEM_DEF = auto()
    ACTION = auto()
    ACTION_DEF = auto()
    STATE = auto()
    STATE_DEF = auto()
    REQUIREMENT = auto()
    REQUIREMENT_DEF = auto()
    CONSTRAINT = auto()
    CONSTRAINT_DEF = auto()
    INTERFACE = auto()
    INTERFACE_DEF = auto()
    CONNECTION = auto()
    CONNECTION_DEF = auto()
    CALC = auto()
    CALC_DEF = auto()
    USE_CASE = auto()
    ALLOCATION = auto()
    ALLOCATION_DEF = auto()
    VIEW = auto()
    VIEW_DEF = auto()
    VIEWPOINT = auto()
    VIEWPOINT_DEF = auto()
    RENDERING = auto()
    RENDERING_DEF = auto()
    CONCERN = auto()
    CONCERN_DEF = auto()
    STAKEHOLDER = auto()
    METADATA = auto()
    METADATA_DEF = auto()
    OCCURRENCE = auto()
    OCCURRENCE_DEF = auto()
    VARIATION = auto()
    VARIANT = auto()

    # Relationship Keywords
    SPECIALIZES = auto()
    SUBSETS = auto()
    REDEFINES = auto()
    CONNECT = auto()
    BIND = auto()
    FLOW = auto()
    STREAM = auto()
    MESSAGE = auto()
    SUCCESSION = auto()
    TRANSITION = auto()
    SATISFY = auto()
    REQUIRE = auto()
    ASSERT = auto()
    ASSUME = auto()

    # Port Direction
    IN = auto()
    OUT = auto()
    INOUT = auto()

    # State Machine
    ENTRY = auto()
    EXIT = auto()
    DO = auto()
    FIRST = auto()
    THEN = auto()
    ACCEPT = auto()

    # Control Flow
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    LOOP = auto()
    FOR = auto()
    MERGE = auto()
    DECIDE = auto()
    JOIN = auto()
    FORK = auto()
    FILTER = auto()

    # Modifiers
    ABSTRACT = auto()
    INDIVIDUAL = auto()
    REF = auto()
    PRIVATE = auto()
    PUBLIC = auto()
    PROTECTED = auto()
    STANDARD = auto()
    LIBRARY = auto()
    NONUNIQUE = auto()
    ORDERED = auto()
    READONLY = auto()

    # Other Keywords
    IMPORT = auto()
    ALIAS = auto()
    DOC = auto()
    COMMENT = auto()
    ABOUT = auto()
    EXHIBIT = auto()
    EXPOSE = auto()
    PERFORM = auto()
    SEND = auto()
    TO = auto()
    VIA = auto()
    FROM = auto()
    ALL = auto()
    AS = auto()
    BY = auto()
    CASE = auto()

    # Symbols
    LBRACE = auto()  # {
    RBRACE = auto()  # }
    LPAREN = auto()  # (
    RPAREN = auto()  # )
    LBRACKET = auto()  # [
    RBRACKET = auto()  # ]
    SEMICOLON = auto()  # ;
    COLON = auto()  # :
    COLONCOLON = auto()  # ::
    COLON_GT = auto()  # :>
    COLON_GTGT = auto()  # :>>
    COMMA = auto()  # ,
    DOT = auto()  # .
    DOTDOT = auto()  # ..
    EQUALS = auto()  # =
    EQEQ = auto()  # ==
    NEQ = auto()  # !=
    LT = auto()  # <
    GT = auto()  # >
    LTEQ = auto()  # <=
    GTEQ = auto()  # >=
    PLUS = auto()  # +
    MINUS = auto()  # -
    STAR = auto()  # *
    SLASH = auto()  # /
    PERCENT = auto()  # %
    AMPERSAND = auto()  # &
    PIPE = auto()  # |
    CARET = auto()  # ^
    TILDE = auto()  # ~
    EXCLAIM = auto()  # !
    QUESTION = auto()  # ?
    ARROW = auto()  # ->
    HASH = auto()  # #
    AT = auto()  # @

    # Literals
    IDENTIFIER = auto()
    STRING = auto()
    NUMBER = auto()
    BOOLEAN = auto()

    # Special
    COMMENT_BLOCK = auto()
    COMMENT_LINE = auto()
    DOC_COMMENT = auto()
    WHITESPACE = auto()
    NEWLINE = auto()
    EOF = auto()
    UNKNOWN = auto()


@dataclass
class Token:
    """A token from the SysML v2 lexer."""

    type: TokenType
    value: str
    line: int
    column: int

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, {self.line}:{self.column})"


# Keywords mapping (lowercase for case-sensitive matching)
KEYWORDS: dict[str, TokenType] = {
    # Definitions
    "package": TokenType.PACKAGE,
    "part": TokenType.PART,
    "port": TokenType.PORT,
    "attribute": TokenType.ATTRIBUTE,
    "item": TokenType.ITEM,
    "action": TokenType.ACTION,
    "state": TokenType.STATE,
    "requirement": TokenType.REQUIREMENT,
    "constraint": TokenType.CONSTRAINT,
    "interface": TokenType.INTERFACE,
    "connection": TokenType.CONNECTION,
    "calc": TokenType.CALC,
    "allocation": TokenType.ALLOCATION,
    "view": TokenType.VIEW,
    "viewpoint": TokenType.VIEWPOINT,
    "rendering": TokenType.RENDERING,
    "concern": TokenType.CONCERN,
    "stakeholder": TokenType.STAKEHOLDER,
    "metadata": TokenType.METADATA,
    "occurrence": TokenType.OCCURRENCE,
    "variation": TokenType.VARIATION,
    "variant": TokenType.VARIANT,
    "def": TokenType.IDENTIFIER,  # 'def' is handled specially
    # Relationships
    "specializes": TokenType.SPECIALIZES,
    "subsets": TokenType.SUBSETS,
    "redefines": TokenType.REDEFINES,
    "connect": TokenType.CONNECT,
    "bind": TokenType.BIND,
    "flow": TokenType.FLOW,
    "stream": TokenType.STREAM,
    "message": TokenType.MESSAGE,
    "succession": TokenType.SUCCESSION,
    "transition": TokenType.TRANSITION,
    "satisfy": TokenType.SATISFY,
    "require": TokenType.REQUIRE,
    "assert": TokenType.ASSERT,
    "assume": TokenType.ASSUME,
    # Port direction
    "in": TokenType.IN,
    "out": TokenType.OUT,
    "inout": TokenType.INOUT,
    # State machine
    "entry": TokenType.ENTRY,
    "exit": TokenType.EXIT,
    "do": TokenType.DO,
    "first": TokenType.FIRST,
    "then": TokenType.THEN,
    "accept": TokenType.ACCEPT,
    # Control flow
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "loop": TokenType.LOOP,
    "for": TokenType.FOR,
    "merge": TokenType.MERGE,
    "decide": TokenType.DECIDE,
    "join": TokenType.JOIN,
    "fork": TokenType.FORK,
    "filter": TokenType.FILTER,
    # Modifiers
    "abstract": TokenType.ABSTRACT,
    "individual": TokenType.INDIVIDUAL,
    "ref": TokenType.REF,
    "private": TokenType.PRIVATE,
    "public": TokenType.PUBLIC,
    "protected": TokenType.PROTECTED,
    "standard": TokenType.STANDARD,
    "library": TokenType.LIBRARY,
    "nonunique": TokenType.NONUNIQUE,
    "ordered": TokenType.ORDERED,
    "readonly": TokenType.READONLY,
    # Other
    "import": TokenType.IMPORT,
    "alias": TokenType.ALIAS,
    "doc": TokenType.DOC,
    "comment": TokenType.COMMENT,
    "about": TokenType.ABOUT,
    "exhibit": TokenType.EXHIBIT,
    "expose": TokenType.EXPOSE,
    "perform": TokenType.PERFORM,
    "send": TokenType.SEND,
    "to": TokenType.TO,
    "via": TokenType.VIA,
    "from": TokenType.FROM,
    "all": TokenType.ALL,
    "as": TokenType.AS,
    "by": TokenType.BY,
    "case": TokenType.CASE,
    # Booleans
    "true": TokenType.BOOLEAN,
    "false": TokenType.BOOLEAN,
}

# Two-keyword definitions that combine to form a single token type
TWO_WORD_KEYWORDS: dict[tuple[str, str], TokenType] = {
    ("part", "def"): TokenType.PART_DEF,
    ("port", "def"): TokenType.PORT_DEF,
    ("attribute", "def"): TokenType.ATTRIBUTE_DEF,
    ("item", "def"): TokenType.ITEM_DEF,
    ("action", "def"): TokenType.ACTION_DEF,
    ("state", "def"): TokenType.STATE_DEF,
    ("requirement", "def"): TokenType.REQUIREMENT_DEF,
    ("constraint", "def"): TokenType.CONSTRAINT_DEF,
    ("interface", "def"): TokenType.INTERFACE_DEF,
    ("connection", "def"): TokenType.CONNECTION_DEF,
    ("calc", "def"): TokenType.CALC_DEF,
    ("allocation", "def"): TokenType.ALLOCATION_DEF,
    ("view", "def"): TokenType.VIEW_DEF,
    ("viewpoint", "def"): TokenType.VIEWPOINT_DEF,
    ("rendering", "def"): TokenType.RENDERING_DEF,
    ("concern", "def"): TokenType.CONCERN_DEF,
    ("metadata", "def"): TokenType.METADATA_DEF,
    ("occurrence", "def"): TokenType.OCCURRENCE_DEF,
    ("use", "case"): TokenType.USE_CASE,
}


class SysMLLexer:
    """
    Lexer for SysML v2 textual notation.

    Converts source text into a stream of tokens.

    Example:
        >>> lexer = SysMLLexer("package Vehicle { part engine : Engine; }")
        >>> tokens = list(lexer.tokenize())
        >>> for token in tokens:
        ...     print(token)
    """

    def __init__(self, source: str):
        """
        Initialize the lexer with source code.

        Args:
            source: The SysML v2 source code to tokenize.
        """
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self._length = len(source)

    def _current_char(self) -> str | None:
        """Return the current character or None if at end."""
        if self.pos >= self._length:
            return None
        return self.source[self.pos]

    def _peek(self, offset: int = 1) -> str | None:
        """Peek at a character ahead of the current position."""
        pos = self.pos + offset
        if pos >= self._length:
            return None
        return self.source[pos]

    def _advance(self, count: int = 1) -> str:
        """Advance the position and return consumed characters."""
        result = self.source[self.pos : self.pos + count]
        for char in result:
            if char == "\n":
                self.line += 1
                self.column = 1
            else:
                self.column += 1
        self.pos += count
        return result

    def _skip_whitespace(self) -> Token | None:
        """Skip whitespace and optionally return a whitespace token."""
        start_line = self.line
        start_column = self.column
        start_pos = self.pos

        while self._current_char() is not None and self._current_char() in " \t\r\n":
            self._advance()

        if self.pos > start_pos:
            value = self.source[start_pos : self.pos]
            return Token(TokenType.WHITESPACE, value, start_line, start_column)
        return None

    def _read_string(self) -> Token:
        """Read a string literal (single or double quoted)."""
        start_line = self.line
        start_column = self.column
        quote_char = self._current_char()
        self._advance()  # Skip opening quote

        value = quote_char
        escaped = False

        while self._current_char() is not None:
            char = self._current_char()
            value += self._advance()

            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote_char:
                break

        return Token(TokenType.STRING, value, start_line, start_column)

    def _read_number(self) -> Token:
        """Read a numeric literal."""
        start_line = self.line
        start_column = self.column
        start_pos = self.pos

        # Integer part
        while self._current_char() is not None and self._current_char().isdigit():
            self._advance()

        # Decimal part
        if self._current_char() == "." and self._peek() and self._peek().isdigit():
            self._advance()  # Skip '.'
            while self._current_char() is not None and self._current_char().isdigit():
                self._advance()

        # Exponent part
        if self._current_char() in ("e", "E"):
            self._advance()
            if self._current_char() in ("+", "-"):
                self._advance()
            while self._current_char() is not None and self._current_char().isdigit():
                self._advance()

        value = self.source[start_pos : self.pos]
        return Token(TokenType.NUMBER, value, start_line, start_column)

    def _read_identifier_or_keyword(self) -> Token:
        """Read an identifier or keyword."""
        start_line = self.line
        start_column = self.column
        start_pos = self.pos

        # First character must be letter or underscore
        while self._current_char() is not None and (
            self._current_char().isalnum() or self._current_char() == "_"
        ):
            self._advance()

        value = self.source[start_pos : self.pos]

        # Check for keyword
        token_type = KEYWORDS.get(value, TokenType.IDENTIFIER)

        return Token(token_type, value, start_line, start_column)

    def _read_block_comment(self) -> Token:
        """Read a block comment /* ... */."""
        start_line = self.line
        start_column = self.column
        start_pos = self.pos

        self._advance(2)  # Skip /*

        while self._current_char() is not None:
            if self._current_char() == "*" and self._peek() == "/":
                self._advance(2)  # Skip */
                break
            self._advance()

        value = self.source[start_pos : self.pos]

        # Check if it's a doc comment
        if value.startswith("/**") or value.startswith("/*"):
            return Token(TokenType.COMMENT_BLOCK, value, start_line, start_column)
        return Token(TokenType.COMMENT_BLOCK, value, start_line, start_column)

    def _read_line_comment(self) -> Token:
        """Read a line comment // ... ."""
        start_line = self.line
        start_column = self.column
        start_pos = self.pos

        while self._current_char() is not None and self._current_char() != "\n":
            self._advance()

        value = self.source[start_pos : self.pos]
        return Token(TokenType.COMMENT_LINE, value, start_line, start_column)

    def _read_symbol(self) -> Token:
        """Read a symbol token."""
        start_line = self.line
        start_column = self.column
        char = self._current_char()
        next_char = self._peek()
        next_next_char = self._peek(2)

        # Three-character tokens
        if char == ":" and next_char == ">" and next_next_char == ">":
            self._advance(3)
            return Token(TokenType.COLON_GTGT, ":>>", start_line, start_column)

        # Two-character tokens
        two_char = char + (next_char or "")
        two_char_tokens = {
            "::": TokenType.COLONCOLON,
            ":>": TokenType.COLON_GT,
            "..": TokenType.DOTDOT,
            "==": TokenType.EQEQ,
            "!=": TokenType.NEQ,
            "<=": TokenType.LTEQ,
            ">=": TokenType.GTEQ,
            "->": TokenType.ARROW,
        }

        if two_char in two_char_tokens:
            self._advance(2)
            return Token(two_char_tokens[two_char], two_char, start_line, start_column)

        # Single-character tokens
        single_char_tokens = {
            "{": TokenType.LBRACE,
            "}": TokenType.RBRACE,
            "(": TokenType.LPAREN,
            ")": TokenType.RPAREN,
            "[": TokenType.LBRACKET,
            "]": TokenType.RBRACKET,
            ";": TokenType.SEMICOLON,
            ":": TokenType.COLON,
            ",": TokenType.COMMA,
            ".": TokenType.DOT,
            "=": TokenType.EQUALS,
            "<": TokenType.LT,
            ">": TokenType.GT,
            "+": TokenType.PLUS,
            "-": TokenType.MINUS,
            "*": TokenType.STAR,
            "/": TokenType.SLASH,
            "%": TokenType.PERCENT,
            "&": TokenType.AMPERSAND,
            "|": TokenType.PIPE,
            "^": TokenType.CARET,
            "~": TokenType.TILDE,
            "!": TokenType.EXCLAIM,
            "?": TokenType.QUESTION,
            "#": TokenType.HASH,
            "@": TokenType.AT,
        }

        if char in single_char_tokens:
            self._advance()
            return Token(single_char_tokens[char], char, start_line, start_column)

        # Unknown character
        self._advance()
        return Token(TokenType.UNKNOWN, char, start_line, start_column)

    def tokenize(self, include_whitespace: bool = False, include_comments: bool = True) -> Iterator[Token]:
        """
        Tokenize the source code into a stream of tokens.

        Args:
            include_whitespace: If True, include whitespace tokens.
            include_comments: If True, include comment tokens.

        Yields:
            Token objects representing the lexical elements.
        """
        pending_tokens: list[Token] = []

        while self.pos < self._length:
            char = self._current_char()

            # Skip whitespace
            ws_token = self._skip_whitespace()
            if ws_token and include_whitespace:
                pending_tokens.append(ws_token)

            if self.pos >= self._length:
                break

            char = self._current_char()

            # Comments
            if char == "/":
                next_char = self._peek()
                if next_char == "*":
                    token = self._read_block_comment()
                    if include_comments:
                        pending_tokens.append(token)
                    continue
                elif next_char == "/":
                    token = self._read_line_comment()
                    if include_comments:
                        pending_tokens.append(token)
                    continue

            # String literals
            if char in ('"', "'"):
                pending_tokens.append(self._read_string())
                continue

            # Numbers
            if char.isdigit():
                pending_tokens.append(self._read_number())
                continue

            # Identifiers and keywords
            if char.isalpha() or char == "_":
                token = self._read_identifier_or_keyword()
                pending_tokens.append(token)
                continue

            # Symbols
            pending_tokens.append(self._read_symbol())

        # Process pending tokens to combine two-word keywords
        tokens = self._combine_two_word_keywords(pending_tokens)

        for token in tokens:
            yield token

        # EOF token
        yield Token(TokenType.EOF, "", self.line, self.column)

    def _combine_two_word_keywords(self, tokens: list[Token]) -> list[Token]:
        """Combine two-word keywords like 'part def' into single tokens."""
        result: list[Token] = []
        i = 0

        while i < len(tokens):
            token = tokens[i]

            # Skip non-keyword tokens
            if token.type in (TokenType.WHITESPACE, TokenType.COMMENT_LINE, TokenType.COMMENT_BLOCK):
                result.append(token)
                i += 1
                continue

            # Check for two-word keyword
            if i + 1 < len(tokens):
                # Look ahead, skipping whitespace and comments
                next_idx = i + 1
                while next_idx < len(tokens) and tokens[next_idx].type in (
                    TokenType.WHITESPACE,
                    TokenType.COMMENT_LINE,
                    TokenType.COMMENT_BLOCK,
                ):
                    next_idx += 1

                if next_idx < len(tokens):
                    next_token = tokens[next_idx]
                    key = (token.value, next_token.value)

                    if key in TWO_WORD_KEYWORDS:
                        combined_type = TWO_WORD_KEYWORDS[key]
                        combined_value = f"{token.value} {next_token.value}"
                        result.append(Token(combined_type, combined_value, token.line, token.column))

                        # Skip to after the second keyword, but include intermediate whitespace/comments
                        for j in range(i + 1, next_idx):
                            result.append(tokens[j])
                        i = next_idx + 1
                        continue

            result.append(token)
            i += 1

        return result


def tokenize(source: str, include_whitespace: bool = False, include_comments: bool = True) -> list[Token]:
    """
    Convenience function to tokenize SysML v2 source code.

    Args:
        source: The SysML v2 source code to tokenize.
        include_whitespace: If True, include whitespace tokens.
        include_comments: If True, include comment tokens.

    Returns:
        A list of Token objects.
    """
    lexer = SysMLLexer(source)
    return list(lexer.tokenize(include_whitespace, include_comments))
