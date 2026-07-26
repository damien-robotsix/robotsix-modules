"""Shared cross-cutting CLI tests."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from conftest import (
    run_invalid_yaml_test,
    run_missing_file_test,
    run_root_flag_respected_test,
)

from robotsix_modules import __version__
from robotsix_modules.cli import main, validate_main
from robotsix_modules.cli._exit_codes import ExitCode

FIXTURES = Path(__file__).parent / "fixtures"
VALID = str(FIXTURES / "valid_modules.yaml")


# ---------------------------------------------------------------------------
# version
# ---------------------------------------------------------------------------


def test_version_exit_zero_stdout(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert captured.out.strip() == f"robotsix-modules {__version__}"


# ===================================================================
# Shared parametrized error-path tests (replaces per-class duplicates)
# ===================================================================


@pytest.mark.parametrize("subcommand", ["check-registration", "validate-paths"])
def test_missing_yaml_file_exit_two(
    capsys: pytest.CaptureFixture[str],
    subcommand: str,
) -> None:
    run_missing_file_test(capsys, subcommand)


@pytest.mark.parametrize(
    "subcommand", ["validate", "check-registration", "validate-paths"]
)
def test_invalid_yaml_exit_two(
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
    subcommand: str,
) -> None:
    run_invalid_yaml_test(capsys, tmp_path, subcommand)


@pytest.mark.parametrize(
    "subcommand,needs_git",
    [("validate", False), ("check-registration", True), ("validate-paths", False)],
)
def test_root_flag_respected(
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
    subcommand: str,
    needs_git: bool,
) -> None:
    run_root_flag_respected_test(capsys, tmp_path, subcommand, needs_git=needs_git)


# ===================================================================
# Exception barrier
# ===================================================================


def test_main_unexpected_exception_returns_fatal(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A bug in validation logic returns ExitCode.FATAL (2), not a raw traceback."""

    def _broken_validate(*args: Any, **kwargs: Any) -> Any:
        raise TypeError("simulated bug in validation")

    monkeypatch.setattr("robotsix_modules.cli.validate", _broken_validate)
    code = main(["validate", VALID, "--root", str(tmp_path)])
    assert code == ExitCode.FATAL
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "internal error" in captured.err.lower()


def test_validate_main_unexpected_exception_returns_fatal(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A bug in validate_main logic returns ExitCode.FATAL (2), not a raw traceback."""

    def _broken_batch(*args: Any, **kwargs: Any) -> Any:
        raise ValueError("simulated bug in validate_main")

    monkeypatch.setattr("robotsix_modules.cli._validate_schema_batch", _broken_batch)
    code = validate_main([VALID, "--root", str(tmp_path)])
    assert code == ExitCode.FATAL
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "internal error" in captured.err.lower()
