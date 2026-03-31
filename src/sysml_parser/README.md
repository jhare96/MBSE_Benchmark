# SysML v2 Python Parser

A Python parser for the SysML v2 textual notation, providing syntax validation, AST generation, and element extraction.

## Overview

This parser is designed to work with SysML v2 textual notation as defined in the [SysML v2 specification](https://github.com/Systems-Modeling/SysML-v2-Release). It provides:

- **Lexer**: Tokenizes SysML v2 source code
- **Parser**: Generates an Abstract Syntax Tree (AST)
- **Extractor**: Extracts structured information from models
- **Validator**: Validates syntax correctness

## Installation

The parser is included in the MBSE Benchmark repository. No additional dependencies are required - it uses only Python standard library.

## Quick Start

```python
from src.sysml_parser import parse, extract, validate

# Parse SysML v2 source code
source = """
package VehicleModel {
    part def Engine {
        attribute power : Real = 200.0;
    }

    part def Vehicle {
        part engine : Engine;
    }
}
"""

# Validate syntax
result = validate(source)
print(f"Valid: {result.valid}")
print(f"Elements: {result.elements}")

# Extract model information
model = extract(source)
print(f"Part definitions: {[p.name for p in model.part_defs]}")
print(f"Parts: {[p.name for p in model.parts]}")

# Parse into AST for detailed analysis
ast = parse(source)
for pkg in ast.packages:
    print(f"Package: {pkg.name}")
    for member in pkg.members:
        print(f"  - {type(member).__name__}: {member.name}")
```

## Usage

### Validation

Use the validator to check if SysML v2 code is syntactically correct:

```python
from src.sysml_parser import validate, is_valid

# Quick check
if is_valid(source):
    print("Syntax is valid!")

# Detailed validation
result = validate(source)
if not result.valid:
    for error in result.errors:
        print(f"Error at {error.line}:{error.column}: {error.message}")
for warning in result.warnings:
    print(f"Warning at {warning.line}:{warning.column}: {warning.message}")
```

### Extraction

Extract structured information from SysML v2 models:

```python
from src.sysml_parser import extract

model = extract(source)

# Access extracted elements
print("Packages:", [p.name for p in model.packages])
print("Part definitions:", [p.name for p in model.part_defs])
print("Parts:", [p.name for p in model.parts])
print("Port definitions:", [p.name for p in model.port_defs])
print("Ports:", [p.name for p in model.ports])
print("Attributes:", len(model.attributes))
print("Connections:", len(model.connections))
print("Requirements:", [r.name for r in model.requirements])
print("States:", [s.name for s in model.states])
print("Transitions:", len(model.transitions))
print("Actions:", [a.name for a in model.actions])
```

### Parsing

For full AST access:

```python
from src.sysml_parser import parse

ast = parse(source)

# Walk the AST
for package in ast.packages:
    print(f"Package: {package.name}")
    for member in package.members:
        if hasattr(member, 'name'):
            print(f"  {type(member).__name__}: {member.name}")
```

### Tokenization

For low-level token access:

```python
from src.sysml_parser import tokenize

tokens = tokenize(source)
for token in tokens:
    print(f"{token.type.name}: {token.value!r} at {token.line}:{token.column}")
```

## Supported SysML v2 Constructs

The parser supports the following SysML v2 elements:

### Definitions

- `package` - Package definitions
- `part def` - Part definitions
- `port def` - Port definitions
- `attribute def` - Attribute definitions
- `item def` - Item definitions
- `action def` - Action definitions
- `state def` - State definitions
- `requirement def` - Requirement definitions
- `constraint def` - Constraint definitions
- `interface def` - Interface definitions
- `connection def` - Connection definitions
- `calc def` - Calculation definitions
- `use case` - Use case definitions

### Usages

- `part` - Part usages
- `port` - Port usages (with `in`, `out`, `inout` directions)
- `attribute` - Attribute usages
- `item` - Item usages
- `action` - Action usages
- `state` - State usages
- `requirement` - Requirement usages
- `constraint` - Constraint usages
- `connect` - Connection statements
- `bind` - Binding statements

### Relationships

- `:>` - Specialization (extends)
- `:>>` - Redefinition
- `satisfy` - Requirement satisfaction
- `transition` - State transitions
- `succession` - Successions

### Other

- `import` - Import statements
- `alias` - Aliases
- `doc` - Documentation comments
- Block comments (`/* */`)
- Line comments (`//`)

## API Reference

### Main Classes

#### `SysMLValidator`

Validates SysML v2 syntax.

```python
validator = SysMLValidator(source)
result = validator.validate()
```

#### `SysMLExtractor`

Extracts structured information.

```python
extractor = SysMLExtractor(source)
model = extractor.extract()
```

#### `SysMLParser`

Parses source into AST.

```python
parser = SysMLParser(source)
ast = parser.parse()
```

#### `SysMLLexer`

Tokenizes source code.

```python
lexer = SysMLLexer(source)
tokens = list(lexer.tokenize())
```

### Data Classes

#### `ValidationResult`

- `valid: bool` - Whether the source is valid
- `errors: list[SyntaxError]` - List of errors
- `warnings: list[SyntaxError]` - List of warnings
- `elements: dict` - Count of each element type

#### `ExtractedModel`

- `packages: list[PackageInfo]`
- `part_defs: list[PartDefInfo]`
- `parts: list[PartInfo]`
- `port_defs: list[PortDefInfo]`
- `ports: list[PortInfo]`
- `attributes: list[AttributeInfo]`
- `connections: list[ConnectionInfo]`
- `requirements: list[RequirementInfo]`
- `states: list[StateInfo]`
- `transitions: list[TransitionInfo]`
- `actions: list[ActionInfo]`
- `item_defs: list[ItemDefInfo]`

## Examples

### Vehicle Model

```python
source = """
package VehicleModel {
    requirement def VehicleMassRequirement {
        doc /* The vehicle mass shall not exceed 2000 kg. */
        attribute massActual : Real;
        attribute massLimit : Real = 2000.0;
    }

    part def Engine {
        attribute mass : Real = 800.0;
        attribute power : Real = 200.0;
    }

    part def Vehicle {
        attribute totalMass : Real;
        part engine : Engine;

        satisfy massReq : VehicleMassRequirement by Vehicle;
    }
}
"""

model = extract(source)
print(f"Requirements: {[r.name for r in model.requirements]}")
# Output: Requirements: ['VehicleMassRequirement']
```

### State Machine

```python
source = """
state def TrafficLight {
    first state Red {
        entry turnOnRed;
        exit turnOffRed;
    }
    state Yellow;
    state Green;

    transition Red then Green;
    transition Green then Yellow;
    transition Yellow then Red;
}
"""

model = extract(source)
print(f"States: {[s.name for s in model.states]}")
# Output: States: ['Red', 'Yellow', 'Green']
print(f"Transitions: {len(model.transitions)}")
# Output: Transitions: 3
```

### Factory Model with Connections

```python
source = """
package FactoryModel {
    port def ProductPort {
        out item product : Product;
    }

    part def Machine {
        in port materialIn : MaterialPort;
        out port productOut : ProductPort;
    }

    part def Factory {
        part machineA : Machine;
        part machineB : Machine;
        connect machineA.productOut to machineB.materialIn;
    }
}
"""

model = extract(source)
print(f"Connections: {len(model.connections)}")
for conn in model.connections:
    print(f"  {conn.source} -> {conn.target}")
```

## Running Tests

```bash
cd /home/runner/work/MBSE_Benchmark/MBSE_Benchmark
python -m unittest src.sysml_parser.test_parser -v
```

## Reference

- [SysML v2 Release Repository](https://github.com/Systems-Modeling/SysML-v2-Release)
- [SysML v2 Language Introduction](https://github.com/Systems-Modeling/SysML-v2-Release/blob/master/doc/Intro%20to%20the%20SysML%20v2%20Language-Textual%20Notation.pdf)
- [SysML v2 Standard Library](https://github.com/Systems-Modeling/SysML-v2-Release/tree/master/sysml.library)

## License

This parser is part of the MBSE Benchmark project and is licensed under the MIT License.
