"""Registration-completeness and path-resolution checks for module taxonomies.

These functions go beyond JSON Schema structural validation: they verify
that every tracked file in a repo is claimed by exactly one module, that
every module path resolves to at least one on-disk file, and that no two
modules accidentally claim the same file.
"""

from __future__ import annotations

import subprocess  # nosec B404
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

# ---------------------------------------------------------------------------
# Finding types
# ---------------------------------------------------------------------------


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

    kind: Literal["unclassified_file", "stale_path", "duplicate_registration"]
    message: str
    file: str | None = None
    module_id: str | None = None
    other_module_id: str | None = None


@dataclass(frozen=True)
class PathFinding:
    """A single finding from :func:`validate_paths`.

    Attributes:
        kind: ``path_not_found`` for a literal path that does not exist, or
            ``glob_empty`` for a glob pattern that matches zero files.
        message: human-readable one-liner suitable for CLI output.
        module_id: the module that declares the path.
        path: the literal path or glob pattern from ``modules.yaml`` that
            failed validation.
    """

    kind: Literal["path_not_found", "glob_empty"]
    message: str
    module_id: str
    path: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _has_glob_metacharacters(pattern: str) -> bool:
    """Return True when *pattern* contains ``*``, ``?``, or ``[``."""
    return any(c in pattern for c in "*?[")


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
    claimed: set[str] = set()
    stale: set[str] = set()

    for pattern in path_entries:
        matches = [
            str(p.relative_to(repo_root))
            for p in repo_root.glob(pattern)
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
    file_to_modules: dict[str, list[str]] = {}
    for module_entry in taxonomy.get("modules", []):
        module_id: str = module_entry["id"]
        claimed, _ = _expand_module_paths(
            module_id, module_entry.get("paths", []), repo_root
        )
        for path in claimed:
            file_to_modules.setdefault(path, []).append(module_id)
    return file_to_modules


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def check_registration(
    taxonomy: dict[str, Any],
    repo_root: Path,
    *,
    tracked_files: list[str] | None = None,
) -> list[RegistrationFinding]:
    """Check that every tracked file is claimed by exactly one module.

    Args:
        taxonomy: a parsed ``modules.yaml`` dict.
        repo_root: the repository root directory.
        tracked_files: optional override — a list of repo-relative file
            paths.  When ``None`` (the default), the list is obtained by
            running ``git ls-files`` in *repo_root*.

    Returns:
        A (possibly empty) list of :class:`RegistrationFinding` objects,
        ordered: *unclassified_file* entries first, then *stale_path*
        entries, then *duplicate_registration* entries.

    Raises:
        RuntimeError: when *tracked_files* is ``None`` and ``git ls-files``
            cannot be run successfully (e.g. git not installed or *repo_root*
            is not a git repository).
    """
    # ---- resolve tracked files --------------------------------------------------
    if tracked_files is None:
        result = subprocess.run(  # nosec B603, B607
            ["git", "ls-files"],  # noqa: S607
            cwd=repo_root,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"git ls-files failed in {repo_root}: {result.stderr.strip()}"
            )
        tracked_files = [
            line.strip() for line in result.stdout.splitlines() if line.strip()
        ]

    tracked_set = set(tracked_files)

    # ---- per-module expansion --------------------------------------------------
    file_to_modules = _build_file_claimants(taxonomy, repo_root)

    findings: list[RegistrationFinding] = []

    # -- unclassified files -------------------------------------------------------
    unclassified = sorted(tracked_set - set(file_to_modules))
    for path in unclassified:
        findings.append(
            RegistrationFinding(
                kind="unclassified_file",
                message=f"File '{path}' is not claimed by any module",
                file=path,
            )
        )

    # -- stale paths --------------------------------------------------------------
    for module_entry in taxonomy.get("modules", []):
        module_id: str = module_entry["id"]
        _, stale_entries = _expand_module_paths(
            module_id, module_entry.get("paths", []), repo_root
        )
        for pattern in sorted(stale_entries):
            findings.append(
                RegistrationFinding(
                    kind="stale_path",
                    message=(
                        f"Module '{module_id}' path '{pattern}' matches "
                        "no files on disk"
                    ),
                    module_id=module_id,
                )
            )

    # -- duplicate registrations --------------------------------------------------
    duplicates = {
        path: ids
        for path, ids in file_to_modules.items()
        if len(ids) >= 2 and path in tracked_set
    }
    for path in sorted(duplicates):
        ids = duplicates[path]
        findings.append(
            RegistrationFinding(
                kind="duplicate_registration",
                message=(
                    f"File '{path}' is claimed by multiple modules: " + ", ".join(ids)
                ),
                file=path,
                module_id=ids[0],
                other_module_id=ids[1],
            )
        )

    return findings


def validate_paths(
    taxonomy: dict[str, Any],
    repo_root: Path,
) -> list[PathFinding]:
    """Check that every module path entry resolves to at least one file on disk.

    Literal paths are checked via ``(repo_root / path).exists()``.  Glob
    patterns are expanded via ``Path.glob()`` and must match at least one
    file.

    This function does **not** use ``git ls-files`` — it validates against
    the actual filesystem only.

    Args:
        taxonomy: a parsed ``modules.yaml`` dict.
        repo_root: the repository root directory.

    Returns:
        A (possibly empty) list of :class:`PathFinding` objects.  The
        function does not short-circuit; it collects all findings across
        all modules.
    """
    findings: list[PathFinding] = []

    for module_entry in taxonomy.get("modules", []):
        module_id: str = module_entry["id"]
        for path_entry in module_entry.get("paths", []):
            if _has_glob_metacharacters(path_entry):
                matches = list(repo_root.glob(path_entry))
                if not matches:
                    findings.append(
                        PathFinding(
                            kind="glob_empty",
                            message=(
                                f"Module '{module_id}' glob '{path_entry}' "
                                "matches no files on disk"
                            ),
                            module_id=module_id,
                            path=path_entry,
                        )
                    )
            else:
                if not (repo_root / path_entry).exists():
                    findings.append(
                        PathFinding(
                            kind="path_not_found",
                            message=(
                                f"Module '{module_id}' path '{path_entry}' "
                                "does not exist on disk"
                            ),
                            module_id=module_id,
                            path=path_entry,
                        )
                    )

    return findings
