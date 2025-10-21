import unittest
import os
from utoml import parse, load


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


if __name__ == "__main__":
    unittest.main()
