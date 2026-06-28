"""Shared JSON-Schema-driven module-taxonomy validation for robotsix projects.

Public API:
    load_taxonomy(path)             -> dict
    validate(taxonomy, *, schema)   -> list[str]
    validate_file(path, *, schema_path) -> list[str]
    check_registration(taxonomy, repo_root, *,
        tracked_files) -> list[RegistrationFinding]
    validate_paths(taxonomy, repo_root) -> list[PathFinding]
    SCHEMA_PATH                     -> pathlib.Path
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from robotsix_yaml_config import YamlReadError, read_yaml_file

from .registration import (
    PathFinding,
    RegistrationFinding,
    check_registration,
    validate_paths,
)
from .schema import SCHEMA_PATH, load_schema

__all__ = [
    "PathFinding",
    "RegistrationFinding",
    "SCHEMA_PATH",
    "check_registration",
    "load_schema",
    "load_taxonomy",
    "validate",
    "validate_file",
    "validate_paths",
]


def load_taxonomy(path: str | Path) -> dict[str, Any]:
    """Load a ``modules.yaml`` file and return it as a dict.

    Raises:
        YamlReadError: when ``path`` does not exist or cannot be read.
        YamlParseError: when the file is not valid YAML.
        InvalidConfigStructureError: when the parsed content is not a mapping.
    """
    target = Path(path)
    if not target.exists():
        raise YamlReadError(f"file not found: {path}")
    return read_yaml_file(target)


def _format_error(error: Any) -> str:
    """Render a jsonschema ValidationError as a debuggable one-liner.

    Includes the JSON pointer to the offending node and the violating
    value, e.g. ``modules[2].id: 'BadId' does not match '^[a-z]...'``.
    """
    parts: list[str] = []
    for token in error.absolute_path:
        if isinstance(token, int):
            parts.append(f"[{token}]")
        elif parts:
            parts.append(f".{token}")
        else:
            parts.append(str(token))
    pointer = "".join(parts) or "<root>"
    return f"{pointer}: {error.message}"


def validate(
    taxonomy: dict[str, Any], *, schema: dict[str, Any] | None = None
) -> list[str]:
    """Validate a taxonomy dict against a JSON Schema.

    Args:
        taxonomy: parsed YAML/JSON object to validate.
        schema: optional override for the bundled schema.

    Returns:
        List of human-readable error messages. Empty list = valid.
    """
    active_schema = schema if schema is not None else load_schema()
    validator = Draft202012Validator(active_schema)
    errors = sorted(
        validator.iter_errors(taxonomy), key=lambda e: list(e.absolute_path)
    )
    return [_format_error(error) for error in errors]


def validate_file(
    path: str | Path, *, schema_path: str | Path | None = None
) -> list[str]:
    """Convenience: ``load_taxonomy`` then ``validate``.

    Same return contract as :func:`validate`.
    """
    taxonomy = load_taxonomy(path)
    schema: dict[str, Any] | None = None
    if schema_path is not None:
        schema = read_yaml_file(Path(schema_path))
    return validate(taxonomy, schema=schema)
