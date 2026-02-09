import re
from dataclasses import dataclass


reserved_keywords = {
    "about", "abstract", "accept", "action", "actor", "after", "alias", "all", "allocate", "allocation", "analysis",
    "and", "as", "assert", "assign", "assume", "at", "attribute", "bind", "binding", "by", "calc", "case", "comment",
    "concern", "connect", "connection", "constant", "constraint", "crosses", "decide", "def", "default",
    "defined", "dependency", "derived", "do", "doc", "else", "end", "entry", "enum", "event", "exhibit", "exit", "expose",
    "false", "filter", "first", "flow", "for", "fork", "frame", "from", "hastype", "if", "implies", "import", "in", "include",
    "individual", "inout", "interface", "istype", "item", "join", "language", "library", "locale", "loop", "merge",
    "message", "meta", "metadata", "nonunique", "not", "null", "objective", "occurrence", "of", "or", "ordered", "out",
    "package", "parallel", "part", "perform", "port", "private", "protected", "public", "redefines", "ref",
    "references", "render", "rendering", "rep", "require", "requirement", "return", "satisfy", "send", "snapshot",
    "specializes", "stakeholder", "standard", "state", "subject", "subsets", "succession", "terminate", "then",
    "timeslice", "to", "transition", "true", "until", "use", "variant", "variation", "verification", "verify", "via",
    "view", "viewpoint", "when", "while", "xor",
}

@dataclass
class Token:
    value: str
    line_start: int
    line_end: int
    col_start: int
    col_end: int

# Regex pattern to tokenize SysML v2 code
# Matches: numbers, words (identifiers/keywords), multi-char operators, single-char operators, and whitespace
sysmlv2_pattern = r"""
    (?P<NUMBER>\d+\.?\d*(?:[eE][+-]?\d+)?)|  # Numbers: int, float, scientific notation
    (?P<WORD>[a-zA-Z_][a-zA-Z0-9_]*)|         # Words: identifiers and keywords
    (?P<OPERATOR>
        :>>|::>|:>|::|->|=>|<=|>=|==|!=|?=|+=|&&|\|\|| # Multi-character operators (longest first!)
        [+\-*/%=!<>:;,.\[\]{}()@?]                     # Single-character operators
    )|
    (?P<WHITESPACE>\s+)|                      # Whitespace (spaces, tabs, newlines)
    (?P<COMMENT>//.*?$|/\*.*?\*/)            # Comments (single-line and multi-line)
"""

def lexer(code: str) -> list[Token]:
    """
    Tokenize SysML v2 code into a list of tokens.
    
    Args:
        code: SysML v2 source code as a string
        
    Returns:
        List of Token objects containing value and line number
    """
    tokens = []
    line_num = 1
    
    for match in re.finditer(sysmlv2_pattern, code, re.MULTILINE | re.VERBOSE):
        token_type = match.lastgroup
        token_value = match.group()
        
        # Skip whitespace and comments, but count newlines for line tracking
        if token_type in ('WHITESPACE', 'COMMENT'):
            line_num += token_value.count('\n')
            continue
        
        tokens.append(Token(value=token_value, line_start=line_num, line_end=line_num, col_start=match.start(), col_end=match.end()))
        
    return tokens


# ============================================================================
# Examples
# ============================================================================

def example_basic():
    """Basic tokenization example"""
    code = "part def Vehicle { attribute mass : Real; }"
    tokens = lexer(code)
    print("Basic Example:")
    for token in tokens:
        print(f"  {token.value:15s} (line {token.line_start})")
    print()


def example_operators():
    """Operators and numbers example"""
    code = """
    constraint { x + y * 2.5 >= 100 && active == true }
    """
    tokens = lexer(code)
    print("Operators Example:")
    for token in tokens:
        print(f"  {token.value:15s} (line {token.line_start})")
    print()


def example_specialization():
    """SysML v2 specialization operators"""
    code = "part vehicle :> Vehicle :>> PhysicalItem;"
    tokens = lexer(code)
    print("Specialization Example:")
    for token in tokens:
        print(f"  {token.value:15s} (line {token.line_start})")
    print()


# ============================================================================
# Unit Tests
# ============================================================================

def test_numbers():
    """Test number tokenization"""
    code = "42 3.14 1.5e-10 0.001"
    tokens = lexer(code)
    assert len(tokens) == 4
    assert tokens[0].value == "42"
    assert tokens[1].value == "3.14"
    assert tokens[2].value == "1.5e-10"
    assert tokens[3].value == "0.001"
    print("✓ test_numbers passed")


