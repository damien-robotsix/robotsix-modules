"""Tests for the robotsix-modules CLI entry points."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
from conftest import git_commit

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


# ---------------------------------------------------------------------------
# Logging verbosity
# ---------------------------------------------------------------------------


def test_verbose_info_logging(capsys: pytest.CaptureFixture[str]) -> None:
    """-v enables INFO-level logging to stderr."""
    code = main(["validate", VALID, "-v"])
    captured = capsys.readouterr()
    assert code == 0
    assert "INFO:" in captured.err
    assert "loading" in captured.err


def test_verbose_debug_logging(capsys: pytest.CaptureFixture[str]) -> None:
    """-vv enables DEBUG-level logging to stderr."""
    code = main(["validate", VALID, "-vv"])
    captured = capsys.readouterr()
    assert code == 0
    assert "DEBUG:" in captured.err
    assert "loaded" in captured.err


def test_validate_file_invalid_names_pointer() -> None:
    errors = validate_file(INVALID)
    assert errors
    assert any("modules[0]" in message for message in errors)


# ---------------------------------------------------------------------------
# CLI: check-registration
# ---------------------------------------------------------------------------


def test_check_registration_valid_fixture_no_findings(
    capsys: pytest.CaptureFixture[str], git_repo: Path
) -> None:
    """Valid taxonomy in a git repo with all tracked files covered → exit 0."""
    (git_repo / "src" / "example").mkdir(parents=True)
    (git_repo / "src" / "example" / "app.py").touch()

    yaml_path = git_repo / "modules.yaml"
    yaml_path.write_text(
        "modules:\n"
        "  - id: example\n"
        "    description: A minimal valid module.\n"
        "    paths:\n"
        "      - src/example/**\n",
        encoding="utf-8",
    )

    # Only track the source file, not modules.yaml itself
    git_commit(git_repo, "src/example/app.py")

    code = main(["check-registration", str(yaml_path), "--root", str(git_repo)])
    captured = capsys.readouterr()
    assert code == 0, f"stderr: {captured.err}"


def test_check_registration_clean_tmp_path(
    capsys: pytest.CaptureFixture[str], git_repo: Path
) -> None:
    """Valid taxonomy + all files covered → exit 0."""
    (git_repo / "src" / "example").mkdir(parents=True)
    (git_repo / "src" / "example" / "app.py").touch()

    yaml_path = git_repo / "modules.yaml"
    yaml_path.write_text(
        "modules:\n"
        "  - id: example\n"
        "    description: x\n"
        "    paths:\n"
        "      - src/example/**\n",
        encoding="utf-8",
    )

    git_commit(git_repo, "src/example/app.py")

    code = main(["check-registration", str(yaml_path), "--root", str(git_repo)])
    captured = capsys.readouterr()
    assert code == 0, f"stderr: {captured.err}"
    assert captured.out == ""


def test_check_registration_unclassified_exit_one(
    capsys: pytest.CaptureFixture[str], git_repo: Path
) -> None:
    """Taxonomy with unclaimed tracked file → exit 1."""
    (git_repo / "orphan.txt").touch()

    yaml_path = git_repo / "modules.yaml"
    yaml_path.write_text(
        "modules:\n"
        "  - id: example\n"
        "    description: x\n"
        "    paths:\n"
        "      - src/example/**\n",
        encoding="utf-8",
    )

    git_commit(git_repo, "orphan.txt")

    code = main(["check-registration", str(yaml_path), "--root", str(git_repo)])
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

    subprocess.run(["git", "init"], cwd=root, capture_output=True, check=True)
    git_commit(root, "src/lib.py")

    code = main(["check-registration", str(yaml_path), "--root", str(root)])
    captured = capsys.readouterr()
    assert code == 0, f"stderr: {captured.err}"


def test_check_registration_non_git_root_exit_two(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    """Non-git --root causes git ls-files to fail → RuntimeError → exit 2."""
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

    code = main(["check-registration", str(yaml_path), "--root", str(tmp_path)])
    captured = capsys.readouterr()
    assert code == 2
    assert "git ls-files failed" in captured.err


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


# ---------------------------------------------------------------------------
# CLI: --output-format json
# ---------------------------------------------------------------------------


def _init_repo_with_orphan(git_repo: Path) -> Path:
    """Create a git repo with an unclaimed tracked file. Return the yaml path."""
    (git_repo / "orphan.txt").touch()

    yaml_path = git_repo / "modules.yaml"
    yaml_path.write_text(
        "modules:\n"
        "  - id: example\n"
        "    description: x\n"
        "    paths:\n"
        "      - src/example/**\n",
        encoding="utf-8",
    )

    git_commit(git_repo, "orphan.txt")
    return yaml_path


def test_check_registration_json_findings(
    capsys: pytest.CaptureFixture[str], git_repo: Path
) -> None:
    """JSON mode emits a RegistrationFinding object and exits 1."""
    yaml_path = _init_repo_with_orphan(git_repo)

    code = main(
        [
            "check-registration",
            str(yaml_path),
            "--root",
            str(git_repo),
            "--output-format",
            "json",
        ]
    )
    captured = capsys.readouterr()
    assert code == 1
    assert captured.err == ""
    payload = json.loads(captured.out)
    assert payload["findings"]
    finding = payload["findings"][0]
    assert finding["kind"] == "unclassified_file"
    assert "message" in finding
    assert finding["file"] == "orphan.txt"


def test_check_registration_json_clean(
    capsys: pytest.CaptureFixture[str], git_repo: Path
) -> None:
    """JSON mode on a clean repo emits {"findings": []} and exits 0."""
    (git_repo / "src" / "example").mkdir(parents=True)
    (git_repo / "src" / "example" / "app.py").touch()

    yaml_path = git_repo / "modules.yaml"
    yaml_path.write_text(
        "modules:\n"
        "  - id: example\n"
        "    description: x\n"
        "    paths:\n"
        "      - src/example/**\n",
        encoding="utf-8",
    )

    git_commit(git_repo, "src/example/app.py")

    code = main(
        [
            "check-registration",
            str(yaml_path),
            "--root",
            str(git_repo),
            "--output-format",
            "json",
        ]
    )
    captured = capsys.readouterr()
    assert code == 0, f"stderr: {captured.err}"
    assert captured.err == ""
    assert json.loads(captured.out) == {"findings": []}


def test_validate_paths_json_findings(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    """JSON mode emits a PathFinding object and exits 1."""
    yaml_path = tmp_path / "modules.yaml"
    yaml_path.write_text(
        "modules:\n"
        "  - id: example\n"
        "    description: x\n"
        "    paths:\n"
        "      - src/missing.py\n",
        encoding="utf-8",
    )

    code = main(
        [
            "validate-paths",
            str(yaml_path),
            "--root",
            str(tmp_path),
            "--output-format",
            "json",
        ]
    )
    captured = capsys.readouterr()
    assert code == 1
    assert captured.err == ""
    payload = json.loads(captured.out)
    assert payload["findings"]
    finding = payload["findings"][0]
    assert "kind" in finding
    assert finding["module_id"] == "example"
    assert finding["path"] == "src/missing.py"


def test_validate_json_invalid_and_valid(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """validate JSON mode emits {"errors": [...]} (exit 1) and [] (exit 0)."""
    code = main(["validate", INVALID, "--output-format", "json"])
    captured = capsys.readouterr()
    assert code == 1
    assert captured.err == ""
    payload = json.loads(captured.out)
    assert payload["errors"]

    code = main(["validate", VALID, "--output-format", "json"])
    captured = capsys.readouterr()
    assert code == 0
    assert captured.err == ""
    assert json.loads(captured.out) == {"errors": []}


def test_validate_json_file_error_exit_two(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Operational errors stay on stderr and exit 2 even in JSON mode."""
    code = main(["validate", "does-not-exist.yaml", "--output-format", "json"])
    captured = capsys.readouterr()
    assert code == 2
    assert "file not found" in captured.err
    assert captured.out == ""


