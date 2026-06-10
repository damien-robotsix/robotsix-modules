"""Tests for registration and path-resolution validation."""

from __future__ import annotations

from pathlib import Path

import pytest

from robotsix_modules.validation.registration import (
    _has_glob_metacharacters,
    check_registration,
    validate_paths,
)

# ---------------------------------------------------------------------------
# _has_glob_metacharacters
# ---------------------------------------------------------------------------


def test_has_glob_metacharacters_literal() -> None:
    assert not _has_glob_metacharacters("src/foo.py")


def test_has_glob_metacharacters_star() -> None:
    assert _has_glob_metacharacters("src/**/*.py")


def test_has_glob_metacharacters_question() -> None:
    assert _has_glob_metacharacters("src/chapter?.md")


def test_has_glob_metacharacters_bracket() -> None:
    assert _has_glob_metacharacters("src/[Ff]oo.py")


# ---------------------------------------------------------------------------
# check_registration
# ---------------------------------------------------------------------------

SINGLE_MODULE_TAXONOMY = {
    "modules": [{"id": "example", "description": "x", "paths": ["src/example/**"]}]
}


def test_all_tracked_files_covered(tmp_path: Path) -> None:
    """All tracked files covered by exactly one module → no findings."""
    (tmp_path / "src" / "example").mkdir(parents=True)
    (tmp_path / "src" / "example" / "foo.py").touch()

    findings = check_registration(
        SINGLE_MODULE_TAXONOMY,
        tmp_path,
        tracked_files=["src/example/foo.py"],
    )
    assert findings == []


def test_unclassified_file(tmp_path: Path) -> None:
    """Tracked file not matching any module glob → unclassified_file."""
    (tmp_path / "src" / "example").mkdir(parents=True)
    (tmp_path / "src" / "example" / "foo.py").touch()
    (tmp_path / "orphan.txt").touch()

    findings = check_registration(
        SINGLE_MODULE_TAXONOMY,
        tmp_path,
        tracked_files=["src/example/foo.py", "orphan.txt"],
    )
    assert len(findings) == 1
    f = findings[0]
    assert f.kind == "unclassified_file"
    assert f.file == "orphan.txt"
    assert f.module_id is None
    assert f.other_module_id is None
    assert "orphan.txt" in f.message
    assert "not claimed" in f.message.lower()


def test_duplicate_registration(tmp_path: Path) -> None:
    """Tracked file matching two modules' globs → duplicate_registration."""
    (tmp_path / "shared").mkdir(parents=True)
    (tmp_path / "shared" / "util.py").touch()

    taxonomy = {
        "modules": [
            {"id": "mod-a", "description": "a", "paths": ["shared/**"]},
            {"id": "mod-b", "description": "b", "paths": ["shared/**"]},
        ]
    }
    findings = check_registration(
        taxonomy,
        tmp_path,
        tracked_files=["shared/util.py"],
    )
    assert len(findings) == 1
    f = findings[0]
    assert f.kind == "duplicate_registration"
    assert f.file == "shared/util.py"
    assert f.module_id in ("mod-a", "mod-b")
    assert f.other_module_id in ("mod-a", "mod-b")
    assert f.module_id != f.other_module_id
    assert "multiple modules" in f.message.lower()


def test_stale_path(tmp_path: Path) -> None:
    """Module path glob that matches zero on-disk files → stale_path."""
    taxonomy = {
        "modules": [{"id": "gone", "description": "x", "paths": ["nonexistent/**"]}]
    }
    findings = check_registration(
        taxonomy,
        tmp_path,
        tracked_files=[],
    )
    assert len(findings) == 1
    f = findings[0]
    assert f.kind == "stale_path"
    assert f.module_id == "gone"
    assert f.file is None
    assert "nonexistent/**" in f.message


def test_tracked_files_override_no_git_call(tmp_path: Path) -> None:
    """tracked_files override supplied → uses provided list, no subprocess."""
    # Create files on disk so the glob isn't stale — the point is that
    # no subprocess is called, even if the directory isn't a git repo.
    (tmp_path / "src" / "example").mkdir(parents=True)
    (tmp_path / "src" / "example" / "app.py").touch()
    findings = check_registration(
        SINGLE_MODULE_TAXONOMY,
        tmp_path,
        tracked_files=[],
    )
    # No tracked files means nothing to check for unclassified/duplicates.
    # The glob matches on-disk files so no stale findings either.
    assert findings == []


def test_git_ls_files_fails_non_repo(tmp_path: Path) -> None:
    """git ls-files fails in a non-repo dir → RuntimeError."""
    # tmp_path is not a git repo.
    with pytest.raises(RuntimeError, match="git ls-files failed"):
        check_registration(SINGLE_MODULE_TAXONOMY, tmp_path)


def test_ordering_unclassified_then_stale_then_duplicates(tmp_path: Path) -> None:
    """Findings follow the mandated order."""
    (tmp_path / "shared").mkdir(parents=True)
    (tmp_path / "shared" / "lib.py").touch()
    (tmp_path / "orphan.txt").touch()

    taxonomy = {
        "modules": [
            {"id": "mod-a", "description": "a", "paths": ["shared/**"]},
            {"id": "mod-b", "description": "b", "paths": ["shared/**"]},
            {"id": "stale-mod", "description": "s", "paths": ["nowhere/**"]},
        ]
    }
    findings = check_registration(
        taxonomy,
        tmp_path,
        tracked_files=["shared/lib.py", "orphan.txt"],
    )
    kinds = [f.kind for f in findings]
    assert kinds == [
        "unclassified_file",
        "stale_path",
        "duplicate_registration",
    ]


