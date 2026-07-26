"""Tests for ``robotsix-modules validate-paths``."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from robotsix_modules.cli import main
from robotsix_modules.cli._exit_codes import ExitCode


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
