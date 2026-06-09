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
    assert captured.out.strip() == "robotsix-modules 0.2.0"


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


# ---------------------------------------------------------------------------
# CLI: check-registration
# ---------------------------------------------------------------------------


def test_check_registration_valid_fixture_no_findings(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    """Valid taxonomy in a git repo with all tracked files covered → exit 0."""
    (tmp_path / "src" / "example").mkdir(parents=True)
    (tmp_path / "src" / "example" / "app.py").touch()

    yaml_path = tmp_path / "modules.yaml"
    yaml_path.write_text(
        "modules:\n"
        "  - id: example\n"
        "    description: A minimal valid module.\n"
        "    paths:\n"
        "      - src/example/**\n",
        encoding="utf-8",
    )

    import subprocess

    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
    # Only track the source file, not modules.yaml itself
    subprocess.run(
        ["git", "add", "src/example/app.py"], cwd=tmp_path, capture_output=True
    )
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
        cwd=tmp_path,
        capture_output=True,
    )

    code = main(["check-registration", str(yaml_path), "--root", str(tmp_path)])
    captured = capsys.readouterr()
    assert code == 0, f"stderr: {captured.err}"


def test_check_registration_clean_tmp_path(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    """Valid taxonomy + all files covered → exit 0."""
    (tmp_path / "src" / "example").mkdir(parents=True)
    (tmp_path / "src" / "example" / "app.py").touch()

    yaml_path = tmp_path / "modules.yaml"
    yaml_path.write_text(
        "modules:\n"
        "  - id: example\n"
        "    description: x\n"
        "    paths:\n"
        "      - src/example/**\n",
        encoding="utf-8",
    )

    # init a git repo so git ls-files works
    import subprocess

    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
    subprocess.run(
        ["git", "add", "src/example/app.py"], cwd=tmp_path, capture_output=True
    )
    # We need a minimal git config to commit
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
        cwd=tmp_path,
        capture_output=True,
    )

    code = main(["check-registration", str(yaml_path), "--root", str(tmp_path)])
    captured = capsys.readouterr()
    assert code == 0, f"stderr: {captured.err}"
    assert captured.out == ""


def test_check_registration_unclassified_exit_one(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    """Taxonomy with unclaimed tracked file → exit 1."""
    (tmp_path / "orphan.txt").touch()

    yaml_path = tmp_path / "modules.yaml"
    yaml_path.write_text(
        "modules:\n"
        "  - id: example\n"
        "    description: x\n"
        "    paths:\n"
        "      - src/example/**\n",
        encoding="utf-8",
    )

    import subprocess

    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "add", "orphan.txt"], cwd=tmp_path, capture_output=True)
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
        cwd=tmp_path,
        capture_output=True,
    )

    code = main(["check-registration", str(yaml_path), "--root", str(tmp_path)])
    captured = capsys.readouterr()
    assert code == 1
    assert "orphan.txt" in captured.err
    assert "not claimed" in captured.err.lower()


def test_check_registration_missing_file_exit_two(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Missing modules.yaml → exit 2."""
    code = main(["check-registration", "does-not-exist.yaml"])
    captured = capsys.readouterr()
    assert code == 2
    assert "file not found" in captured.err


def test_check_registration_invalid_yaml_exit_two(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    """Invalid YAML in modules.yaml → exit 2."""
    bad = tmp_path / "broken.yaml"
    bad.write_text("key: [unclosed", encoding="utf-8")
    code = main(["check-registration", str(bad)])
    captured = capsys.readouterr()
    assert code == 2
    assert "invalid YAML" in captured.err


def test_check_registration_root_flag_respected(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    """--root flag is respected when resolving paths."""
    root = tmp_path / "myroot"
    root.mkdir()
    (root / "src").mkdir()
    (root / "src" / "lib.py").touch()

    yaml_path = tmp_path / "modules.yaml"
    yaml_path.write_text(
        "modules:\n  - id: lib\n    description: x\n    paths:\n      - src/lib.py\n",
        encoding="utf-8",
    )

    import subprocess

    subprocess.run(["git", "init"], cwd=root, capture_output=True)
    subprocess.run(["git", "add", "src/lib.py"], cwd=root, capture_output=True)
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
        cwd=root,
        capture_output=True,
    )

    code = main(["check-registration", str(yaml_path), "--root", str(root)])
    captured = capsys.readouterr()
    assert code == 0, f"stderr: {captured.err}"


# ---------------------------------------------------------------------------
# CLI: validate-paths
# ---------------------------------------------------------------------------


def test_validate_paths_valid_exit_zero(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    """Valid taxonomy with all paths resolving → exit 0."""
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").touch()

    yaml_path = tmp_path / "modules.yaml"
    yaml_path.write_text(
        "modules:\n"
        "  - id: example\n"
        "    description: x\n"
        "    paths:\n"
        "      - src/app.py\n",
        encoding="utf-8",
    )

    code = main(["validate-paths", str(yaml_path), "--root", str(tmp_path)])
    captured = capsys.readouterr()
    assert code == 0, f"stderr: {captured.err}"
    assert captured.out == ""


def test_validate_paths_broken_literal_exit_one(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    """Taxonomy with a broken literal path → exit 1."""
    yaml_path = tmp_path / "modules.yaml"
    yaml_path.write_text(
        "modules:\n"
        "  - id: example\n"
        "    description: x\n"
        "    paths:\n"
        "      - src/missing.py\n",
        encoding="utf-8",
    )

    code = main(["validate-paths", str(yaml_path), "--root", str(tmp_path)])
    captured = capsys.readouterr()
    assert code == 1
    assert "does not exist" in captured.err.lower()
    assert "src/missing.py" in captured.err


def test_validate_paths_missing_file_exit_two(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Missing modules.yaml → exit 2."""
    code = main(["validate-paths", "does-not-exist.yaml"])
    captured = capsys.readouterr()
    assert code == 2
    assert "file not found" in captured.err


def test_validate_paths_invalid_yaml_exit_two(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    """Invalid YAML in modules.yaml → exit 2."""
    bad = tmp_path / "broken.yaml"
    bad.write_text("key: [unclosed", encoding="utf-8")
    code = main(["validate-paths", str(bad)])
    captured = capsys.readouterr()
    assert code == 2
    assert "invalid YAML" in captured.err


def test_validate_paths_root_flag_respected(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    """--root flag is respected when checking literal paths."""
    root = tmp_path / "myroot"
    root.mkdir()
    (root / "src").mkdir()
    (root / "src" / "lib.py").touch()

    yaml_path = tmp_path / "modules.yaml"
    yaml_path.write_text(
        "modules:\n  - id: lib\n    description: x\n    paths:\n      - src/lib.py\n",
        encoding="utf-8",
    )

    code = main(["validate-paths", str(yaml_path), "--root", str(root)])
    captured = capsys.readouterr()
    assert code == 0, f"stderr: {captured.err}"
