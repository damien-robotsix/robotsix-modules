"""Tests for ``robotsix-modules validate`` and ``robotsix-modules-validate``."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from conftest import git_commit

from robotsix_modules import SCHEMA_PATH, validate_file
from robotsix_modules.cli import main, validate_main
from robotsix_modules.cli._exit_codes import ExitCode

FIXTURES = Path(__file__).parent / "fixtures"
VALID = str(FIXTURES / "valid_modules.yaml")
INVALID = str(FIXTURES / "invalid_modules.yaml")
SCHEMA = str(SCHEMA_PATH)


# ===================================================================
# validate
# ===================================================================


class TestValidate:
    """Tests for ``robotsix-modules validate``."""

    # -- text output ---------------------------------------------------------

    @pytest.mark.parametrize(
        "args,exit_code,err_substrs,out_empty,err_empty",
        [
            (["validate", VALID], ExitCode.OK, [], True, True),
            (
                ["validate", INVALID],
                ExitCode.ERRORS,
                ["modules[0]", "modules[1]"],
                True,
                False,
            ),
            (
                ["validate", "does-not-exist.yaml"],
                ExitCode.FATAL,
                ["file not found", "does-not-exist.yaml"],
                False,
                False,
            ),
            (["validate", VALID, "--schema", SCHEMA], ExitCode.OK, [], False, True),
            (
                ["validate", VALID, "-v"],
                ExitCode.OK,
                ["INFO:", "loading"],
                False,
                False,
            ),
            (
                ["validate", VALID, "-vv"],
                ExitCode.OK,
                ["DEBUG:", "loaded"],
                False,
                False,
            ),
        ],
    )
    def test_validate(
        self,
        capsys: pytest.CaptureFixture[str],
        args: list[str],
        exit_code: ExitCode,
        err_substrs: list[str],
        out_empty: bool,
        err_empty: bool,
        tmp_path: Path,
    ) -> None:
        # Isolate coverage check: use a non-git temp dir so check_coverage
        # gracefully returns [] rather than scanning the real repo.
        args = list(args) + ["--root", str(tmp_path)]
        code = main(args)
        captured = capsys.readouterr()
        assert code == exit_code
        if out_empty:
            assert captured.out == ""
        if err_empty:
            assert captured.err == ""
        for s in err_substrs:
            assert s in captured.err

    def test_missing_schema_file_exit_two(
        self,
        capsys: pytest.CaptureFixture[str],
        tmp_path: Path,
    ) -> None:
        missing = tmp_path / "no-such-schema.yaml"
        code = main(
            ["validate", VALID, "--schema", str(missing), "--root", str(tmp_path)]
        )
        captured = capsys.readouterr()
        assert code == ExitCode.FATAL
        assert "schema file not found" in captured.err
        assert str(missing) in captured.err

    def test_invalid_schema_yaml_exit_two(
        self,
        capsys: pytest.CaptureFixture[str],
        tmp_path: Path,
    ) -> None:
        bad_schema = tmp_path / "broken-schema.yaml"
        bad_schema.write_text("key: [unclosed", encoding="utf-8")
        code = main(
            [
                "validate",
                VALID,
                "--schema",
                str(bad_schema),
                "--root",
                str(tmp_path),
            ]
        )
        captured = capsys.readouterr()
        assert code == ExitCode.FATAL
        assert "invalid YAML in schema" in captured.err
        assert str(bad_schema) in captured.err

    # -- JSON output ---------------------------------------------------------

    @pytest.mark.parametrize(
        "file_path,exit_code,expect_errors",
        [(INVALID, ExitCode.ERRORS, True), (VALID, ExitCode.OK, False)],
    )
    def test_validate_json(
        self,
        capsys: pytest.CaptureFixture[str],
        file_path: str,
        exit_code: ExitCode,
        expect_errors: bool,
        tmp_path: Path,
    ) -> None:
        code = main(
            ["validate", file_path, "--output-format", "json", "--root", str(tmp_path)]
        )
        captured = capsys.readouterr()
        assert code == exit_code
        assert captured.err == ""
        payload = json.loads(captured.out)
        if expect_errors:
            assert payload["errors"]
        else:
            assert payload["errors"] == []

    def test_validate_json_file_error_exit_two(
        self,
        capsys: pytest.CaptureFixture[str],
        tmp_path: Path,
    ) -> None:
        code = main(
            [
                "validate",
                "does-not-exist.yaml",
                "--output-format",
                "json",
                "--root",
                str(tmp_path),
            ]
        )
        captured = capsys.readouterr()
        assert code == ExitCode.FATAL
        assert "file not found" in captured.err
        assert captured.out == ""


# ===================================================================
# validate_main  (robotsix-modules-validate)
# ===================================================================


class TestValidateMain:
    """Tests for ``robotsix-modules-validate`` (validate_main)."""

    # -- text output ---------------------------------------------------------

    @pytest.mark.parametrize(
        "args,exit_code,err_substrs,err_empty",
        [
            ([VALID, INVALID], ExitCode.ERRORS, ["modules[0]"], False),
            ([VALID], ExitCode.OK, [], True),
            ([VALID, "--schema", SCHEMA], ExitCode.OK, [], True),
            ([VALID, "-v"], ExitCode.OK, ["INFO:"], False),
            ([VALID, "-vv"], ExitCode.OK, ["DEBUG:"], False),
        ],
    )
    def test_validate_main(
        self,
        capsys: pytest.CaptureFixture[str],
        args: list[str],
        exit_code: ExitCode,
        err_substrs: list[str],
        err_empty: bool,
        tmp_path: Path,
    ) -> None:
        code = validate_main([*args, "--root", str(tmp_path)])
        captured = capsys.readouterr()
        assert code == exit_code
        if err_empty:
            assert captured.err == ""
        for s in err_substrs:
            assert s in captured.err

    def test_validate_main_schema_override_missing(
        self,
        capsys: pytest.CaptureFixture[str],
        tmp_path: Path,
    ) -> None:
        missing = tmp_path / "no-such-schema.yaml"
        code = validate_main([VALID, "--schema", str(missing), "--root", str(tmp_path)])
        captured = capsys.readouterr()
        assert code == ExitCode.FATAL
        assert "schema file not found" in captured.err
        assert str(missing) in captured.err

    # -- JSON output ---------------------------------------------------------

    @pytest.mark.parametrize(
        "args,exit_code,expect_errors",
        [
            (
                [VALID, INVALID, "--output-format", "json"],
                ExitCode.ERRORS,
                True,
            ),
            ([VALID, "--output-format", "json"], ExitCode.OK, False),
            (
                [VALID, "--schema", SCHEMA, "--output-format", "json"],
                ExitCode.OK,
                False,
            ),
        ],
    )
    def test_validate_main_json(
        self,
        capsys: pytest.CaptureFixture[str],
        args: list[str],
        exit_code: ExitCode,
        expect_errors: bool,
        tmp_path: Path,
    ) -> None:
        code = validate_main([*args, "--root", str(tmp_path)])
        captured = capsys.readouterr()
        assert code == exit_code
        payload = json.loads(captured.out)
        if expect_errors:
            assert payload["errors"]
        else:
            assert payload["errors"] == []

    def test_validate_main_json_missing_file(
        self,
        capsys: pytest.CaptureFixture[str],
        tmp_path: Path,
    ) -> None:
        code = validate_main(
            ["does-not-exist.yaml", "--output-format", "json", "--root", str(tmp_path)]
        )
        captured = capsys.readouterr()
        assert code == ExitCode.FATAL
        assert "file not found" in captured.err

    def test_validate_main_json_schema_missing(
        self,
        capsys: pytest.CaptureFixture[str],
        tmp_path: Path,
    ) -> None:
        missing = tmp_path / "no-such.yaml"
        code = validate_main(
            [
                VALID,
                "--schema",
                str(missing),
                "--output-format",
                "json",
                "--root",
                str(tmp_path),
            ],
        )
        captured = capsys.readouterr()
        assert code == ExitCode.FATAL
        assert "schema file not found" in captured.err

    def test_validate_main_json_schema_bad_yaml(
        self,
        capsys: pytest.CaptureFixture[str],
        tmp_path: Path,
    ) -> None:
        bad_schema = tmp_path / "bad-schema.yaml"
        bad_schema.write_text("key: [unclosed", encoding="utf-8")
        code = validate_main(
            [
                VALID,
                "--schema",
                str(bad_schema),
                "--output-format",
                "json",
                "--root",
                str(tmp_path),
            ],
        )
        captured = capsys.readouterr()
        assert code == ExitCode.FATAL
        assert "invalid YAML in schema" in captured.err


# ===================================================================
# validate_file  (Python API)
# ===================================================================


class TestValidateCoverage:
    """Tests for coverage checking in ``robotsix-modules validate``."""

    def test_validate_coverage_unclassified(
        self,
        capsys: pytest.CaptureFixture[str],
        git_repo: Path,
    ) -> None:
        """validate with a valid taxonomy in a git repo detects unclassified files."""
        (git_repo / "orphan.txt").touch()
        git_commit(git_repo, "orphan.txt")

        yaml_path = git_repo / "modules.yaml"
        yaml_path.write_text(
            "modules:\n"
            "  - id: example\n"
            "    description: x\n"
            "    paths:\n"
            "      - src/example/**\n",
            encoding="utf-8",
        )

        code = main(["validate", str(yaml_path), "--root", str(git_repo)])
        captured = capsys.readouterr()
        assert code == ExitCode.ERRORS
        assert "orphan.txt" in captured.err
        assert "not claimed" in captured.err.lower()

    def test_validate_coverage_all_covered(
        self,
        capsys: pytest.CaptureFixture[str],
        git_repo: Path,
    ) -> None:
        """validate with all tracked files covered → OK, no coverage errors."""
        (git_repo / "src" / "example").mkdir(parents=True)
        (git_repo / "src" / "example" / "app.py").touch()
        git_commit(git_repo, "src/example/app.py")

        yaml_path = git_repo / "modules.yaml"
        yaml_path.write_text(
            "modules:\n"
            "  - id: example\n"
            "    description: x\n"
            "    paths:\n"
            "      - src/example/**\n",
            encoding="utf-8",
        )

        code = main(["validate", str(yaml_path), "--root", str(git_repo)])
        captured = capsys.readouterr()
        assert code == ExitCode.OK, f"stderr: {captured.err}"

    def test_validate_coverage_default_globs_cover(
        self,
        capsys: pytest.CaptureFixture[str],
        git_repo: Path,
    ) -> None:
        """validate covers files via convention globs when package is set."""
        (git_repo / "src" / "pkg" / "core").mkdir(parents=True)
        (git_repo / "src" / "pkg" / "core" / "lib.py").touch()
        git_commit(git_repo, "src/pkg/core/lib.py")

        yaml_path = git_repo / "modules.yaml"
        yaml_path.write_text(
            "package: pkg\n"
            "modules:\n"
            "  - id: core\n"
            "    description: Fully conventional.\n",
            encoding="utf-8",
        )

        code = main(["validate", str(yaml_path), "--root", str(git_repo)])
        captured = capsys.readouterr()
        assert code == ExitCode.OK, f"stderr: {captured.err}"

    def test_validate_coverage_json_output(
        self,
        capsys: pytest.CaptureFixture[str],
        git_repo: Path,
    ) -> None:
        """validate --output-format json includes coverage errors."""
        (git_repo / "orphan.txt").touch()
        git_commit(git_repo, "orphan.txt")

        yaml_path = git_repo / "modules.yaml"
        yaml_path.write_text(
            "modules:\n"
            "  - id: example\n"
            "    description: x\n"
            "    paths:\n"
            "      - src/example/**\n",
            encoding="utf-8",
        )

        code = main(
            [
                "validate",
                str(yaml_path),
                "--root",
                str(git_repo),
                "--output-format",
                "json",
            ]
        )
        captured = capsys.readouterr()
        assert code == ExitCode.ERRORS
        payload = json.loads(captured.out)
        assert payload["errors"]
        assert any("orphan.txt" in e for e in payload["errors"])

    def test_validate_main_coverage_unclassified(
        self,
        capsys: pytest.CaptureFixture[str],
        git_repo: Path,
    ) -> None:
        """validate_main detects unclassified files via coverage check."""
        (git_repo / "orphan.txt").touch()
        git_commit(git_repo, "orphan.txt")

        yaml_path = git_repo / "modules.yaml"
        yaml_path.write_text(
            "modules:\n"
            "  - id: example\n"
            "    description: x\n"
            "    paths:\n"
            "      - src/example/**\n",
            encoding="utf-8",
        )

        code = validate_main([str(yaml_path), "--root", str(git_repo)])
        captured = capsys.readouterr()
        assert code == ExitCode.ERRORS
        assert "orphan.txt" in captured.err


class TestValidateFile:
    """Tests for the ``validate_file`` Python API."""

    def test_valid_no_schema(self) -> None:
        assert validate_file(VALID) == []

    def test_valid_schema_override(self) -> None:
        assert validate_file(VALID, schema_path=SCHEMA) == []

    def test_invalid_names_pointer(self) -> None:
        errors = validate_file(INVALID)
        assert errors
        assert any("modules[0]" in message for message in errors)
