"""
SysML v2 Parser for Python

A parser for the SysML v2 textual notation, providing syntax validation,
AST generation, and element extraction.

Based on the SysML v2 specification from Systems-Modeling/SysML-v2-Release.
"""

from .lexer import SysMLLexer, Token, TokenType, tokenize
from .parser import SysMLParser, parse
from .ast_nodes import (
    ASTNode,
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
    ConstraintDefNode,
    ConnectionNode,
    ImportNode,
    CommentNode,
)
from .extractor import SysMLExtractor, ExtractedModel, extract
from .validator import SysMLValidator, ValidationResult, SysMLSyntaxError, validate, is_valid

# Backwards compatibility alias
SyntaxError = SysMLSyntaxError

__all__ = [
    # Lexer
    "SysMLLexer",
    "Token",
    "TokenType",
    "tokenize",
    # Parser
    "SysMLParser",
    "parse",
    # AST Nodes
    "ASTNode",
    "PackageNode",
    "PartDefNode",
    "PartNode",
    "PortDefNode",
    "PortNode",
    "AttributeNode",
    "ActionDefNode",
    "ActionNode",
    "StateDefNode",
    "StateNode",
    "TransitionNode",
    "RequirementDefNode",
    "RequirementNode",
    "ConstraintDefNode",
    "ConnectionNode",
    "ImportNode",
    "CommentNode",
    # Extractor
    "SysMLExtractor",
    "ExtractedModel",
    "extract",
    # Validator
    "SysMLValidator",
    "ValidationResult",
    "SysMLSyntaxError",
    "SyntaxError",  # Backwards compatibility alias
    "validate",
    "is_valid",
]

__version__ = "0.1.0"
