"""Access to the bundled module-taxonomy JSON Schema."""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path
from typing import Any

from robotsix_yaml_config import read_yaml_file

#: Filesystem path to the bundled JSON Schema resource.
SCHEMA_PATH: Path = Path(
    str(files("robotsix_modules.validation.schemas").joinpath("modules.schema.yaml"))
)


def load_schema() -> dict[str, Any]:
    """Parse and return the bundled JSON Schema as a dict."""
    return read_yaml_file(SCHEMA_PATH)
