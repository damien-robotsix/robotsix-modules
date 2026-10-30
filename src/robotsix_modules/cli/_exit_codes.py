"""Named exit codes for robotsix-modules CLI."""

from __future__ import annotations

from enum import IntEnum


class ExitCode(IntEnum):
    """Exit codes returned by the robotsix-modules CLI."""

    OK = 0  # All checks passed
    ERRORS = 1  # Validation/path/registration errors found
    # Taxonomy/schema file could not be loaded, or a git operation failed
    # (e.g. non-git --root)
    FATAL = 2
