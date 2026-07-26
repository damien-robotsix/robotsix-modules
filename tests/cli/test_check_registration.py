"""Tests for ``robotsix-modules check-registration``."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from conftest import git_commit

from robotsix_modules.cli import main
from robotsix_modules.cli._exit_codes import ExitCode
from robotsix_modules.validation import FindingKind


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
