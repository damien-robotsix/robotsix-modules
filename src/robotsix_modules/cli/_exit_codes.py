"""Named exit codes for robotsix-modules CLI."""

from __future__ import annotations

from enum import IntEnum


class ExitCode(IntEnum):
    """Exit codes returned by the robotsix-modules CLI."""

    OK = 0       # All checks passed
    ERRORS = 1   # Validation/path/registration errors found
    FATAL = 2    # Taxonomy or schema file could not be loaded
