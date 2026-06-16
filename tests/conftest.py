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