def test_validate_main_json_single_document(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The wrapper emits one parseable JSON document across multiple paths."""
    code = validate_main([VALID, INVALID, "--output-format", "json"])
    captured = capsys.readouterr()
    assert code == 1
    payload = json.loads(captured.out)
    assert payload["errors"]

    code = validate_main([VALID, "--output-format", "json"])
    captured = capsys.readouterr()
    assert code == 0
    assert json.loads(captured.out) == {"errors": []}


def test_validate_main_json_missing_file(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """JSON mode: missing taxonomy file → exit 2, file-not-found on stderr."""
    code = validate_main(["does-not-exist.yaml", "--output-format", "json"])
    captured = capsys.readouterr()
    assert code == 2
    assert "file not found" in captured.err


def test_validate_main_json_schema_missing(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    """JSON mode: missing schema file → exit 2, schema-not-found on stderr."""
    missing = tmp_path / "no-such.yaml"
    code = validate_main([VALID, "--schema", str(missing), "--output-format", "json"])
    captured = capsys.readouterr()
    assert code == 2
    assert "schema file not found" in captured.err


def test_validate_main_json_schema_bad_yaml(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    """JSON mode: broken schema YAML → exit 2, invalid-YAML on stderr."""
    bad_schema = tmp_path / "bad-schema.yaml"
    bad_schema.write_text("key: [unclosed", encoding="utf-8")
    code = validate_main(
        [VALID, "--schema", str(bad_schema), "--output-format", "json"]
    )
    captured = capsys.readouterr()
    assert code == 2
    assert "invalid YAML in schema" in captured.err
