"""Tests for ``robotsix-modules migrate``."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pytest

from robotsix_modules.cli import main
from robotsix_modules.cli._exit_codes import ExitCode


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
