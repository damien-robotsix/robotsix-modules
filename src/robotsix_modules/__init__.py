"""Shared JSON-Schema-driven module-taxonomy validation for robotsix projects.

Public API:
    load_taxonomy(path)             -> dict
    validate(taxonomy, *, schema)   -> list[str]
    validate_file(path, *, schema_path) -> list[str]
    check_registration(taxonomy, repo_root, *,
        tracked_files) -> list[RegistrationFinding]
    validate_paths(taxonomy, repo_root) -> list[PathFinding]
    SCHEMA_PATH                     -> pathlib.Path
    __version__                     -> str
"""

from __future__ import annotations

from .validation import (
    SCHEMA_PATH,
    PathFinding,
    RegistrationFinding,
    check_registration,
    load_taxonomy,
    validate,
    validate_file,
    validate_paths,
)

__version__ = "0.2.0"

__all__ = [
    "PathFinding",
    "RegistrationFinding",
    "SCHEMA_PATH",
    "__version__",
    "check_registration",
    "load_taxonomy",
    "validate",
    "validate_file",
    "validate_paths",
]
