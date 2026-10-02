"""Tests for the centralized YAML I/O helpers in ``_yaml``."""

from __future__ import annotations

from pathlib import Path

import pytest

from robotsix_modules._yaml import (
    YamlWriteError,
    dump_yaml,
    read_yaml_file,
    write_yaml_file,
)


def test_dump_yaml_preserves_key_order() -> None:
    """``sort_keys=False`` is centralized, so insertion order is kept."""
    data = {"package": "pkg", "modules": [], "zeta": 1, "alpha": 2}
    output = dump_yaml(data)
    assert output.index("package") < output.index("modules") < output.index("zeta")
    assert output.index("zeta") < output.index("alpha")


def test_dump_yaml_block_style_and_unicode() -> None:
    """Block style (not flow) and unicode pass-through are the defaults."""
    data = {"name": "café", "items": ["a", "b"]}
    output = dump_yaml(data)
    assert "café" in output  # allow_unicode=True — not escaped
    assert "{" not in output and "[" not in output  # default_flow_style=False


def test_dump_yaml_is_stable_round_trip(tmp_path: Path) -> None:
    """Serializing then parsing returns the original mapping."""
    data = {"package": "robotsix_modules", "modules": [{"id": "cli", "paths": None}]}
    path = tmp_path / "taxonomy.yaml"
    write_yaml_file(path, data)
    assert read_yaml_file(path) == data


def test_write_yaml_file_matches_dump_yaml(tmp_path: Path) -> None:
    """``write_yaml_file`` and ``dump_yaml`` produce identical serialization.

    This guards against in-place vs stdout migration output drifting apart.
    """
    data = {"package": "pkg", "modules": [{"id": "root"}]}
    path = tmp_path / "out.yaml"
    write_yaml_file(path, data)
    assert path.read_text(encoding="utf-8") == dump_yaml(data)


def test_write_yaml_file_raises_on_unwritable_path(tmp_path: Path) -> None:
    """A path that cannot be written raises ``YamlWriteError``."""
    missing_dir = tmp_path / "does-not-exist" / "out.yaml"
    with pytest.raises(YamlWriteError):
        write_yaml_file(missing_dir, {"package": "pkg"})
