"""Shared pytest fixtures for the robotsix-modules test suite."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    """Create an empty temporary git repository and return its path."""
    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True, check=True)
    return tmp_path


def git_commit(repo: Path, *files: str) -> None:
    """Stage and commit one or more files in a git repository."""
    for f in files:
        subprocess.run(["git", "add", f], cwd=repo, capture_output=True, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=test",
            "-c",
            "user.email=test@test",
            "commit",
            "-m",
            "init",
        ],
        cwd=repo,
        capture_output=True,
        check=True,
    )


# ---------------------------------------------------------------------------
# Shared CLI error-test helpers
# ---------------------------------------------------------------------------


def run_missing_file_test(capsys: pytest.CaptureFixture[str], subcommand: str) -> None:
    """Assert *subcommand* with a missing YAML file exits FATAL / 'file not found'."""
    from robotsix_modules.cli import main
    from robotsix_modules.cli._exit_codes import ExitCode

    code = main([subcommand, "does-not-exist.yaml"])
    captured = capsys.readouterr()
    assert code == ExitCode.FATAL
    assert "file not found" in captured.err


def run_invalid_yaml_test(
    capsys: pytest.CaptureFixture[str], tmp_path: Path, subcommand: str
) -> None:
    """Assert *subcommand* with broken YAML exits FATAL / 'invalid YAML'."""
    from robotsix_modules.cli import main
    from robotsix_modules.cli._exit_codes import ExitCode

    bad = tmp_path / "broken.yaml"
    bad.write_text("key: [unclosed", encoding="utf-8")
    code = main([subcommand, str(bad)])
    captured = capsys.readouterr()
    assert code == ExitCode.FATAL
    assert "invalid YAML" in captured.err


def run_root_flag_respected_test(
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
    subcommand: str,
    *,
    needs_git: bool = False,
) -> None:
    """Assert *subcommand* with --root resolves paths correctly."""
    from robotsix_modules.cli import main
    from robotsix_modules.cli._exit_codes import ExitCode

    root = tmp_path / "myroot"
    root.mkdir()
    (root / "src").mkdir()
    (root / "src" / "lib.py").touch()

    yaml_path = tmp_path / "modules.yaml"
    yaml_path.write_text(
        "modules:\n  - id: lib\n    description: x\n    paths:\n      - src/lib.py\n",
        encoding="utf-8",
    )

    if needs_git:
        subprocess.run(["git", "init"], cwd=root, capture_output=True, check=True)
        git_commit(root, "src/lib.py")

    code = main([subcommand, str(yaml_path), "--root", str(root)])
    captured = capsys.readouterr()
    assert code == ExitCode.OK, f"stderr: {captured.err}"
