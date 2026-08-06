"""Self-tests for the published pre-commit hook (``.pre-commit-hooks.yaml``)."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

FIXTURES = Path(__file__).parent / "fixtures"
VALID = str(FIXTURES / "valid_modules.yaml")
INVALID = str(FIXTURES / "invalid_modules.yaml")
REPO_ROOT = Path(__file__).resolve().parents[2]

MANIFEST_PATH = REPO_ROOT / ".pre-commit-hooks.yaml"


# ---------------------------------------------------------------------------
# Tier 1 — manifest structure
# ---------------------------------------------------------------------------


def test_manifest_structure() -> None:
    """``.pre-commit-hooks.yaml`` has correct structure and entry."""
    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    assert isinstance(manifest, list), "top-level must be a list of hooks"
    assert len(manifest) >= 1, "at least one hook entry required"

    entry = next(
        (h for h in manifest if h.get("id") == "validate-module-taxonomy"), None
    )
    assert entry is not None, "validate-module-taxonomy hook missing from manifest"

    assert entry["id"] == "validate-module-taxonomy"
    assert entry["name"] == "Validate module taxonomy"
    assert isinstance(entry.get("description"), str)
    assert entry["entry"] == "robotsix-modules-validate"
    assert entry["language"] == "python"
    assert entry["files"] == r"^docs/modules\.ya?ml$"
    assert entry["types_or"] == ["yaml"]


def test_manifest_entry_matches_console_script() -> None:
    """Hook ``entry`` matches a key in ``[project.scripts]``."""
    import tomllib

    pyproject = tomllib.loads(
        (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    )
    scripts = pyproject.get("project", {}).get("scripts", {})

    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    entry = next(
        (h for h in manifest if h.get("id") == "validate-module-taxonomy"), None
    )
    assert entry is not None

    hook_entry = entry["entry"]
    assert hook_entry in scripts, (
        f"hook entry {hook_entry!r} not found in [project.scripts]; "
        f"available: {sorted(scripts)}"
    )


# ---------------------------------------------------------------------------
# Tier 2 — end-to-end integration via pre-commit
# ---------------------------------------------------------------------------


def _resolve_pre_commit() -> str:
    pre_commit = shutil.which("pre-commit")
    if pre_commit is None:
        # Also check inside the venv (uv run creates a .venv in the repo root)
        venv_bin = REPO_ROOT / ".venv" / "bin" / "pre-commit"
        if venv_bin.exists():
            pre_commit = str(venv_bin)
        else:
            pytest.skip("pre-commit not found on PATH or in venv")
    return pre_commit


def _init_git_repo(path: Path) -> None:
    subprocess.run(["git", "init"], cwd=path, capture_output=True, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=test",
            "-c",
            "user.email=test@test",
            "commit",
            "--allow-empty",
            "-m",
            "init",
        ],
        cwd=path,
        capture_output=True,
        check=True,
    )


def test_pre_commit_run_hook_valid(tmp_path: Path) -> None:
    """``pre-commit try-repo`` succeeds on a valid ``modules.yaml`` fixture."""
    pre_commit = _resolve_pre_commit()
    _init_git_repo(tmp_path)

    docs = tmp_path / "docs"
    docs.mkdir()
    shutil.copy(VALID, docs / "modules.yaml")

    proc = subprocess.run(
        [
            pre_commit,
            "try-repo",
            str(REPO_ROOT),
            "validate-module-taxonomy",
            "--files",
            "docs/modules.yaml",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, (
        f"pre-commit try-repo failed (exit {proc.returncode})\n"
        f"stdout:\n{proc.stdout}\n"
        f"stderr:\n{proc.stderr}"
    )


def test_pre_commit_run_hook_invalid(tmp_path: Path) -> None:
    """``pre-commit try-repo`` fails on an invalid ``modules.yaml`` fixture."""
    pre_commit = _resolve_pre_commit()
    _init_git_repo(tmp_path)

    docs = tmp_path / "docs"
    docs.mkdir()
    shutil.copy(INVALID, docs / "modules.yaml")

    proc = subprocess.run(
        [
            pre_commit,
            "try-repo",
            str(REPO_ROOT),
            "validate-module-taxonomy",
            "--files",
            "docs/modules.yaml",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert proc.returncode != 0, (
        f"pre-commit try-repo unexpectedly passed (exit {proc.returncode})\n"
        f"stdout:\n{proc.stdout}\n"
        f"stderr:\n{proc.stderr}"
    )
