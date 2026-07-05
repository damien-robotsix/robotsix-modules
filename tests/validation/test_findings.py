"""Unit tests for ``robotsix_modules.validation._findings``."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from robotsix_modules._exceptions import GitOperationError
from robotsix_modules.validation import FindingKind
from robotsix_modules.validation._findings import (
    _build_file_claimants,
    _expand_module_paths,
    _find_duplicates,
    _find_stale_paths,
    _find_unclassified,
    _resolve_tracked_files,
)

# ---------------------------------------------------------------------------
# _expand_module_paths
# ---------------------------------------------------------------------------


def test_expand_module_paths_all_claimed(tmp_path: Path) -> None:
    """Every pattern matches at least one on-disk file."""
    (tmp_path / "src" / "foo").mkdir(parents=True)
    (tmp_path / "src" / "foo" / "a.py").touch()
    (tmp_path / "tests" / "foo").mkdir(parents=True)
    (tmp_path / "tests" / "foo" / "test_a.py").touch()

    claimed, stale = _expand_module_paths(
        "mod", ["src/foo/**", "tests/foo/**"], tmp_path
    )
    assert claimed == {"src/foo/a.py", "tests/foo/test_a.py"}
    assert stale == set()


def test_expand_module_paths_all_stale(tmp_path: Path) -> None:
    """No pattern matches any on-disk file."""
    claimed, stale = _expand_module_paths("mod", ["nowhere/**", "ghost/*.py"], tmp_path)
    assert claimed == set()
    assert stale == {"nowhere/**", "ghost/*.py"}


def test_expand_module_paths_mixed(tmp_path: Path) -> None:
    """Some patterns match, others are stale."""
    (tmp_path / "src" / "mod").mkdir(parents=True)
    (tmp_path / "src" / "mod" / "main.py").touch()

    claimed, stale = _expand_module_paths("mod", ["src/mod/**", "missing/**"], tmp_path)
    assert claimed == {"src/mod/main.py"}
    assert stale == {"missing/**"}


def test_expand_module_paths_empty_entries(tmp_path: Path) -> None:
    """Empty path entries list → both sets empty."""
    claimed, stale = _expand_module_paths("mod", [], tmp_path)
    assert claimed == set()
    assert stale == set()


def test_expand_module_paths_directory_only_glob(tmp_path: Path) -> None:
    """Glob matches only directories, not files → stale."""
    (tmp_path / "docs" / "mod").mkdir(parents=True)
    # No files, only directories — "docs/mod/**" globs the directory itself
    # but _expand_module_paths only counts file matches.
    claimed, stale = _expand_module_paths("mod", ["docs/mod/**"], tmp_path)
    assert claimed == set()
    assert stale == {"docs/mod/**"}


# ---------------------------------------------------------------------------
# _build_file_claimants
# ---------------------------------------------------------------------------


def test_build_file_claimants_single_module(tmp_path: Path) -> None:
    """One module → file → [module_id] mapping."""
    (tmp_path / "src" / "alpha").mkdir(parents=True)
    (tmp_path / "src" / "alpha" / "app.py").touch()

    taxonomy = {
        "modules": [{"id": "alpha", "description": "x", "paths": ["src/alpha/**"]}]
    }
    file_to_modules = _build_file_claimants(taxonomy, tmp_path)
    assert file_to_modules == {"src/alpha/app.py": ["alpha"]}


def test_build_file_claimants_no_overlap(tmp_path: Path) -> None:
    """Two modules with disjoint paths."""
    (tmp_path / "src" / "alpha").mkdir(parents=True)
    (tmp_path / "src" / "alpha" / "a.py").touch()
    (tmp_path / "src" / "beta").mkdir(parents=True)
    (tmp_path / "src" / "beta" / "b.py").touch()

    taxonomy = {
        "modules": [
            {"id": "alpha", "description": "a", "paths": ["src/alpha/**"]},
            {"id": "beta", "description": "b", "paths": ["src/beta/**"]},
        ]
    }
    file_to_modules = _build_file_claimants(taxonomy, tmp_path)
    assert file_to_modules == {
        "src/alpha/a.py": ["alpha"],
        "src/beta/b.py": ["beta"],
    }


def test_build_file_claimants_overlapping(tmp_path: Path) -> None:
    """Two modules claim the same file."""
    (tmp_path / "shared").mkdir(parents=True)
    (tmp_path / "shared" / "util.py").touch()

    taxonomy = {
        "modules": [
            {"id": "alpha", "description": "a", "paths": ["shared/**"]},
            {"id": "beta", "description": "b", "paths": ["shared/**"]},
        ]
    }
    file_to_modules = _build_file_claimants(taxonomy, tmp_path)
    assert file_to_modules == {"shared/util.py": ["alpha", "beta"]}


def test_build_file_claimants_with_package(tmp_path: Path) -> None:
    """Taxonomy with package key → default globs are merged."""
    (tmp_path / "src" / "pkg" / "core").mkdir(parents=True)
    (tmp_path / "src" / "pkg" / "core" / "main.py").touch()

    taxonomy = {
        "package": "pkg",
        "modules": [{"id": "core", "description": "x"}],
    }
    file_to_modules = _build_file_claimants(taxonomy, tmp_path)
    # The default globs include src/pkg/core/**
    assert "src/pkg/core/main.py" in file_to_modules
    assert file_to_modules["src/pkg/core/main.py"] == ["core"]


def test_build_file_claimants_no_modules(tmp_path: Path) -> None:
    """Empty modules list → empty mapping."""
    file_to_modules = _build_file_claimants({"modules": []}, tmp_path)
    assert file_to_modules == {}


def test_build_file_claimants_no_package(tmp_path: Path) -> None:
    """No package key — only explicit paths are used."""
    (tmp_path / "src" / "pkg" / "core").mkdir(parents=True)
    (tmp_path / "src" / "pkg" / "core" / "main.py").touch()
    (tmp_path / "explicit").mkdir(parents=True)
    (tmp_path / "explicit" / "lib.py").touch()

    taxonomy = {
        "modules": [{"id": "core", "description": "x", "paths": ["explicit/**"]}]
    }
    file_to_modules = _build_file_claimants(taxonomy, tmp_path)
    # Default globs don't fire; only explicit paths count.
    assert file_to_modules == {"explicit/lib.py": ["core"]}


# ---------------------------------------------------------------------------
# _resolve_tracked_files
# ---------------------------------------------------------------------------


def test_resolve_tracked_files_passthrough(tmp_path: Path) -> None:
    """tracked_files is provided → returned unchanged."""
    result = _resolve_tracked_files(tmp_path, ["a.py", "b.py"])
    assert result == ["a.py", "b.py"]


def test_resolve_tracked_files_git_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """subprocess.run succeeds → parsed file list."""
    fake_result = subprocess.CompletedProcess(
        args=["git", "ls-files"],
        returncode=0,
        stdout="src/a.py\nsrc/b.py\n\n",
        stderr="",
    )
    monkeypatch.setattr(
        "robotsix_modules.validation._findings.subprocess.run",
        lambda *a, **kw: fake_result,
    )
    result = _resolve_tracked_files(tmp_path, None)
    assert result == ["src/a.py", "src/b.py"]


def test_resolve_tracked_files_file_not_found(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """git not on PATH → GitOperationError."""

    def _raise_fnf(*_a: object, **_kw: object) -> None:
        raise FileNotFoundError(2, "No such file or directory", "git")

    monkeypatch.setattr(
        "robotsix_modules.validation._findings.subprocess.run", _raise_fnf
    )
    with pytest.raises(GitOperationError, match="git is not installed"):
        _resolve_tracked_files(tmp_path, None)


def test_resolve_tracked_files_timeout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """git ls-files times out → GitOperationError."""

    def _raise_timeout(*_a: object, **_kw: object) -> None:
        raise subprocess.TimeoutExpired(cmd=["git", "ls-files"], timeout=60)

    monkeypatch.setattr(
        "robotsix_modules.validation._findings.subprocess.run", _raise_timeout
    )
    with pytest.raises(GitOperationError, match="timed out"):
        _resolve_tracked_files(tmp_path, None)


def test_resolve_tracked_files_non_zero_exit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """git ls-files returns non-zero → GitOperationError."""
    fake_result = subprocess.CompletedProcess(
        args=["git", "ls-files"],
        returncode=128,
        stdout="",
        stderr="fatal: not a git repository",
    )
    monkeypatch.setattr(
        "robotsix_modules.validation._findings.subprocess.run",
        lambda *a, **kw: fake_result,
    )
    with pytest.raises(GitOperationError, match="git ls-files failed"):
        _resolve_tracked_files(tmp_path, None)


# ---------------------------------------------------------------------------
# _find_unclassified
# ---------------------------------------------------------------------------


def test_find_unclassified_none() -> None:
    """All tracked files are classified."""
    findings = _find_unclassified(
        tracked_set={"a.py", "b.py"},
        file_to_modules={"a.py": ["mod"], "b.py": ["mod"]},
    )
    assert findings == []


def test_find_unclassified_single() -> None:
    """One unclassified file."""
    findings = _find_unclassified(
        tracked_set={"a.py", "orphan.txt"},
        file_to_modules={"a.py": ["mod"]},
    )
    assert len(findings) == 1
    f = findings[0]
    assert f.kind == FindingKind.UNCLASSIFIED_FILE
    assert f.file == "orphan.txt"
    assert f.module_id is None
    assert "not claimed" in f.message.lower()


def test_find_unclassified_multiple_sorted() -> None:
    """Multiple unclassified files — sorted order."""
    findings = _find_unclassified(
        tracked_set={"z.py", "a.py", "m.py"},
        file_to_modules={},
    )
    assert len(findings) == 3
    assert [f.file for f in findings] == ["a.py", "m.py", "z.py"]


def test_find_unclassified_empty_tracked_set() -> None:
    """No tracked files → no findings."""
    findings = _find_unclassified(
        tracked_set=set(),
        file_to_modules={"a.py": ["mod"]},
    )
    assert findings == []


# ---------------------------------------------------------------------------
# _find_stale_paths
# ---------------------------------------------------------------------------


def test_find_stale_paths_single(tmp_path: Path) -> None:
    """One stale path entry."""
    taxonomy = {
        "modules": [{"id": "gone", "description": "x", "paths": ["nowhere/**"]}]
    }
    findings = _find_stale_paths(taxonomy, tmp_path)
    assert len(findings) == 1
    f = findings[0]
    assert f.kind == FindingKind.STALE_PATH
    assert f.module_id == "gone"
    assert f.file is None
    assert "nowhere/**" in f.message


def test_find_stale_paths_multiple_modules(tmp_path: Path) -> None:
    """Multiple modules each with stale paths."""
    taxonomy = {
        "modules": [
            {"id": "a", "description": "x", "paths": ["a-gone/**"]},
            {"id": "b", "description": "x", "paths": ["b-gone/**"]},
        ]
    }
    findings = _find_stale_paths(taxonomy, tmp_path)
    assert len(findings) == 2
    assert {f.module_id for f in findings} == {"a", "b"}


def test_find_stale_paths_none(tmp_path: Path) -> None:
    """All patterns match on-disk files."""
    (tmp_path / "src" / "mod").mkdir(parents=True)
    (tmp_path / "src" / "mod" / "main.py").touch()

    taxonomy = {"modules": [{"id": "mod", "description": "x", "paths": ["src/mod/**"]}]}
    findings = _find_stale_paths(taxonomy, tmp_path)
    assert findings == []


def test_find_stale_paths_no_modules(tmp_path: Path) -> None:
    """Empty modules list → no findings."""
    findings = _find_stale_paths({"modules": []}, tmp_path)
    assert findings == []


def test_find_stale_paths_empty_paths(tmp_path: Path) -> None:
    """Module with empty paths → no stale findings."""
    taxonomy = {"modules": [{"id": "empty", "description": "x", "paths": []}]}
    findings = _find_stale_paths(taxonomy, tmp_path)
    assert findings == []


def test_find_stale_paths_sorted_stale_entries(tmp_path: Path) -> None:
    """Stale entries per module are sorted."""
    taxonomy = {
        "modules": [
            {
                "id": "multi",
                "description": "x",
                "paths": ["zzz/**", "aaa/**", "mmm/**"],
            }
        ]
    }
    findings = _find_stale_paths(taxonomy, tmp_path)
    assert len(findings) == 3
    messages = [f.message for f in findings]
    assert messages[0] < messages[1] < messages[2]


# ---------------------------------------------------------------------------
# _find_duplicates
# ---------------------------------------------------------------------------


def test_find_duplicates_none() -> None:
    """No files with multiple claimants."""
    findings = _find_duplicates(
        file_to_modules={"a.py": ["mod"]},
        tracked_set={"a.py"},
    )
    assert findings == []


def test_find_duplicates_two_claimants() -> None:
    """Two modules claim the same tracked file."""
    findings = _find_duplicates(
        file_to_modules={"shared.py": ["alpha", "beta"]},
        tracked_set={"shared.py"},
    )
    assert len(findings) == 1
    f = findings[0]
    assert f.kind == FindingKind.DUPLICATE_REGISTRATION
    assert f.file == "shared.py"
    assert f.module_id == "alpha"
    assert f.other_module_id == "beta"
    assert "alpha" in f.message
    assert "beta" in f.message


def test_find_duplicates_three_claimants() -> None:
    """Three modules claim the same tracked file — ids[0] and ids[1] used."""
    findings = _find_duplicates(
        file_to_modules={"shared.py": ["alpha", "beta", "gamma"]},
        tracked_set={"shared.py"},
    )
    assert len(findings) == 1
    f = findings[0]
    assert f.kind == FindingKind.DUPLICATE_REGISTRATION
    assert f.file == "shared.py"
    # Only first two are set as module_id / other_module_id.
    assert f.module_id == "alpha"
    assert f.other_module_id == "beta"
    # But the message references all three.
    assert "alpha" in f.message
    assert "beta" in f.message
    assert "gamma" in f.message


def test_find_duplicates_not_in_tracked_set() -> None:
    """File claimed by multiple modules but not tracked → no finding."""
    findings = _find_duplicates(
        file_to_modules={"shared.py": ["alpha", "beta"]},
        tracked_set={"other.py"},  # shared.py not in tracked_set
    )
    assert findings == []


def test_find_duplicates_multiple_files() -> None:
    """Multiple files each with duplicate claimants."""
    findings = _find_duplicates(
        file_to_modules={
            "a.py": ["mod1", "mod2"],
            "z.py": ["mod3", "mod4"],
        },
        tracked_set={"a.py", "z.py"},
    )
    assert len(findings) == 2
    # Sorted by file path.
    assert findings[0].file == "a.py"
    assert findings[1].file == "z.py"


def test_find_duplicates_single_claimant_not_duplicate() -> None:
    """File with only one claimant is not a duplicate."""
    findings = _find_duplicates(
        file_to_modules={
            "single.py": ["mod1"],
            "double.py": ["mod2", "mod3"],
        },
        tracked_set={"single.py", "double.py"},
    )
    assert len(findings) == 1
    assert findings[0].file == "double.py"
