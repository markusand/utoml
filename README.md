# Micropython TOML

A simple TOML parser and serializer for micropython that converts TOML format to dictionaries.

## Features

- **Basic Data Types**: Supports Boolean values, integers, floats, and strings.
- **Nested Sections**: Handles sections in the TOML format, including nested subsections.
- **Arrays**: Parses arrays while respecting nested brackets.
- **Inline Tables**: Parses inline tables and converts them to Python dictionaries.

## Installation

There are no external dependencies required. You can include the `utoml.py` file directly in the root of your project. Compile it to .mpy to save some resources.

If you are creating a custom micropython firmware, you can freeze it to load it from ROM and save even more resources. Add it to the `extmod` directory and load it from the `manifest.py`

```python
module('utoml.py', base_path="$(MPY_DIR)/extmod", opt=2)
```

## Usage

You can parse a TOML string into a Python dictionary by calling the `parse()` function.

```python
from utoml import parse

toml = """
# Example TOML data
[owner]
name = "John Doe"
age = 30

[database]
enabled = true
ports = [8000, 8001, 8002]
settings = { timeout = 30, keep_alive = true }
"""

config = parse(toml)
print(config)
```

or you can directly load a file with the `load()` function

```python
from utoml import load

config = load('config.toml')
```

You can serialize Python dictionaries back to TOML format using the `serialize()` function or save directly to a file with `save()`:

```python
from utoml import serialize, save

config = {
    "title": "My Application",
    "debug": True,
    "database": {
        "host": "localhost",
        "port": 5432,
        "credentials": {"user": "admin", "password": "secret"}
    },
    "servers": ["web1", "web2", "db1"]
}

# Serialize to TOML string
toml = serialize(config)
print(toml)

# Save directly to file
save('output.toml', config)
```

## Tests

A battery of tests is included to verify the proper working of the parser.
Run tests by executing the command:

```bash
python -m unittest discover tests
```
