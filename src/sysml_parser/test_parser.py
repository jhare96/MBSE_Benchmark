"""
Tests for the SysML v2 Parser

Unit tests for the lexer, parser, extractor, and validator.
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sysml_parser.lexer import SysMLLexer, TokenType, tokenize
from sysml_parser.parser import SysMLParser, parse
from sysml_parser.extractor import SysMLExtractor, extract, extract_part_def_names
from sysml_parser.validator import SysMLValidator, validate, is_valid
from sysml_parser.ast_nodes import PackageNode, PartDefNode, PartNode


class TestLexer(unittest.TestCase):
    """Tests for the SysML v2 lexer."""

    def test_tokenize_simple_package(self):
        """Test tokenizing a simple package."""
        source = "package Vehicle {}"
        tokens = tokenize(source)

        # Filter out EOF and comments
        tokens = [t for t in tokens if t.type != TokenType.EOF]

        self.assertEqual(tokens[0].type, TokenType.PACKAGE)
        self.assertEqual(tokens[1].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[1].value, "Vehicle")
        self.assertEqual(tokens[2].type, TokenType.LBRACE)
        self.assertEqual(tokens[3].type, TokenType.RBRACE)

    def test_tokenize_part_def(self):
        """Test tokenizing a part definition."""
        source = "part def Engine { attribute power : Real; }"
        tokens = tokenize(source)

        tokens = [t for t in tokens if t.type != TokenType.EOF]

        self.assertEqual(tokens[0].type, TokenType.PART_DEF)
        self.assertEqual(tokens[0].value, "part def")
        self.assertEqual(tokens[1].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[1].value, "Engine")

    def test_tokenize_specialization(self):
        """Test tokenizing specialization syntax."""
        source = "part def SportsCar :> Car {}"
        tokens = tokenize(source)

        types = [t.type for t in tokens if t.type != TokenType.EOF]
        self.assertIn(TokenType.COLON_GT, types)

    def test_tokenize_string_literal(self):
        """Test tokenizing string literals."""
        source = 'attribute name : String = "MyName";'
        tokens = tokenize(source)

        string_tokens = [t for t in tokens if t.type == TokenType.STRING]
        self.assertEqual(len(string_tokens), 1)
        self.assertEqual(string_tokens[0].value, '"MyName"')

    def test_tokenize_number_literal(self):
        """Test tokenizing number literals."""
        source = "attribute mass : Real = 100.5;"
        tokens = tokenize(source)

        number_tokens = [t for t in tokens if t.type == TokenType.NUMBER]
        self.assertEqual(len(number_tokens), 1)
        self.assertEqual(number_tokens[0].value, "100.5")

    def test_tokenize_line_comment(self):
        """Test tokenizing line comments."""
        source = "// This is a comment\npackage P {}"
        tokens = tokenize(source, include_comments=True)

        comment_tokens = [t for t in tokens if t.type == TokenType.COMMENT_LINE]
        self.assertEqual(len(comment_tokens), 1)

    def test_tokenize_block_comment(self):
        """Test tokenizing block comments."""
        source = "/* This is a block comment */ package P {}"
        tokens = tokenize(source, include_comments=True)

        comment_tokens = [t for t in tokens if t.type == TokenType.COMMENT_BLOCK]
        self.assertEqual(len(comment_tokens), 1)

    def test_tokenize_keywords(self):
        """Test that keywords are recognized."""
        keywords = ["package", "import", "action", "state", "requirement", "constraint"]
        for kw in keywords:
            tokens = tokenize(kw)
            # Check that it's not just an identifier
            self.assertNotEqual(tokens[0].type, TokenType.IDENTIFIER)


class TestParser(unittest.TestCase):
    """Tests for the SysML v2 parser."""

    def test_parse_empty_package(self):
        """Test parsing an empty package."""
        source = "package Vehicle {}"
        model = parse(source)

        self.assertEqual(len(model.packages), 1)
        self.assertEqual(model.packages[0].name, "Vehicle")

    def test_parse_package_with_import(self):
        """Test parsing a package with imports."""
        source = """
        package Vehicle {
            import Parts::*;
        }
        """
        model = parse(source)

        self.assertEqual(len(model.packages), 1)
        self.assertEqual(len(model.packages[0].imports), 1)
        self.assertEqual(model.packages[0].imports[0].path, "Parts::*")

    def test_parse_part_def(self):
        """Test parsing a part definition."""
        source = """
        part def Engine {
            attribute power : Real;
        }
        """
        model = parse(source)

        self.assertEqual(len(model.members), 1)
        part_def = model.members[0]
        self.assertIsInstance(part_def, PartDefNode)
        self.assertEqual(part_def.name, "Engine")
        self.assertEqual(len(part_def.attributes), 1)
        self.assertEqual(part_def.attributes[0].name, "power")

    def test_parse_part_def_with_specialization(self):
        """Test parsing a part definition with specialization."""
        source = "part def SportsCar :> Car {}"
        model = parse(source)

        part_def = model.members[0]
        self.assertEqual(part_def.name, "SportsCar")
        self.assertEqual(part_def.parent, "Car")

    def test_parse_part_usage(self):
        """Test parsing a part usage."""
        source = """
        part def Vehicle {
            part engine : Engine;
        }
        """
        model = parse(source)

        part_def = model.members[0]
        self.assertEqual(len(part_def.parts), 1)
        self.assertEqual(part_def.parts[0].name, "engine")

    def test_parse_port_def(self):
        """Test parsing a port definition."""
        source = """
        port def FuelPort {
            out item fuel : Fuel;
        }
        """
        model = parse(source)

        self.assertEqual(len(model.members), 1)
        self.assertEqual(model.members[0].name, "FuelPort")

    def test_parse_requirement_def(self):
        """Test parsing a requirement definition."""
        source = """
        requirement def MassRequirement {
            doc /* The vehicle mass shall not exceed the limit. */
            attribute massActual : Real;
            attribute massLimit : Real;
        }
        """
        model = parse(source)

        self.assertEqual(len(model.members), 1)
        req_def = model.members[0]
        self.assertEqual(req_def.name, "MassRequirement")

    def test_parse_state_def(self):
        """Test parsing a state definition."""
        source = """
        state def VehicleState {
            first state Idle;
            state Running;
            transition Idle then Running;
        }
        """
        model = parse(source)

        self.assertEqual(len(model.members), 1)
        state_def = model.members[0]
        self.assertEqual(state_def.name, "VehicleState")
        self.assertEqual(len(state_def.states), 2)
        self.assertEqual(len(state_def.transitions), 1)

    def test_parse_action_def(self):
        """Test parsing an action definition."""
        source = """
        action def Accelerate {
            in pedal : PedalPosition;
            out torque : Torque;
        }
        """
        model = parse(source)

        self.assertEqual(len(model.members), 1)
        action_def = model.members[0]
        self.assertEqual(action_def.name, "Accelerate")
        self.assertEqual(len(action_def.inputs), 1)
        self.assertEqual(len(action_def.outputs), 1)

    def test_parse_connect(self):
        """Test parsing a connect statement."""
        source = """
        part def System {
            part a : A;
            part b : B;
            connect a.out to b.in;
        }
        """
        model = parse(source)

        part_def = model.members[0]
        self.assertEqual(len(part_def.connections), 1)
        self.assertEqual(part_def.connections[0].source, "a.out")
        self.assertEqual(part_def.connections[0].target, "b.in")

    def test_parse_complex_model(self):
        """Test parsing a more complex model."""
        source = """
        package VehicleModel {
            part def Vehicle {
                attribute mass : Real;
                part engine : Engine;
                port fuelPort : FuelPort;
            }
            
            part def Engine {
                attribute power : Real = 200.0;
            }
            
            port def FuelPort {
                out item fuel : Fuel;
            }
        }
        """
        model = parse(source)

        self.assertEqual(len(model.packages), 1)
        pkg = model.packages[0]
        self.assertEqual(pkg.name, "VehicleModel")
        self.assertEqual(len(pkg.members), 3)


class TestExtractor(unittest.TestCase):
    """Tests for the SysML v2 element extractor."""

    def test_extract_part_defs(self):
        """Test extracting part definitions."""
        source = """
        part def Engine {}
        part def Transmission {}
        part def Vehicle {
            part engine : Engine;
        }
        """
        model = extract(source)

        self.assertEqual(len(model.part_defs), 3)
        names = [p.name for p in model.part_defs]
        self.assertIn("Engine", names)
        self.assertIn("Transmission", names)
        self.assertIn("Vehicle", names)

    def test_extract_parts(self):
        """Test extracting parts."""
        source = """
        part def Vehicle {
            part engine : Engine;
            part transmission : Transmission;
        }
        """
        model = extract(source)

        self.assertEqual(len(model.parts), 2)
        names = [p.name for p in model.parts]
        self.assertIn("engine", names)
        self.assertIn("transmission", names)

    def test_extract_ports(self):
        """Test extracting ports."""
        source = """
        part def Sensor {
            out port dataOut : DataPort;
            in port commandIn : CommandPort;
        }
        """
        model = extract(source)

        self.assertEqual(len(model.ports), 2)

    def test_extract_attributes(self):
        """Test extracting attributes."""
        source = """
        part def Vehicle {
            attribute mass : Real = 1500.0;
            attribute color : String;
        }
        """
        model = extract(source)

        self.assertEqual(len(model.attributes), 2)
        mass_attr = next((a for a in model.attributes if a.name == "mass"), None)
        self.assertIsNotNone(mass_attr)
        self.assertEqual(mass_attr.type, "Real")

    def test_extract_connections(self):
        """Test extracting connections."""
        source = """
        part def System {
            connect sensor.dataOut to controller.dataIn;
            connect controller.commandOut to actuator.commandIn;
        }
        """
        model = extract(source)

        self.assertEqual(len(model.connections), 2)

    def test_extract_requirements(self):
        """Test extracting requirements."""
        source = """
        requirement def MassReq {}
        requirement def PerformanceReq {}
        """
        model = extract(source)

        self.assertEqual(len(model.requirements), 2)

    def test_extract_states(self):
        """Test extracting states."""
        source = """
        state def VehicleState {
            first state Idle;
            state Running;
            state Stopped;
        }
        """
        model = extract(source)

        self.assertGreaterEqual(len(model.states), 3)

    def test_extract_with_regex(self):
        """Test extraction using regex fallback."""
        source = """
        package Test {
            part def Engine {
                attribute power : Real;
            }
        }
        """
        model = extract(source, use_parser=False)

        self.assertEqual(len(model.packages), 1)
        self.assertEqual(len(model.part_defs), 1)

    def test_extract_part_def_names(self):
        """Test the convenience function for extracting part def names."""
        source = """
        part def A {}
        part def B {}
        part def C {}
        """
        names = extract_part_def_names(source)

        self.assertEqual(len(names), 3)
        self.assertIn("A", names)
        self.assertIn("B", names)
        self.assertIn("C", names)


class TestValidator(unittest.TestCase):
    """Tests for the SysML v2 syntax validator."""

    def test_valid_simple_package(self):
        """Test that a simple valid package passes validation."""
        source = "package Vehicle {}"
        result = validate(source)

        self.assertTrue(result.valid)
        self.assertEqual(len(result.errors), 0)

    def test_valid_nested_braces(self):
        """Test that nested braces are validated correctly."""
        source = """
        package Vehicle {
            part def Engine {
                attribute power : Real;
            }
        }
        """
        result = validate(source)

        self.assertTrue(result.valid)

    def test_invalid_missing_closing_brace(self):
        """Test that missing closing brace is detected."""
        source = "package Vehicle {"
        result = validate(source)

        self.assertFalse(result.valid)
        self.assertGreater(len(result.errors), 0)
        self.assertTrue(any("Unclosed" in e.message for e in result.errors))

    def test_invalid_extra_closing_brace(self):
        """Test that extra closing brace is detected."""
        source = "package Vehicle {}}"
        result = validate(source)

        self.assertFalse(result.valid)
        self.assertTrue(any("Unexpected" in e.message for e in result.errors))

    def test_invalid_mismatched_braces(self):
        """Test that mismatched braces are detected."""
        source = "package Vehicle { part def Engine { }"
        result = validate(source)

        self.assertFalse(result.valid)

    def test_import_without_semicolon(self):
        """Test that import without semicolon is flagged."""
        source = """
        package P {
            import Parts::*
        }
        """
        result = validate(source)

        self.assertTrue(any("semicolon" in e.message.lower() for e in result.errors))

    def test_element_counting(self):
        """Test that elements are counted correctly."""
        source = """
        package Vehicle {
            part def Engine {}
            part def Transmission {}
            part myPart : Engine;
        }
        """
        result = validate(source)

        self.assertEqual(result.elements["packages"], 1)
        self.assertEqual(result.elements["part_defs"], 2)
        self.assertEqual(result.elements["parts"], 1)

    def test_is_valid_function(self):
        """Test the is_valid convenience function."""
        valid_source = "package Vehicle {}"
        invalid_source = "package Vehicle {"

        self.assertTrue(is_valid(valid_source))
        self.assertFalse(is_valid(invalid_source))

    def test_comments_ignored(self):
        """Test that comments don't affect brace matching."""
        source = """
        package Vehicle {
            // { this is a comment with a brace
            /* { another brace in a block comment } */
            part def Engine {}
        }
        """
        result = validate(source)

        self.assertTrue(result.valid)

    def test_strings_ignored(self):
        """Test that strings don't affect brace matching."""
        source = '''
        package Vehicle {
            attribute name : String = "{ not a brace }";
        }
        '''
        result = validate(source)

        self.assertTrue(result.valid)


