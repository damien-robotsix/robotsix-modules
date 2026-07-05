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
    ConfigError                     — base class for configuration errors
    ConfigFileNotFoundError         — raised when a config file is missing
    ConfigParseError                — raised when a config file is invalid YAML
    ConfigStructureError            — raised when a config file structure is wrong
    GitOperationError               — raised when a Git operation fails
    RobotsixModulesError            — base for all errors from this package
    read_yaml_file(path)            -> dict
"""

from __future__ import annotations

from ._exceptions import (
    ConfigError,
    ConfigFileNotFoundError,
    ConfigParseError,
    ConfigStructureError,
    GitOperationError,
    RobotsixModulesError,
)
from ._yaml import read_yaml_file
from .validation import (
    SCHEMA_PATH,
    FindingKind,
    PathFinding,
    RegistrationFinding,
    check_coverage,
    check_registration,
    load_schema,
    load_taxonomy,
    validate,
    validate_file,
    validate_paths,
)

try:
    from importlib.metadata import version as _metadata_version

    __version__ = _metadata_version("robotsix-modules")
except Exception:
    __version__ = "0.0.0.dev0"  # fallback for uninstalled / dev context

__all__ = [
    "ConfigError",
    "ConfigFileNotFoundError",
    "ConfigParseError",
    "ConfigStructureError",
    "FindingKind",
    "GitOperationError",
    "PathFinding",
    "RegistrationFinding",
    "RobotsixModulesError",
    "SCHEMA_PATH",
    "__version__",
    "check_coverage",
    "check_registration",
    "load_schema",
    "load_taxonomy",
    "read_yaml_file",
    "validate",
    "validate_file",
    "validate_paths",
]
