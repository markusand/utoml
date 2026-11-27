"""Tests for utoml TOML parser and serializer."""

import unittest
import os
from unittest.mock import patch, mock_open
from utoml import parse, serialize, load, save


class TestTOMLParser(unittest.TestCase):
    """Test TOML parsing into Python dictionaries."""

    def test_boolean(self):
        """Parse true and false literals into Python booleans."""
        content = """
        bool_true = true
        bool_false = false
        """
        result = parse(content)
        self.assertEqual(result["bool_true"], True)
        self.assertEqual(result["bool_false"], False)

    def test_string(self):
        """Parse double-quoted and single-quoted strings."""
        content = """
        name = "Toml Parser"
        description = "A simple TOML parser implementation"
        other = 'Single quoted string'
        """
        result = parse(content)
        self.assertEqual(result["name"], "Toml Parser")
        self.assertEqual(result["description"], "A simple TOML parser implementation")
        self.assertEqual(result["other"], "Single quoted string")

    def test_string_special_chars(self):
        """Keep `#`, `,` and `=` inside strings, also in arrays and inline tables (issue #1)."""
        self.assertEqual(parse('a = "x # not a comment"'), {"a": "x # not a comment"})
        self.assertEqual(parse('a = "http://e.com/#frag" # comment'), {"a": "http://e.com/#frag"})
        self.assertEqual(parse('a = ["x,y", "z"]'), {"a": ["x,y", "z"]})
        self.assertEqual(parse('a = {k = "x,y", j = 1}'), {"a": {"k": "x,y", "j": 1}})
        self.assertEqual(parse('a = {k = "x=y"}'), {"a": {"k": "x=y"}})
        self.assertEqual(parse("a = {k = [1, 2], j = 'b,c'}"), {"a": {"k": [1, 2], "j": "b,c"}})

    def test_number(self):
        """Parse integers, negative numbers, floats, and scientific notation."""
        content = """
        age = 25
        temp = -17
        pi = 3.1415
        scientific = 0.34e-5
        """
        result = parse(content)
        self.assertEqual(result["age"], 25)
        self.assertEqual(result["temp"], -17)
        self.assertEqual(result["pi"], 3.1415)
        self.assertEqual(result["scientific"], 0.0000034)

    def test_array(self):
        """Parse flat and nested arrays."""
        content = """
        fruits = ["apple", "banana", "cherry"]
        nested = [[1, 2], [3, 4]]
        """
        result = parse(content)
        self.assertEqual(result["fruits"], ["apple", "banana", "cherry"])
        self.assertEqual(result["nested"], [[1, 2], [3, 4]])

    def test_dictionary(self):
        """Parse inline table syntax into a dictionary."""
        content = """
        person = { name = "John", age = 30 }
        """
        result = parse(content)
        self.assertEqual(result["person"], {"name": "John", "age": 30})

    def test_section(self):
        """Parse [section] headers into nested dictionary keys."""
        content = """
        [person]
        name = "John"
        age = 30
        """
        result = parse(content)
        self.assertEqual(result["person"]["name"], "John")
        self.assertEqual(result["person"]["age"], 30)

    def test_nested_sections(self):
        """Parse dotted [section.subsection] headers into nested dictionaries."""
        content = """
        [person]
        name = "John"

        [person.address]
        street = "123 Main St"
        city = "Anytown"
        """
        result = parse(content)
        self.assertEqual(result["person"]["name"], "John")
        self.assertEqual(result["person"]["address"]["street"], "123 Main St")
        self.assertEqual(result["person"]["address"]["city"], "Anytown")

    def test_empty_content(self):
        """Parse empty input into an empty dictionary."""
        content = ""
        result = parse(content)
        self.assertEqual(result, {})

    def test_comments(self):
        """Strip full-line and inline comments during parsing."""
        content = """
        # This is a comment
        name = "Toml Parser"  # Another comment
        """
        result = parse(content)
        self.assertEqual(result["name"], "Toml Parser")

    def test_invalid_data(self):
        """Quoted numeric values are preserved as strings, not coerced."""
        content = """
        age = "25"  # Invalid data, should be an integer
        """
        result = parse(content)
        self.assertEqual(result["age"], "25")  # Should return the value as a string, no conversion

    def test_mixed_types(self):
        """Parse a document with strings, integers, booleans, and floats together."""
        content = """
        name = "Alice"
        age = 28
        is_active = true
        height = 5.7
        """
        result = parse(content)
        self.assertEqual(result["name"], "Alice")
        self.assertEqual(result["age"], 28)
        self.assertEqual(result["is_active"], True)
        self.assertEqual(result["height"], 5.7)

    def test_array_of_tables(self):
        """Parse [[key]] entries into a list of dictionaries."""
        content = """
        [[products]]
        name = "Hammer"
        sku = 738594937

        [[products]]
        name = "Nail"
        sku = 284758393
        color = "gray"
        """
        result = parse(content)
        self.assertEqual(
            result,
            {
                "products": [
                    {"name": "Hammer", "sku": 738594937},
                    {"name": "Nail", "sku": 284758393, "color": "gray"},
                ]
            },
        )

    def test_array_of_tables_nested(self):
        """Parse [[parent.key]] entries into a list nested under a section."""
        content = """
        [fruit]
        name = "apple"

        [[fruit.varieties]]
        name = "red delicious"

        [[fruit.varieties]]
        name = "granny smith"
        """
        result = parse(content)
        self.assertEqual(
            result,
            {
                "fruit": {
                    "name": "apple",
                    "varieties": [
                        {"name": "red delicious"},
                        {"name": "granny smith"},
                    ],
                }
            },
        )

    def test_array_of_tables_mixed_value_types(self):
        """Parse [[key]] entries containing strings, integers, and booleans."""
        content = """
        [[sensors]]
        type = "gps"
        baudrate = 9500
        port = 9
        rtk = true
        """
        result = parse(content)
        self.assertEqual(
            result,
            {
                "sensors": [
                    {"type": "gps", "baudrate": 9500, "port": 9, "rtk": True},
                ]
            },
        )

    def test_load_file(self):
        """Load and parse a TOML file from disk."""
        dir = os.path.dirname(os.path.realpath(__file__))
        file = os.path.join(dir, "test.toml")
        result = load(file)
        self.assertEqual(result["title"], "TOML Example")
        self.assertEqual(
            result["products"],
            [
                {"name": "Hammer", "sku": 738594937},
                {"name": "Nail", "sku": 284758393, "color": "gray"},
            ],
        )


