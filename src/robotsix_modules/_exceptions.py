"""Custom exception hierarchy for robotsix-modules."""

from __future__ import annotations


class RobotsixModulesError(Exception):
    """Base exception for all robotsix-modules errors."""


class GitOperationError(RobotsixModulesError):
    """Raised when a git subprocess operation fails.

    Attributes:
        message: Human-readable error description.
        command: The git subcommand that failed (e.g. "ls-files").
        returncode: The subprocess return code, if available, or None.
    """

    def __init__(
        self,
        message: str,
        command: str = "ls-files",
        returncode: int | None = None,
    ) -> None:
        self.command = command
        self.returncode = returncode
        super().__init__(message)


class ConfigError(RobotsixModulesError):
    """Base for errors related to reading or parsing configuration files."""


class ConfigFileNotFoundError(ConfigError):
    """A required configuration file was not found on disk."""


class ConfigParseError(ConfigError):
    """A configuration file is not valid YAML."""


class ConfigStructureError(ConfigError):
    """The top-level structure of a configuration file is not a mapping."""


__all__ = [
    "RobotsixModulesError",
    "GitOperationError",
    "ConfigError",
    "ConfigFileNotFoundError",
    "ConfigParseError",
    "ConfigStructureError",
]
