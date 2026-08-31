"""
Minimal, dependency-free JSON Schema validator.

Supports exactly the subset of draft 2020-12 this repo's schemas under
/data/schema/ actually use: type, const, enum, required, properties,
additionalProperties, items, pattern, minLength, minimum, maximum.
No network dependency, no pip install step in CI, nothing to pin.

Not a general-purpose validator. If a schema needs a keyword this file
does not implement, extend this file rather than reaching for a
third-party library first -- the data this validates is small and the
schemas are hand-written, so the coverage needed is narrow.
"""
import re


class SchemaError(Exception):
    def __init__(self, path, message):
        self.path = path
        self.message = message
        super().__init__(f"{path}: {message}")


def _type_ok(value, expected):
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    raise SchemaError("<schema>", f"unsupported type keyword {expected!r}")


def validate(instance, schema, path="$"):
    """Raises SchemaError on the first violation found. Returns None on success."""
    if "const" in schema:
        if instance != schema["const"]:
            raise SchemaError(path, f"expected const {schema['const']!r}, got {instance!r}")

    if "enum" in schema:
        if instance not in schema["enum"]:
            raise SchemaError(path, f"expected one of {schema['enum']!r}, got {instance!r}")

    if "type" in schema:
        if not _type_ok(instance, schema["type"]):
            raise SchemaError(path, f"expected type {schema['type']!r}, got {type(instance).__name__}")

    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            raise SchemaError(path, f"string shorter than minLength {schema['minLength']}")
        if "pattern" in schema and not re.match(schema["pattern"], instance):
            raise SchemaError(path, f"does not match pattern {schema['pattern']!r}: {instance!r}")

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            raise SchemaError(path, f"below minimum {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            raise SchemaError(path, f"above maximum {schema['maximum']}")

    if isinstance(instance, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in instance:
                raise SchemaError(path, f"missing required property {key!r}")

        properties = schema.get("properties", {})
        for key, value in instance.items():
            if key in properties:
                validate(value, properties[key], f"{path}.{key}")
            elif schema.get("additionalProperties") is False:
                raise SchemaError(path, f"unexpected property {key!r} (additionalProperties: false)")

    if isinstance(instance, list) and "items" in schema:
        for i, item in enumerate(instance):
            validate(item, schema["items"], f"{path}[{i}]")
