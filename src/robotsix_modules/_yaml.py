"""Thin YAML I/O wrapper replacing ``robotsix_yaml_config``.

All YAML I/O in this package must go through the functions and
exception classes defined here — agents must **not** add a second
YAML parser.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from ._exceptions import ConfigError, ConfigParseError, ConfigStructureError


class YamlConfigError(ConfigError):
    """Base for all YAML I/O errors raised by this package."""


class YamlReadError(YamlConfigError):
    """Raised when a file cannot be found or read."""


def read_yaml_file(path: Path) -> dict[str, Any]:
    """Read *path* and return its content as a parsed mapping.

    Raises:
        YamlReadError: file missing or unreadable.
        ConfigParseError: invalid YAML.
        ConfigStructureError: root is not a mapping.
    """
    try:
        raw = path.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError) as exc:
        raise YamlReadError(str(exc)) from exc

    try:
        result = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise ConfigParseError(str(exc)) from exc

    if not isinstance(result, dict):
        raise ConfigStructureError(
            f"expected a YAML mapping at the document root, got {type(result).__name__}"
        )
    return result
