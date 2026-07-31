"""Shared path utilities used by registration and findings modules.

Extracted from ``registration.py`` to break a circular dependency with
``_findings.py``.
"""

from __future__ import annotations

from pathlib import Path


def _has_glob_metacharacters(pattern: str) -> bool:
    """Return True when *pattern* contains ``*``, ``?``, or ``[``."""
    return any(c in pattern for c in "*?[")


def _glob_paths(repo_root: Path, pattern: str) -> list[Path]:
    """Expand *pattern* under *repo_root* via Path.glob."""
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