class TestIntegration(unittest.TestCase):
    """Integration tests for the full parser pipeline."""

    def test_vehicle_model(self):
        """Test parsing a complete vehicle model."""
        source = """
        package VehicleModel {
            requirement def VehicleMassRequirement {
                doc /* The vehicle mass shall not exceed 2000 kg. */
                attribute massActual : Real;
                attribute massLimit : Real = 2000.0;
            }
            
            part def Engine {
                attribute mass : Real = 800.0;
                attribute torque : Real = 320.0;
            }
            
            part def Vehicle {
                attribute calculatedMass : Real;
                part engine : Engine;
                
                satisfy massReq : VehicleMassRequirement by Vehicle;
            }
        }
        """
        # Validate
        result = validate(source)
        self.assertTrue(result.valid)

        # Parse
        model = parse(source)
        self.assertEqual(len(model.packages), 1)

        # Extract
        extracted = extract(source)
        self.assertGreater(len(extracted.part_defs), 0)
        self.assertGreater(len(extracted.requirements), 0)

    def test_factory_model(self):
        """Test parsing a factory model with connections."""
        source = """
        package FactoryModel {
            item def Product {}
            item def Material {}
            
            port def ProductPort {
                out item product : Product;
            }
            
            port def MaterialPort {
                in item material : Material;
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
        # Validate
        result = validate(source)
        self.assertTrue(result.valid)

        # Extract
        extracted = extract(source)
        self.assertGreater(len(extracted.connections), 0)
        self.assertGreater(len(extracted.ports), 0)

    def test_state_machine_model(self):
        """Test parsing a state machine model."""
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
        # Validate
        result = validate(source)
        self.assertTrue(result.valid)

        # Extract
        extracted = extract(source)
        self.assertGreater(len(extracted.states), 0)
        self.assertGreater(len(extracted.transitions), 0)


if __name__ == "__main__":
    unittest.main()
