"""Tests for the robotsix-modules CLI entry points."""

from __future__ import annotations

from pathlib import Path

import pytest

from robotsix_modules import SCHEMA_PATH, validate_file
from robotsix_modules.cli import main, validate_main

FIXTURES = Path(__file__).parent / "fixtures"
VALID = str(FIXTURES / "valid_modules.yaml")
INVALID = str(FIXTURES / "invalid_modules.yaml")


def test_valid_fixture_exit_zero_empty_output(
    capsys: pytest.CaptureFixture[str],
) -> None:
    code = main(["validate", VALID])
    captured = capsys.readouterr()
    assert code == 0
    assert captured.out == ""
    assert captured.err == ""


def test_invalid_fixture_exit_one_names_pointer(
    capsys: pytest.CaptureFixture[str],
) -> None:
    code = main(["validate", INVALID])
    captured = capsys.readouterr()
    assert code == 1
    # The first module is missing its id; the second has empty paths.
    assert "modules[0]" in captured.err
    assert "modules[1]" in captured.err
    assert captured.out == ""


def test_missing_path_exit_two_names_file(capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["validate", "does-not-exist.yaml"])
    captured = capsys.readouterr()
    assert code == 2
    assert "file not found" in captured.err
    assert "does-not-exist.yaml" in captured.err


def test_version_exit_zero_stdout(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert captured.out.strip() == "robotsix-modules 0.1.0"


def test_schema_override_used(capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["validate", VALID, "--schema", str(SCHEMA_PATH)])
    captured = capsys.readouterr()
    assert code == 0
    assert captured.err == ""


def test_validate_main_multiple_paths(capsys: pytest.CaptureFixture[str]) -> None:
    # One valid + one invalid -> overall exit 1.
    code = validate_main([VALID, INVALID])
    captured = capsys.readouterr()
    assert code == 1
    assert "modules[0]" in captured.err


def test_validate_main_single_valid(capsys: pytest.CaptureFixture[str]) -> None:
    code = validate_main([VALID])
    captured = capsys.readouterr()
    assert code == 0
    assert captured.err == ""


def test_invalid_taxonomy_yaml_exit_two(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    bad = tmp_path / "broken.yaml"
    bad.write_text("key: [unclosed", encoding="utf-8")
    code = main(["validate", str(bad)])
    captured = capsys.readouterr()
    assert code == 2
    assert "invalid YAML" in captured.err
    assert str(bad) in captured.err


def test_missing_schema_file_exit_two(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    missing = tmp_path / "no-such-schema.yaml"
    code = main(["validate", VALID, "--schema", str(missing)])
    captured = capsys.readouterr()
    assert code == 2
    assert "schema file not found" in captured.err
    assert str(missing) in captured.err


def test_invalid_schema_yaml_exit_two(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    bad_schema = tmp_path / "broken-schema.yaml"
    bad_schema.write_text("key: [unclosed", encoding="utf-8")
    code = main(["validate", VALID, "--schema", str(bad_schema)])
    captured = capsys.readouterr()
    assert code == 2
    assert "invalid YAML in schema" in captured.err
    assert str(bad_schema) in captured.err


def test_validate_main_schema_override_valid(
    capsys: pytest.CaptureFixture[str],
) -> None:
    code = validate_main([VALID, "--schema", str(SCHEMA_PATH)])
    captured = capsys.readouterr()
    assert code == 0
    assert captured.err == ""


def test_validate_main_schema_override_missing(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    missing = tmp_path / "no-such-schema.yaml"
    code = validate_main([VALID, "--schema", str(missing)])
    captured = capsys.readouterr()
    assert code == 2
    assert "schema file not found" in captured.err
    assert str(missing) in captured.err


def test_validate_file_valid_no_schema() -> None:
    assert validate_file(VALID) == []


def test_validate_file_valid_schema_override() -> None:
    assert validate_file(VALID, schema_path=str(SCHEMA_PATH)) == []


def test_validate_file_invalid_names_pointer() -> None:
    errors = validate_file(INVALID)
    assert errors
    assert any("modules[0]" in message for message in errors)
