"""Finding definitions and finding-production logic for ``check_registration``.

These helpers are extracted from ``registration.py`` to keep that module
focused on the public API and the path-resolution infra shared with
``validate_paths``.
"""

from __future__ import annotations

import logging
import subprocess  # nosec B404
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

from .._exceptions import GitOperationError

logger = logging.getLogger("robotsix_modules")

# ---------------------------------------------------------------------------
# Finding types
# ---------------------------------------------------------------------------


class FindingKind(StrEnum):
    """Canonical kinds for registration and path-validation findings."""

    UNCLASSIFIED_FILE = "unclassified_file"
    STALE_PATH = "stale_path"
    DUPLICATE_REGISTRATION = "duplicate_registration"
    PATH_NOT_FOUND = "path_not_found"
    GLOB_EMPTY = "glob_empty"


@dataclass(frozen=True)
class RegistrationFinding:
    """A single finding from :func:`check_registration`.

    Attributes:
        kind: the category of finding.
        message: human-readable one-liner suitable for CLI output.
        file: repo-relative path (set for ``unclassified_file`` and
            ``duplicate_registration``).
        module_id: module id (set for ``stale_path`` and
            ``duplicate_registration``).
        other_module_id: second claimant (set for ``duplicate_registration``
            only).
    """

    kind: FindingKind
    message: str
    file: str | None = None
    module_id: str | None = None
    other_module_id: str | None = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _expand_module_paths(
    module_id: str,
    path_entries: list[str],
    repo_root: Path,
) -> tuple[set[str], set[str]]:
    """Expand every path entry for a single module.

    Returns:
        (*claimed_files*, *stale_entries*).

    ``claimed_files`` is the set of repo-relative paths that exist on disk
    and match at least one of the module's path patterns.  ``stale_entries``
    is the subset of *path_entries* whose glob expansion matched zero files
    on disk.
    """
    # Lazy import to avoid circular dependency with registration._glob_paths.
    from .registration import _glob_paths

    claimed: set[str] = set()
    stale: set[str] = set()

    logger.debug(
        "expanding %d path entries for module %s", len(path_entries), module_id
    )

    for pattern in path_entries:
        matches = [
            str(p.relative_to(repo_root))
            for p in _glob_paths(repo_root, pattern)
            if p.is_file()
        ]
        if matches:
            claimed.update(matches)
        else:
            stale.add(pattern)

    return claimed, stale


def _build_file_claimants(
    taxonomy: dict[str, Any],
    repo_root: Path,
) -> dict[str, list[str]]:
    """Build a mapping of repo-relative file path → list of claiming module ids.

    Only paths expanded via ``Path.glob`` that correspond to actual on-disk
    files are included.
    """
    # lazy import to avoid circular dependency
    from .registration import compute_default_globs

    package: str | None = taxonomy.get("package")
    file_to_modules: dict[str, list[str]] = {}
    for module_entry in taxonomy.get("modules", []):
        module_id: str = module_entry["id"]
        explicit_paths: list[str] = module_entry.get("paths") or []
        effective_paths: list[str] = list(explicit_paths)
        if package:
            effective_paths.extend(compute_default_globs(module_id, package))
        claimed, _ = _expand_module_paths(module_id, effective_paths, repo_root)
        for path in claimed:
            file_to_modules.setdefault(path, []).append(module_id)
    return file_to_modules


def _resolve_tracked_files(
    repo_root: Path,
    tracked_files: list[str] | None,
) -> list[str]:
    """Resolve the list of tracked files for *repo_root*.

    When *tracked_files* is not ``None`` it is returned unchanged.
    Otherwise ``git ls-files`` is run in *repo_root*.

    Returns:
        A list of repo-relative file paths.

    Raises:
        GitOperationError: when *tracked_files* is ``None`` and ``git ls-files``
            cannot be run successfully.
    """
    if tracked_files is not None:
        return tracked_files

    logger.debug("running git ls-files in %s", repo_root)
    try:
        result = subprocess.run(  # nosec B603, B607
            ["git", "ls-files"],  # noqa: S607
            capture_output=True,
            text=True,
            cwd=repo_root,
            timeout=60,
            check=False,
        )
    except FileNotFoundError as exc:
        raise GitOperationError(
            "git is not installed or not on PATH; cannot list tracked files",
            returncode=None,
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise GitOperationError(
            f"git ls-files timed out after 60s in {repo_root}",
            returncode=None,
        ) from exc
    if result.returncode != 0:
        raise GitOperationError(
            f"git ls-files failed in {repo_root}: {result.stderr.strip()}",
            returncode=result.returncode,
        )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _find_unclassified(
    tracked_set: set[str],
    file_to_modules: dict[str, list[str]],
) -> list[RegistrationFinding]:
    """Return findings for tracked files not claimed by any module."""
    findings: list[RegistrationFinding] = []
    unclassified = sorted(tracked_set - set(file_to_modules))
    for path in unclassified:
        findings.append(
            RegistrationFinding(
                kind=FindingKind.UNCLASSIFIED_FILE,
                message=f"File '{path}' is not claimed by any module",
                file=path,
            )
        )
    return findings


def _find_stale_paths(
    taxonomy: dict[str, Any],
    repo_root: Path,
) -> list[RegistrationFinding]:
    """Return findings for module path entries that match zero files on disk."""
    findings: list[RegistrationFinding] = []
    for module_entry in taxonomy.get("modules", []):
        module_id: str = module_entry["id"]
        _, stale_entries = _expand_module_paths(
            module_id, module_entry.get("paths", []), repo_root
        )
        for pattern in sorted(stale_entries):
            findings.append(
                RegistrationFinding(
                    kind=FindingKind.STALE_PATH,
                    message=(
                        f"Module '{module_id}' path '{pattern}' matches "
                        "no files on disk"
                    ),
                    module_id=module_id,
                )
            )
    return findings


def _find_duplicates(
    file_to_modules: dict[str, list[str]],
    tracked_set: set[str],
) -> list[RegistrationFinding]:
    """Return findings for files claimed by more than one module."""
    findings: list[RegistrationFinding] = []
    duplicates = {
        path: ids
        for path, ids in file_to_modules.items()
        if len(ids) >= 2 and path in tracked_set
    }
    for path in sorted(duplicates):
        ids = duplicates[path]
        findings.append(
            RegistrationFinding(
                kind=FindingKind.DUPLICATE_REGISTRATION,
                message=(
                    f"File '{path}' is claimed by multiple modules: " + ", ".join(ids)
                ),
                file=path,
                module_id=ids[0],
                other_module_id=ids[1],
            )
        )
    return findings
