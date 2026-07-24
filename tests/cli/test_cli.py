"""Tests for the robotsix-modules CLI entry points."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pytest
from conftest import (
    git_commit,
    run_invalid_yaml_test,
    run_missing_file_test,
    run_root_flag_respected_test,
)

from robotsix_modules import SCHEMA_PATH, __version__, validate_file
from robotsix_modules.cli import main, validate_main
from robotsix_modules.cli._exit_codes import ExitCode
from robotsix_modules.validation import FindingKind

FIXTURES = Path(__file__).parent / "fixtures"
VALID = str(FIXTURES / "valid_modules.yaml")
INVALID = str(FIXTURES / "invalid_modules.yaml")
SCHEMA = str(SCHEMA_PATH)


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


# ===================================================================
# check-registration
# ===================================================================


class TestCheckRegistration:
    """Tests for ``robotsix-modules check-registration``."""

    _YAML_VALID = (
        "modules:\n"
        "  - id: example\n"
        "    description: x\n"
        "    paths:\n"
        "      - src/example/**\n"
    )

    @staticmethod
    def _setup_git_repo(
        git_repo: Path,
        *,
        yaml_body: str,
        files_to_create: list[str],
        files_to_commit: list[str],
    ) -> Path:
        """Create files, write modules.yaml, stage+commit, return yaml path."""
        for f in files_to_create:
            p = git_repo / f
            p.parent.mkdir(parents=True, exist_ok=True)
            p.touch()
        yaml_path = git_repo / "modules.yaml"
        yaml_path.write_text(yaml_body, encoding="utf-8")
        if files_to_commit:
            git_commit(git_repo, *files_to_commit)
        return yaml_path

    # -- text output ---------------------------------------------------------

    @pytest.mark.parametrize(
        "files_to_create,files_to_commit,exit_code,err_substrs,out_empty",
        [
            (["src/example/app.py"], ["src/example/app.py"], ExitCode.OK, [], True),
            (
                ["orphan.txt"],
                ["orphan.txt"],
                ExitCode.ERRORS,
                ["orphan.txt", "not claimed"],
                False,
            ),
        ],
    )
    def test_check_registration_git(
        self,
        capsys: pytest.CaptureFixture[str],
        git_repo: Path,
        files_to_create: list[str],
        files_to_commit: list[str],
        exit_code: ExitCode,
        err_substrs: list[str],
        out_empty: bool,
    ) -> None:
        yaml_path = self._setup_git_repo(
            git_repo,
            yaml_body=self._YAML_VALID,
            files_to_create=files_to_create,
            files_to_commit=files_to_commit,
        )
        code = main(
            ["check-registration", str(yaml_path), "--root", str(git_repo)],
        )
        captured = capsys.readouterr()
        assert code == exit_code, f"stderr: {captured.err}"
        if out_empty:
            assert captured.out == ""
        lower_err = captured.err.lower()
        for s in err_substrs:
            assert s in lower_err

    def test_check_registration_non_git_root_exit_two(
        self,
        capsys: pytest.CaptureFixture[str],
        tmp_path: Path,
    ) -> None:
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

        code = main(
            ["check-registration", str(yaml_path), "--root", str(tmp_path)],
        )
        captured = capsys.readouterr()
        assert code == ExitCode.FATAL
        assert "git ls-files failed" in captured.err

    # -- JSON output ---------------------------------------------------------

    @pytest.mark.parametrize(
        "files_to_create,files_to_commit,exit_code,expect_findings",
        [
            (["src/example/app.py"], ["src/example/app.py"], ExitCode.OK, False),
            (["orphan.txt"], ["orphan.txt"], ExitCode.ERRORS, True),
        ],
    )
    def test_check_registration_json(
        self,
        capsys: pytest.CaptureFixture[str],
        git_repo: Path,
        files_to_create: list[str],
        files_to_commit: list[str],
        exit_code: ExitCode,
        expect_findings: bool,
    ) -> None:
        yaml_path = self._setup_git_repo(
            git_repo,
            yaml_body=self._YAML_VALID,
            files_to_create=files_to_create,
            files_to_commit=files_to_commit,
        )
        code = main(
            [
                "check-registration",
                str(yaml_path),
                "--root",
                str(git_repo),
                "--output-format",
                "json",
            ],
        )
        captured = capsys.readouterr()
        assert code == exit_code
        assert captured.err == ""
        payload = json.loads(captured.out)
        if expect_findings:
            assert payload["findings"]
            finding = payload["findings"][0]
            assert finding["kind"] == FindingKind.UNCLASSIFIED_FILE
            assert "message" in finding
            assert finding["file"] == "orphan.txt"
        else:
            assert payload == {"findings": []}


# ===================================================================
# validate-paths
# ===================================================================


class TestValidatePaths:
    """Tests for ``robotsix-modules validate-paths``."""

    # -- text output ---------------------------------------------------------

    @pytest.mark.parametrize(
        "create_file,yaml_body,exit_code,err_substrs,out_empty",
        [
            (
                "src/app.py",
                "modules:\n"
                "  - id: example\n"
                "    description: x\n"
                "    paths:\n"
                "      - src/app.py\n",
                ExitCode.OK,
                [],
                True,
            ),
            (
                None,
                "modules:\n"
                "  - id: example\n"
                "    description: x\n"
                "    paths:\n"
                "      - src/missing.py\n",
                ExitCode.ERRORS,
                ["does not exist", "src/missing.py"],
                False,
            ),
        ],
    )
    def test_validate_paths(
        self,
        capsys: pytest.CaptureFixture[str],
        tmp_path: Path,
        create_file: str | None,
        yaml_body: str,
        exit_code: ExitCode,
        err_substrs: list[str],
        out_empty: bool,
    ) -> None:
        if create_file is not None:
            p = tmp_path / create_file
            p.parent.mkdir(parents=True, exist_ok=True)
            p.touch()

        yaml_path = tmp_path / "modules.yaml"
        yaml_path.write_text(yaml_body, encoding="utf-8")

        code = main(
            ["validate-paths", str(yaml_path), "--root", str(tmp_path)],
        )
        captured = capsys.readouterr()
        assert code == exit_code, f"stderr: {captured.err}"
        if out_empty:
            assert captured.out == ""
        lower_err = captured.err.lower()
        for s in err_substrs:
            assert s in lower_err

    # -- JSON output ---------------------------------------------------------

    def test_validate_paths_json_findings(
        self,
        capsys: pytest.CaptureFixture[str],
        tmp_path: Path,
    ) -> None:
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
            ],
        )
        captured = capsys.readouterr()
        assert code == ExitCode.ERRORS
        assert captured.err == ""
        payload = json.loads(captured.out)
        assert payload["findings"]
        finding = payload["findings"][0]
        assert "kind" in finding
        assert finding["module_id"] == "example"
        assert finding["path"] == "src/missing.py"


# ===================================================================
# migrate
# ===================================================================


class TestMigrate:
    """Tests for ``robotsix-modules migrate``."""

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _write_yaml(
        tmp_path: Path,
        body: Mapping[str, Any],
        *,
        filename: str = "modules.yaml",
    ) -> Path:
        import yaml

        p = tmp_path / filename
        p.write_text(
            yaml.dump(body, default_flow_style=False, sort_keys=False),
            encoding="utf-8",
        )
        return p

    @staticmethod
    def _load_yaml(path: str | Path) -> Any:
        import yaml

        return yaml.safe_load(Path(path).read_text(encoding="utf-8"))

    # ------------------------------------------------------------------
    # sentinels for parametrized path assertions
    # ------------------------------------------------------------------

    _PATHS_ABSENT = object()
    _UNCHANGED = object()

    # ------------------------------------------------------------------
    # parametrized stdout tests (was 4 separate copy-pasted methods)
    # ------------------------------------------------------------------

    @pytest.mark.parametrize(
        ("taxonomy", "expected_paths", "expected_stderr"),
        [
            # Strips default paths, keeps non-default.
            (
                {
                    "package": "example_pkg",
                    "modules": [
                        {
                            "id": "core",
                            "description": "Core module.",
                            "paths": [
                                "src/example_pkg/core/**",
                                "tests/core/**",
                                "docs/core/**",
                                "legacy/old.py",
                            ],
                        },
                    ],
                },
                ["legacy/old.py"],
                None,
            ),
            # Fully conventional module — paths key dropped entirely.
            (
                {
                    "package": "pkg",
                    "modules": [
                        {
                            "id": "sub",
                            "description": "Sub module.",
                            "paths": [
                                "src/pkg/sub/**",
                                "tests/sub/**",
                                "docs/sub/**",
                            ],
                        },
                    ],
                },
                _PATHS_ABSENT,
                None,
            ),
            # No package key — warning + unchanged stdout.
            (
                {
                    "modules": [
                        {
                            "id": "core",
                            "description": "Core.",
                            "paths": ["src/pkg/core/**"],
                        },
                    ],
                },
                _UNCHANGED,
                "nothing to migrate",
            ),
            # Preserves non-default paths.
            (
                {
                    "package": "example_pkg",
                    "modules": [
                        {
                            "id": "core",
                            "description": "Core.",
                            "paths": [
                                "src/example_pkg/core/**",
                                "src/example_pkg/core/extra.py",
                            ],
                        },
                    ],
                },
                ["src/example_pkg/core/extra.py"],
                None,
            ),
        ],
    )
    def test_migrate_stdout(
        self,
        capsys: pytest.CaptureFixture[str],
        tmp_path: Path,
        taxonomy: dict[str, Any],
        expected_paths: object,
        expected_stderr: str | None,
    ) -> None:
        p = self._write_yaml(tmp_path, taxonomy)
        code = main(["migrate", str(p)])
        captured = capsys.readouterr()
        assert code == ExitCode.OK

        import yaml

        result = yaml.safe_load(captured.out)

        if expected_paths is self._UNCHANGED:
            assert result == taxonomy
        elif expected_paths is self._PATHS_ABSENT:
            assert "paths" not in result["modules"][0]
        else:
            assert result["modules"][0]["paths"] == expected_paths

        if expected_stderr is not None:
            assert expected_stderr in captured.err

    # ------------------------------------------------------------------
    # parametrized --in-place test
    # ------------------------------------------------------------------

    @pytest.mark.parametrize(
        ("taxonomy", "expected_paths", "expected_stderr"),
        [
            (
                {
                    "package": "pkg",
                    "modules": [
                        {
                            "id": "core",
                            "description": "Core.",
                            "paths": [
                                "src/pkg/core/**",
                                "tests/core/**",
                                "docs/core/**",
                                "custom/extra.py",
                            ],
                        },
                    ],
                },
                ["custom/extra.py"],
                "Wrote simplified taxonomy",
            ),
        ],
    )
    def test_migrate_in_place(
        self,
        capsys: pytest.CaptureFixture[str],
        tmp_path: Path,
        taxonomy: dict[str, Any],
        expected_paths: list[str],
        expected_stderr: str,
    ) -> None:
        p = self._write_yaml(tmp_path, taxonomy)
        code = main(["migrate", str(p), "--in-place"])
        captured = capsys.readouterr()
        assert code == ExitCode.OK
        assert expected_stderr in captured.err

        result = self._load_yaml(p)
        assert result["modules"][0]["paths"] == expected_paths

    # ------------------------------------------------------------------
    # error-path test (structurally different — no YAML file written)
    # ------------------------------------------------------------------

    def test_migrate_missing_file_exits_two(
        self,
        capsys: pytest.CaptureFixture[str],
        tmp_path: Path,
    ) -> None:
        missing = tmp_path / "nonexistent.yaml"
        code = main(["migrate", str(missing)])
        captured = capsys.readouterr()
        assert code == ExitCode.FATAL
        assert "file not found" in captured.err


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
