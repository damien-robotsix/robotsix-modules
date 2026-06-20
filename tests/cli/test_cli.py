"""Tests for the robotsix-modules CLI entry points."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
from conftest import git_commit

from robotsix_modules import SCHEMA_PATH, __version__, validate_file
from robotsix_modules.cli import main, validate_main

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
            (["validate", VALID], 0, [], True, True),
            (["validate", INVALID], 1, ["modules[0]", "modules[1]"], True, False),
            (
                ["validate", "does-not-exist.yaml"],
                2,
                ["file not found", "does-not-exist.yaml"],
                False,
                False,
            ),
            (["validate", VALID, "--schema", SCHEMA], 0, [], False, True),
            (["validate", VALID, "-v"], 0, ["INFO:", "loading"], False, False),
            (["validate", VALID, "-vv"], 0, ["DEBUG:", "loaded"], False, False),
        ],
    )
    def test_validate(
        self,
        capsys: pytest.CaptureFixture[str],
        args: list[str],
        exit_code: int,
        err_substrs: list[str],
        out_empty: bool,
        err_empty: bool,
    ) -> None:
        code = main(args)
        captured = capsys.readouterr()
        assert code == exit_code
        if out_empty:
            assert captured.out == ""
        if err_empty:
            assert captured.err == ""
        for s in err_substrs:
            assert s in captured.err

    def test_invalid_taxonomy_yaml_exit_two(
        self,
        capsys: pytest.CaptureFixture[str],
        tmp_path: Path,
    ) -> None:
        bad = tmp_path / "broken.yaml"
        bad.write_text("key: [unclosed", encoding="utf-8")
        code = main(["validate", str(bad)])
        captured = capsys.readouterr()
        assert code == 2
        assert "invalid YAML" in captured.err
        assert str(bad) in captured.err

    def test_missing_schema_file_exit_two(
        self,
        capsys: pytest.CaptureFixture[str],
        tmp_path: Path,
    ) -> None:
        missing = tmp_path / "no-such-schema.yaml"
        code = main(["validate", VALID, "--schema", str(missing)])
        captured = capsys.readouterr()
        assert code == 2
        assert "schema file not found" in captured.err
        assert str(missing) in captured.err

    def test_invalid_schema_yaml_exit_two(
        self,
        capsys: pytest.CaptureFixture[str],
        tmp_path: Path,
    ) -> None:
        bad_schema = tmp_path / "broken-schema.yaml"
        bad_schema.write_text("key: [unclosed", encoding="utf-8")
        code = main(["validate", VALID, "--schema", str(bad_schema)])
        captured = capsys.readouterr()
        assert code == 2
        assert "invalid YAML in schema" in captured.err
        assert str(bad_schema) in captured.err

    # -- JSON output ---------------------------------------------------------

    @pytest.mark.parametrize(
        "file_path,exit_code,expect_errors",
        [(INVALID, 1, True), (VALID, 0, False)],
    )
    def test_validate_json(
        self,
        capsys: pytest.CaptureFixture[str],
        file_path: str,
        exit_code: int,
        expect_errors: bool,
    ) -> None:
        code = main(["validate", file_path, "--output-format", "json"])
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
    ) -> None:
        code = main(["validate", "does-not-exist.yaml", "--output-format", "json"])
        captured = capsys.readouterr()
        assert code == 2
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
            ([VALID, INVALID], 1, ["modules[0]"], False),
            ([VALID], 0, [], True),
            ([VALID, "--schema", SCHEMA], 0, [], True),
        ],
    )
    def test_validate_main(
        self,
        capsys: pytest.CaptureFixture[str],
        args: list[str],
        exit_code: int,
        err_substrs: list[str],
        err_empty: bool,
    ) -> None:
        code = validate_main(args)
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
        code = validate_main([VALID, "--schema", str(missing)])
        captured = capsys.readouterr()
        assert code == 2
        assert "schema file not found" in captured.err
        assert str(missing) in captured.err

    # -- JSON output ---------------------------------------------------------

    @pytest.mark.parametrize(
        "args,exit_code,expect_errors",
        [
            ([VALID, INVALID, "--output-format", "json"], 1, True),
            ([VALID, "--output-format", "json"], 0, False),
        ],
    )
    def test_validate_main_json(
        self,
        capsys: pytest.CaptureFixture[str],
        args: list[str],
        exit_code: int,
        expect_errors: bool,
    ) -> None:
        code = validate_main(args)
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
    ) -> None:
        code = validate_main(["does-not-exist.yaml", "--output-format", "json"])
        captured = capsys.readouterr()
        assert code == 2
        assert "file not found" in captured.err

    def test_validate_main_json_schema_missing(
        self,
        capsys: pytest.CaptureFixture[str],
        tmp_path: Path,
    ) -> None:
        missing = tmp_path / "no-such.yaml"
        code = validate_main(
            [VALID, "--schema", str(missing), "--output-format", "json"],
        )
        captured = capsys.readouterr()
        assert code == 2
        assert "schema file not found" in captured.err

    def test_validate_main_json_schema_bad_yaml(
        self,
        capsys: pytest.CaptureFixture[str],
        tmp_path: Path,
    ) -> None:
        bad_schema = tmp_path / "bad-schema.yaml"
        bad_schema.write_text("key: [unclosed", encoding="utf-8")
        code = validate_main(
            [VALID, "--schema", str(bad_schema), "--output-format", "json"],
        )
        captured = capsys.readouterr()
        assert code == 2
        assert "invalid YAML in schema" in captured.err


# ===================================================================
# validate_file  (Python API)
# ===================================================================


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
            (["src/example/app.py"], ["src/example/app.py"], 0, [], True),
            (["orphan.txt"], ["orphan.txt"], 1, ["orphan.txt", "not claimed"], False),
        ],
    )
    def test_check_registration_git(
        self,
        capsys: pytest.CaptureFixture[str],
        git_repo: Path,
        files_to_create: list[str],
        files_to_commit: list[str],
        exit_code: int,
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

    def test_check_registration_missing_file_exit_two(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        code = main(["check-registration", "does-not-exist.yaml"])
        captured = capsys.readouterr()
        assert code == 2
        assert "file not found" in captured.err

    def test_check_registration_invalid_yaml_exit_two(
        self,
        capsys: pytest.CaptureFixture[str],
        tmp_path: Path,
    ) -> None:
        bad = tmp_path / "broken.yaml"
        bad.write_text("key: [unclosed", encoding="utf-8")
        code = main(["check-registration", str(bad)])
        captured = capsys.readouterr()
        assert code == 2
        assert "invalid YAML" in captured.err

    def test_check_registration_root_flag_respected(
        self,
        capsys: pytest.CaptureFixture[str],
        tmp_path: Path,
    ) -> None:
        root = tmp_path / "myroot"
        root.mkdir()
        (root / "src").mkdir()
        (root / "src" / "lib.py").touch()

        yaml_path = tmp_path / "modules.yaml"
        yaml_path.write_text(
            "modules:\n"
            "  - id: lib\n"
            "    description: x\n"
            "    paths:\n"
            "      - src/lib.py\n",
            encoding="utf-8",
        )

        subprocess.run(["git", "init"], cwd=root, capture_output=True, check=True)
        git_commit(root, "src/lib.py")

        code = main(
            ["check-registration", str(yaml_path), "--root", str(root)],
        )
        captured = capsys.readouterr()
        assert code == 0, f"stderr: {captured.err}"

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
        assert code == 2
        assert "git ls-files failed" in captured.err

    # -- JSON output ---------------------------------------------------------

    @pytest.mark.parametrize(
        "files_to_create,files_to_commit,exit_code,expect_findings",
        [
            (["src/example/app.py"], ["src/example/app.py"], 0, False),
            (["orphan.txt"], ["orphan.txt"], 1, True),
        ],
    )
    def test_check_registration_json(
        self,
        capsys: pytest.CaptureFixture[str],
        git_repo: Path,
        files_to_create: list[str],
        files_to_commit: list[str],
        exit_code: int,
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
            assert finding["kind"] == "unclassified_file"
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
                0,
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
                1,
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
        exit_code: int,
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

    def test_validate_paths_missing_file_exit_two(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        code = main(["validate-paths", "does-not-exist.yaml"])
        captured = capsys.readouterr()
        assert code == 2
        assert "file not found" in captured.err

    def test_validate_paths_invalid_yaml_exit_two(
        self,
        capsys: pytest.CaptureFixture[str],
        tmp_path: Path,
    ) -> None:
        bad = tmp_path / "broken.yaml"
        bad.write_text("key: [unclosed", encoding="utf-8")
        code = main(["validate-paths", str(bad)])
        captured = capsys.readouterr()
        assert code == 2
        assert "invalid YAML" in captured.err

    def test_validate_paths_root_flag_respected(
        self,
        capsys: pytest.CaptureFixture[str],
        tmp_path: Path,
    ) -> None:
        root = tmp_path / "myroot"
        root.mkdir()
        (root / "src").mkdir()
        (root / "src" / "lib.py").touch()

        yaml_path = tmp_path / "modules.yaml"
        yaml_path.write_text(
            "modules:\n"
            "  - id: lib\n"
            "    description: x\n"
            "    paths:\n"
            "      - src/lib.py\n",
            encoding="utf-8",
        )

        code = main(
            ["validate-paths", str(yaml_path), "--root", str(root)],
        )
        captured = capsys.readouterr()
        assert code == 0, f"stderr: {captured.err}"

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
        assert code == 1
        assert captured.err == ""
        payload = json.loads(captured.out)
        assert payload["findings"]
        finding = payload["findings"][0]
        assert "kind" in finding
        assert finding["module_id"] == "example"
        assert finding["path"] == "src/missing.py"
