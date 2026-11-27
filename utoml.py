"""
Simple TOML parser implementation that converts TOML format to Python dictionaries.
Supports basic data types, nested sections, arrays, and inline tables
"""


def _split(value: str, sep: str) -> list[str]:
    """Split on sep, ignoring separators inside strings and nested brackets."""
    # ponytail: no escaped quotes (\") inside strings
    parts, start, depth, quote = [], 0, 0, None

    for i, char in enumerate(value):
        if quote:
            quote = None if char == quote else quote
        elif char in "\"'":
            quote = char
        elif char in "[{":
            depth += 1
        elif char in "]}":
            depth -= 1
        elif char == sep and depth == 0:
            parts.append(value[start:i].strip())
            start = i + 1

    parts.append(value[start:].strip())
    return parts


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
            return [_parse(part) for part in _split(value[1:-1], ",") if part]

        if value.startswith("{") and value.endswith("}"):  # Parse Dict
            return {
                _parse(k.strip()): _parse(v.strip())
                for k, v in (pair.split("=", 1) for pair in _split(value[1:-1], ",") if "=" in pair)
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

    for line in content.split("\n"):
        # Remove comments and whitespace
        line = _split(line, "#")[0]
        if not line:
            continue

        # Handle array of tables: [[section]]
        if line.startswith("[[") and line.endswith("]]"):
            keys = line[2:-2].split(".")
            section = result
            for key in keys[:-1]:
                section = section.setdefault(key, {})
            table = {}
            section.setdefault(keys[-1], []).append(table)
            current_section = table
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


def serialize(data: dict) -> str:
    """Serialize a Python dictionary to TOML format."""

    def _serialize(value):
        """Serialize a Python value to its TOML string representation."""
        if isinstance(value, bool):
            return "true" if value else "false"

        if isinstance(value, str):
            return f'"{value}"'

        if isinstance(value, (int, float)):
            return str(value)

        if isinstance(value, list):
            items = [_serialize(item) for item in value]
            return f"[{', '.join(items)}]"

        if isinstance(value, dict):
            pairs = [f"{_serialize(k)} = {_serialize(v)}" for k, v in value.items()]
            return f"{{{', '.join(pairs)}}}"

        return str(value)

    def _is_array_of_tables(value):
        """Check if a value is a list of dictionaries (array of tables)."""
        return isinstance(value, list) and value and all(isinstance(v, dict) for v in value)

    def _serialize_section(section_data, section_path=""):
        """Serialize a section of the dictionary."""
        lines = []

        # First, add simple key-value pairs
        for key, value in section_data.items():
            if not isinstance(value, dict) and not _is_array_of_tables(value):
                lines.append(f"{key} = {_serialize(value)}")

        # Then, add subsections
        for key, value in section_data.items():
            subsection_path = f"{section_path}.{key}" if section_path else key
            if isinstance(value, dict):
                lines.append(f"\n[{subsection_path}]")
                lines.extend(_serialize_section(value, subsection_path))
            elif _is_array_of_tables(value):
                for table in value:
                    lines.append(f"\n[[{subsection_path}]]")
                    lines.extend(_serialize_section(table, subsection_path))

        return lines

    return "\n".join(_serialize_section(data))


def load(filename: str) -> dict:
    """Load and parse a TOML file."""
    with open(filename, encoding="utf-8") as file:
        return parse(file.read())


def save(filename: str, data: dict) -> None:
    """Save a TOML file."""
    with open(filename, "w", encoding="utf-8") as file:
        file.write(serialize(data))