def test_sparse_checkout_unclassified(tmp_path: Path) -> None:
    """Tracked file not on disk → glob won't find it → unclassified."""
    # Create directory with one real file so the glob isn't stale,
    # but ghost.py is tracked and not on disk.
    (tmp_path / "src" / "example").mkdir(parents=True)
    (tmp_path / "src" / "example" / "real.py").touch()
    findings = check_registration(
        SINGLE_MODULE_TAXONOMY,
        tmp_path,
        tracked_files=["src/example/ghost.py", "src/example/real.py"],
    )
    assert len(findings) == 1
    assert findings[0].kind == "unclassified_file"
    assert findings[0].file == "src/example/ghost.py"


def test_multiple_stale_paths(tmp_path: Path) -> None:
    """A module with multiple stale paths produces one finding per path."""
    taxonomy = {
        "modules": [
            {
                "id": "multi-stale",
                "description": "x",
                "paths": ["gone/**", "also-gone/**", "present/*"],
            }
        ]
    }
    (tmp_path / "present").mkdir()
    (tmp_path / "present" / "a.txt").touch()

    findings = check_registration(
        taxonomy,
        tmp_path,
        tracked_files=["present/a.txt"],
    )
    stale = [f for f in findings if f.kind == "stale_path"]
    assert len(stale) == 2
    stale_patterns = {f.message for f in stale}
    assert any("gone/**" in m for m in stale_patterns)
    assert any("also-gone/**" in m for m in stale_patterns)


def test_module_with_no_paths_produces_stale(tmp_path: Path) -> None:
    """A module with empty paths → every path entry is stale (none exist)."""
    taxonomy = {"modules": [{"id": "empty-paths", "description": "x", "paths": []}]}
    findings = check_registration(
        taxonomy,
        tmp_path,
        tracked_files=[],
    )
    assert findings == []  # No path entries → no stale findings


def test_no_modules_empty_findings(tmp_path: Path) -> None:
    """Empty modules list with no tracked files → no findings."""
    findings = check_registration(
        {"modules": []},
        tmp_path,
        tracked_files=[],
    )
    assert findings == []


# ---------------------------------------------------------------------------
# validate_paths
# ---------------------------------------------------------------------------


def test_literal_path_exists(tmp_path: Path) -> None:
    """Literal path that exists on disk → no findings."""
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").touch()

    taxonomy = {"modules": [{"id": "lit", "description": "x", "paths": ["src/app.py"]}]}
    assert validate_paths(taxonomy, tmp_path) == []


def test_literal_path_not_found(tmp_path: Path) -> None:
    """Literal path does not exist → path_not_found."""
    taxonomy = {
        "modules": [{"id": "lit", "description": "x", "paths": ["src/missing.py"]}]
    }
    findings = validate_paths(taxonomy, tmp_path)
    assert len(findings) == 1
    f = findings[0]
    assert f.kind == "path_not_found"
    assert f.module_id == "lit"
    assert f.path == "src/missing.py"
    assert "does not exist" in f.message.lower()


def test_glob_matches_one_or_more_files(tmp_path: Path) -> None:
    """Glob pattern matching ≥1 file → no findings."""
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").touch()
    (tmp_path / "src" / "b.py").touch()

    taxonomy = {"modules": [{"id": "g", "description": "x", "paths": ["src/*.py"]}]}
    assert validate_paths(taxonomy, tmp_path) == []


def test_glob_empty(tmp_path: Path) -> None:
    """Glob pattern matching zero files → glob_empty."""
    taxonomy = {"modules": [{"id": "g", "description": "x", "paths": ["nothing/**"]}]}
    findings = validate_paths(taxonomy, tmp_path)
    assert len(findings) == 1
    f = findings[0]
    assert f.kind == "glob_empty"
    assert f.module_id == "g"
    assert f.path == "nothing/**"
    assert "matches no files" in f.message.lower()


def test_validate_paths_collects_all_errors(tmp_path: Path) -> None:
    """Does not short-circuit; collects findings from all modules."""
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "ok.py").touch()

    taxonomy = {
        "modules": [
            {"id": "m1", "description": "x", "paths": ["src/missing.py"]},
            {"id": "m2", "description": "x", "paths": ["gone/**"]},
            {"id": "m3", "description": "x", "paths": ["src/ok.py"]},
        ]
    }
    findings = validate_paths(taxonomy, tmp_path)
    assert len(findings) == 2
    kinds = {f.kind for f in findings}
    assert kinds == {"path_not_found", "glob_empty"}


def test_literal_path_directory(tmp_path: Path) -> None:
    """A literal path that is a directory still counts as existing."""
    (tmp_path / "mydir").mkdir()
    taxonomy = {"modules": [{"id": "d", "description": "x", "paths": ["mydir"]}]}
    assert validate_paths(taxonomy, tmp_path) == []


def test_validate_paths_no_modules(tmp_path: Path) -> None:
    """Empty modules list → no findings."""
    assert validate_paths({"modules": []}, tmp_path) == []
