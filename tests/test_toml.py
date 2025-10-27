import unittest
import os
from unittest.mock import patch, mock_open
from utoml import parse, serialize, load, save


class TestTOMLParser(unittest.TestCase):

    def test_boolean(self):
        content = """
        bool_true = true
        bool_false = false
        """
        result = parse(content)
        self.assertEqual(result["bool_true"], True)
        self.assertEqual(result["bool_false"], False)

    def test_string(self):
        content = """
        name = "Toml Parser"
        description = "A simple TOML parser implementation"
        other = 'Single quoted string'
        """
        result = parse(content)
        self.assertEqual(result["name"], "Toml Parser")
        self.assertEqual(result["description"], "A simple TOML parser implementation")
        self.assertEqual(result["other"], "Single quoted string")

    def test_number(self):
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
        content = """
        fruits = ["apple", "banana", "cherry"]
        nested = [[1, 2], [3, 4]]
        """
        result = parse(content)
        self.assertEqual(result["fruits"], ["apple", "banana", "cherry"])
        self.assertEqual(result["nested"], [[1, 2], [3, 4]])

    def test_dictionary(self):
        content = """
        person = { name = "John", age = 30 }
        """
        result = parse(content)
        self.assertEqual(result["person"], {"name": "John", "age": 30})

    def test_section(self):
        content = """
        [person]
        name = "John"
        age = 30
        """
        result = parse(content)
        self.assertEqual(result["person"]["name"], "John")
        self.assertEqual(result["person"]["age"], 30)

    def test_nested_sections(self):
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
        content = ""
        result = parse(content)
        self.assertEqual(result, {})

    def test_comments(self):
        content = """
        # This is a comment
        name = "Toml Parser"  # Another comment
        """
        result = parse(content)
        self.assertEqual(result["name"], "Toml Parser")

    def test_invalid_data(self):
        content = """
        age = "25"  # Invalid data, should be an integer
        """
        result = parse(content)
        self.assertEqual(result["age"], "25")  # Should return the value as a string, no conversion

    def test_mixed_types(self):
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

    def test_load_file(self):
        dir = os.path.dirname(os.path.realpath(__file__))
        file = os.path.join(dir, "test.toml")
        result = load(file)
        self.assertEqual(result["title"], "TOML Example")


class TestTOMLSerializer(unittest.TestCase):

    def test_serialize_boolean(self):
        data = {"first": True, "second": False}
        result = serialize(data)
        self.assertIn("first = true", result)
        self.assertIn("second = false", result)

    def test_serialize_string(self):
        data = {"name": "Toml Parser", "description": "A simple TOML parser implementation"}
        result = serialize(data)
        self.assertIn('name = "Toml Parser"', result)
        self.assertIn('description = "A simple TOML parser implementation"', result)

    def test_serialize_number(self):
        data = {"age": 25, "temp": -17, "pi": 3.1415}
        result = serialize(data)
        self.assertIn("age = 25", result)
        self.assertIn("temp = -17", result)
        self.assertIn("pi = 3.1415", result)

    def test_serialize_array(self):
        data = {"fruits": ["apple", "banana", "cherry"], "nested": [[1, 2], [3, 4]]}
        result = serialize(data)
        self.assertIn('fruits = ["apple", "banana", "cherry"]', result)
        self.assertIn('nested = [[1, 2], [3, 4]]', result)

    def test_serialize_dictionary(self):
        data = {"person": {"name": "John", "age": 30}}
        result = serialize(data)
        self.assertIn('[person]', result)
        self.assertIn('name = "John"', result)
        self.assertIn('age = 30', result)

    def test_serialize_nested_sections(self):
        data = {
            "person": {
                "name": "John",
                "address": {
                    "street": "123 Main St",
                    "city": "Anytown"
                }
            }
        }
        result = serialize(data)
        self.assertIn('[person]', result)
        self.assertIn('name = "John"', result)
        self.assertIn('[person.address]', result)
        self.assertIn('street = "123 Main St"', result)
        self.assertIn('city = "Anytown"', result)

    def test_serialize_mixed_types(self):
        data = {
            "name": "Alice",
            "age": 28,
            "is_active": True,
            "height": 5.7,
            "hobbies": ["reading", "swimming"]
        }
        result = serialize(data)
        self.assertIn('name = "Alice"', result)
        self.assertIn('age = 28', result)
        self.assertIn('is_active = true', result)
        self.assertIn('height = 5.7', result)
        self.assertIn('hobbies = ["reading", "swimming"]', result)

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
                "urls": {
                    "api": "https://api.example.com",
                    "web": "https://web.example.com"
                }
            }
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
            "database": {
                "host": "localhost",
                "user": "admin"
            }
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
        self.assertIn('debug = true', content)
        self.assertIn('port = 8080', content)
        self.assertIn('[database]', content)
        self.assertIn('host = "localhost"', content)
        self.assertIn('user = "admin"', content)


if __name__ == "__main__":
    unittest.main()
