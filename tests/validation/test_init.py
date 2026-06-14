"""Unit tests for the public API functions in robotsix_modules.__init__."""

from __future__ import annotations

from pathlib import Path

import pytest
from robotsix_yaml_config import YamlParseError, YamlReadError

from robotsix_modules import load_taxonomy


def test_load_taxonomy_valid(tmp_path: Path) -> None:
    valid = tmp_path / "valid.yaml"
    valid.write_text("modules: []", encoding="utf-8")
    result = load_taxonomy(valid)
    assert result == {"modules": []}


def test_load_taxonomy_not_found() -> None:
    with pytest.raises(YamlReadError):
        load_taxonomy("does-not-exist.yaml")


def test_load_taxonomy_invalid_yaml(tmp_path: Path) -> None:
    broken = tmp_path / "broken.yaml"
    broken.write_text("key: [unclosed", encoding="utf-8")
    with pytest.raises(YamlParseError):
        load_taxonomy(broken)
