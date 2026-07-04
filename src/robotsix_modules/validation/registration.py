"""Registration-completeness and path-resolution checks for module taxonomies.

These functions go beyond JSON Schema structural validation: they verify
that every tracked file in a repo is claimed by exactly one module, that
every module path resolves to at least one on-disk file, and that no two
modules accidentally claim the same file.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from ._findings import (
    RegistrationFinding,
    _build_file_claimants,
    _find_duplicates,
    _find_stale_paths,
    _find_unclassified,
    _resolve_tracked_files,
)
from .._exceptions import GitOperationError


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


def _glob_paths(repo_root: Path, pattern: str) -> list[Path]:
    """Expand *pattern* under *repo_root* with version-portable semantics.

    A pattern ending in a bare ``**`` segment is rewritten to ``**/*`` so
    that it matches files recursively on every supported Python version.
    On Python 3.13+ ``Path.glob`` treats a trailing ``**`` as matching both
    files and directories, but on Python 3.12 it matches directories only;
    rewriting to ``**/*`` yields the 3.13 behaviour everywhere.
    """
    if pattern == "**" or pattern.endswith("/**"):
        pattern = f"{pattern}/*"
    return list(repo_root.glob(pattern))


def compute_default_globs(module_id: str, package: str) -> list[str]:
    """Return the three convention globs for *module_id* in *package*.

    Covers the standard robotsix repo layout:
    - ``src/<package>/<module_id>/**``
    - ``tests/<module_id>/**``
    - ``docs/<module_id>/**``
    """
    return [
        f"src/{package}/{module_id}/**",
        f"tests/{module_id}/**",
        f"docs/{module_id}/**",
    ]


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
        GitOperationError: when *tracked_files* is ``None`` and ``git ls-files``
            cannot be run successfully (e.g. git not installed or *repo_root*
            is not a git repository).
    """
    tracked = _resolve_tracked_files(repo_root, tracked_files)
    file_to_modules = _build_file_claimants(taxonomy, repo_root)
    tracked_set = set(tracked)
    return (
        _find_unclassified(tracked_set, file_to_modules)
        + _find_stale_paths(taxonomy, repo_root)
        + _find_duplicates(file_to_modules, tracked_set)
    )


def check_coverage(
    taxonomy: dict[str, Any],
    repo_root: Path,
    *,
    tracked_files: list[str] | None = None,
) -> list[str]:
    """Check that every tracked file is covered by at least one module's globs.

    Collects all module globs (explicit ``paths`` + convention defaults) and
    verifies every tracked file is matched by at least one of them.  Only
    *unclassified_file* findings are returned; stale-path and duplicate
    findings are left to :func:`check_registration`.

    Args:
        taxonomy: a parsed ``modules.yaml`` dict.
        repo_root: the repository root directory.
        tracked_files: optional override — a list of repo-relative file
            paths.  When ``None`` (the default), the list is obtained by
            running ``git ls-files`` in *repo_root*.

    Returns:
        A (possibly empty) list of human-readable error messages, one per
        unclassified file.  Returns an empty list (graceful no-op) when
        ``git ls-files`` cannot be run — e.g. in a non-git directory.
    """
    try:
        findings = check_registration(taxonomy, repo_root, tracked_files=tracked_files)
    except GitOperationError:
        return []
    return [f.message for f in findings if f.kind == "unclassified_file"]


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
                matches = _glob_paths(repo_root, path_entry)
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