def test_words():
    """Test identifier/keyword tokenization"""
    code = "part def attribute requirement"
    tokens = lexer(code)
    assert len(tokens) == 4
    assert tokens[0].value == "part"
    assert tokens[1].value == "def"
    assert tokens[2].value == "attribute"
    assert tokens[3].value == "requirement"
    print("✓ test_words passed")


def test_operators():
    """Test operator tokenization"""
    code = ":> :>> :: -> => == != && ||"
    tokens = lexer(code)
    # Debug: print actual tokens
    # print(f"Got {len(tokens)} tokens: {[t.value for t in tokens]}")
    assert len(tokens) == 9, f"Expected 9 tokens, got {len(tokens)}: {[t.value for t in tokens]}"
    assert tokens[0].value == ":>"
    assert tokens[1].value == ":>>"
    assert tokens[2].value == "::"
    assert tokens[3].value == "->"
    assert tokens[4].value == "=>"
    assert tokens[5].value == "=="
    assert tokens[6].value == "!="
    assert tokens[7].value == "&&"
    assert tokens[8].value == "||"
    print("✓ test_operators passed")


def test_single_char_operators():
    """Test single character operators"""
    code = "{}[]();,."
    tokens = lexer(code)
    assert len(tokens) == 9, f"Expected 9 tokens, got {len(tokens)}: {[t.value for t in tokens]}"
    assert tokens[0].value == "{"
    assert tokens[1].value == "}"
    assert tokens[2].value == "["
    assert tokens[3].value == "]"
    assert tokens[4].value == "("
    assert tokens[5].value == ")"
    assert tokens[6].value == ";"
    assert tokens[7].value == ","
    assert tokens[8].value == "."
    print("✓ test_single_char_operators passed")


def test_redefines_symbol():
    """Test REDEFINES symbol - both ':>>' operator and 'redefines' keyword"""
    # Test :>> operator
    code1 = "part vehicle :>> PhysicalItem;"
    tokens1 = lexer(code1)
    redefines_token = next(t for t in tokens1 if t.value == ":>>")
    assert redefines_token.value == ":>>"
    
    # Test 'redefines' keyword
    code2 = "part vehicle redefines PhysicalItem;"
    tokens2 = lexer(code2)
    redefines_keyword = next(t for t in tokens2 if t.value == "redefines")
    assert redefines_keyword.value == "redefines"
    
    # Test both forms work interchangeably
    assert any(t.value in [":>>", "redefines"] for t in tokens1)
    assert any(t.value in [":>>", "redefines"] for t in tokens2)
    print("✓ test_redefines_symbol passed")


def test_line_tracking():
    """Test line number tracking"""
    code = """part Vehicle {
    attribute mass : Real;
}"""
    tokens = lexer(code)
    # First token should be on line 1
    assert tokens[0].line_start == 1
    assert tokens[0].value == "part"
    # Find 'attribute' token - should be on line 2
    attr_token = next(t for t in tokens if t.value == "attribute")
    assert attr_token.line_start == 2
    print("✓ test_line_tracking passed")


def test_comments():
    """Test comment handling"""
    code = """
    // This is a comment
    part Vehicle {
        /* Multi-line
           comment */
        attribute mass;
    }
    """
    tokens = lexer(code)
    # Comments should be filtered out
    assert all(t.value not in ["//", "/*", "*/"] for t in tokens)
    # Should still have the actual tokens
    assert any(t.value == "part" for t in tokens)
    assert any(t.value == "Vehicle" for t in tokens)
    print("✓ test_comments passed")


def test_empty_string():
    """Test empty input"""
    tokens = lexer("")
    assert len(tokens) == 0
    print("✓ test_empty_string passed")


def test_sysml_sample():
    """Test realistic SysML v2 code"""
    code = """
    part def Vehicle :> Item {
        attribute mass : Real;
        part engine : Engine;
        
        constraint massLimit {
            mass <= 2000
        }
    }
    """
    tokens = lexer(code)
    assert len(tokens) > 0
    assert tokens[0].value == "part"
    assert any(t.value == ":>" for t in tokens)
    assert any(t.value == "<=" for t in tokens)
    print("✓ test_sysml_sample passed")


def run_all_tests():
    """Run all unit tests"""
    print("\n" + "="*50)
    print("Running Unit Tests")
    print("="*50)
    test_numbers()
    test_words()
    test_operators()
    test_single_char_operators()
    test_redefines_symbol()
    test_line_tracking()
    test_comments()
    test_empty_string()
    test_sysml_sample()
    print("="*50)
    print("All tests passed! ✓")
    print("="*50 + "\n")


def run_all_examples():
    """Run all examples"""
    print("\n" + "="*50)
    print("Examples")
    print("="*50)
    example_basic()
    example_operators()
    example_specialization()
    print("="*50 + "\n")


if __name__ == "__main__":
    run_all_examples()
    run_all_tests()
