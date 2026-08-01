"""Tests for shared path utilities."""

from __future__ import annotations

from pathlib import Path

import pytest

from robotsix_modules.validation._paths import (
    _glob_paths,
    _has_glob_metacharacters,
    compute_default_globs,
)

# ---------------------------------------------------------------------------
# _has_glob_metacharacters
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("src/foo.py", False),
        ("src/**/*.py", True),
        ("src/chapter?.md", True),
        ("src/[Ff]oo.py", True),
    ],
)
def test_has_glob_metacharacters(path: str, expected: bool) -> None:
    assert _has_glob_metacharacters(path) is expected


# ---------------------------------------------------------------------------
# _glob_paths
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("pattern", "files_to_create", "expected_count"),
    [
        # Non-empty matches
        ("*.py", ["a.py", "b.py"], 2),
        # Empty results
        ("*.md", ["a.py"], 0),
        # Pattern with glob metacharacters — nested directory
        ("src/**/*.py", [], 0),
        # Pattern without glob metacharacters — literal filename
        ("README.md", ["README.md"], 1),
    ],
)
def test_glob_paths(
    tmp_path: Path,
    pattern: str,
    files_to_create: list[str],
    expected_count: int,
) -> None:
    for fname in files_to_create:
        file_path = tmp_path / fname
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.touch()

    result = _glob_paths(tmp_path, pattern)
    assert len(result) == expected_count
    # All returned paths are relative to tmp_path
    for p in result:
        assert p.is_relative_to(tmp_path)


# ---------------------------------------------------------------------------
# compute_default_globs
# ---------------------------------------------------------------------------


def test_compute_default_globs() -> None:
    """Compute the three convention globs for a module_id/package pair."""
    result = compute_default_globs("cli", "my_pkg")
    assert result == ["src/my_pkg/cli/**", "tests/cli/**", "docs/cli/**"]
