"""
Simple TOML parser implementation that converts TOML format to Python dictionaries.
Supports basic data types, nested sections, arrays, and inline tables
"""


def _split_array(value: str) -> list[str]:
    """Splits an array string, respecting nested brackets."""
    elements = []
    segment = []
    depth = 0

    for char in value:
        depth += 1 if char == "[" else -1 if char == "]" else 0
        if char == "," and depth == 0:
            elements.append("".join(segment).strip())
            segment = []
            continue
        segment.append(char)

    if segment:
        elements.append("".join(segment).strip())

    return elements


def parse(content: str) -> dict:
    """Parse TOML content into a Python dictionary."""
    result = {}
    current_section = result

    def _parse(value: str):
        """Parse a TOML value into its Python equivalent."""
        value = value.strip()

        if value.lower() in ("true", "false"):  # Parse Boolean
            return value.lower() == "true"

        if value[0] in ('"', "'") and value[-1] == value[0]:  # Parse String
            return value[1:-1]

        if value.startswith("[") and value.endswith("]"):  # Parse Array
            return [_parse(part) for part in _split_array(value[1:-1])]

        if value.startswith("{") and value.endswith("}"):  # Parse Dict
            return {
                _parse(k.strip()): _parse(v.strip())
                for k, v in (pair.split("=") for pair in value[1:-1].split(",") if "=" in pair)
            }

        # Parse numbes (try integer first, then float)
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                pass

        # If not any of previous type, return as is (might be a reference or date)
        return value

    for line in content.split('\n'):
        # Remove comments and whitespace
        line = line.split("#")[0].strip()
        if not line:
            continue

        # Handle section headers: [section.subsection]
        if line.startswith("[") and line.endswith("]"):
            section = result
            for key in line[1:-1].split("."):
                section = section.setdefault(key, {})
            current_section = section
            continue

        # Handle key-value pairs
        if "=" in line:
            key, value = map(str.strip, line.split("=", 1))
            current_section[_parse(key)] = _parse(value)

    return result


def load(filename: str) -> dict:
    """Load and parse a TOML file."""
    with open(filename, encoding="utf-8") as file:
        return parse(file.read())