class TestTOMLSerializer(unittest.TestCase):
    """Test Python dictionary serialization to TOML format."""

    def test_serialize_boolean(self):
        """Serialize Python booleans into TOML true/false literals."""
        data = {"first": True, "second": False}
        result = serialize(data)
        self.assertIn("first = true", result)
        self.assertIn("second = false", result)

    def test_serialize_string(self):
        """Serialize Python strings into double-quoted TOML strings."""
        data = {"name": "Toml Parser", "description": "A simple TOML parser implementation"}
        result = serialize(data)
        self.assertIn('name = "Toml Parser"', result)
        self.assertIn('description = "A simple TOML parser implementation"', result)

    def test_serialize_number(self):
        """Serialize integers and floats into TOML numeric values."""
        data = {"age": 25, "temp": -17, "pi": 3.1415}
        result = serialize(data)
        self.assertIn("age = 25", result)
        self.assertIn("temp = -17", result)
        self.assertIn("pi = 3.1415", result)

    def test_serialize_array(self):
        """Serialize flat and nested lists into TOML arrays."""
        data = {"fruits": ["apple", "banana", "cherry"], "nested": [[1, 2], [3, 4]]}
        result = serialize(data)
        self.assertIn('fruits = ["apple", "banana", "cherry"]', result)
        self.assertIn("nested = [[1, 2], [3, 4]]", result)

    def test_serialize_dictionary(self):
        """Serialize a nested dictionary into a [section] with key-value pairs."""
        data = {"person": {"name": "John", "age": 30}}
        result = serialize(data)
        self.assertIn("[person]", result)
        self.assertIn('name = "John"', result)
        self.assertIn("age = 30", result)

    def test_serialize_nested_sections(self):
        """Serialize deeply nested dicts into dotted [section.subsection] headers."""
        data = {"person": {"name": "John", "address": {"street": "123 Main St", "city": "Anytown"}}}
        result = serialize(data)
        self.assertIn("[person]", result)
        self.assertIn('name = "John"', result)
        self.assertIn("[person.address]", result)
        self.assertIn('street = "123 Main St"', result)
        self.assertIn('city = "Anytown"', result)

    def test_serialize_mixed_types(self):
        """Serialize a document with strings, integers, booleans, floats, and arrays."""
        data = {
            "name": "Alice",
            "age": 28,
            "is_active": True,
            "height": 5.7,
            "hobbies": ["reading", "swimming"],
        }
        result = serialize(data)
        self.assertIn('name = "Alice"', result)
        self.assertIn("age = 28", result)
        self.assertIn("is_active = true", result)
        self.assertIn("height = 5.7", result)
        self.assertIn('hobbies = ["reading", "swimming"]', result)

    def test_serialize_array_of_tables(self):
        """Serialize a list of dictionaries into [[key]] sections."""
        data = {
            "products": [
                {"name": "Hammer", "sku": 738594937},
                {"name": "Nail", "sku": 284758393, "color": "gray"},
            ]
        }
        result = serialize(data)
        self.assertIn("[[products]]", result)
        self.assertIn('name = "Hammer"', result)
        self.assertIn("sku = 738594937", result)
        self.assertIn('name = "Nail"', result)
        self.assertIn('color = "gray"', result)
        self.assertNotIn("[products]", result.replace("[[products]]", ""))

    def test_round_trip_consistency(self):
        """Test that serialize(parse(toml)) produces equivalent structure"""
        data = {
            "name": "Test",
            "value": 42,
            "active": True,
            "items": ["a", "b", "c"],
            "config": {
                "debug": False,
                "timeout": 30,
                "urls": {"api": "https://api.example.com", "web": "https://web.example.com"},
            },
        }
        serialized = serialize(data)
        parsed = parse(serialized)
        self.assertEqual(data, parsed)

    @patch("builtins.open", new_callable=mock_open)
    def test_save_file(self, _open):
        """Test that save function writes serialized data to file"""
        data = {
            "name": "Test Config",
            "debug": True,
            "port": 8080,
            "database": {"host": "localhost", "user": "admin"},
            "sensors": [
                {"type": "gps", "baudrate": 9500},
                {"type": "uart", "port": 2},
            ],
        }
        filename = "test.toml"

        # Call the save function
        save(filename, data)

        # Verify that open was called with correct parameters
        _open.assert_called_once_with(filename, "w", encoding="utf-8")

        # Get the written content
        content = _open().write.call_args[0][0]

        # Verify that the content contains expected TOML structure
        self.assertIn('name = "Test Config"', content)
        self.assertIn("debug = true", content)
        self.assertIn("port = 8080", content)
        self.assertIn("[database]", content)
        self.assertIn('host = "localhost"', content)
        self.assertIn('user = "admin"', content)
        self.assertIn("[[sensors]]", content)
        self.assertIn('type = "gps"', content)
        self.assertIn("baudrate = 9500", content)
        self.assertIn('type = "uart"', content)
        self.assertIn("port = 2", content)


if __name__ == "__main__":
    unittest.main()
