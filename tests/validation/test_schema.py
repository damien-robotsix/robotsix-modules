"""Tests for the bundled schema and the validation API."""

from __future__ import annotations

from robotsix_yaml_config import read_yaml_file

from robotsix_modules import SCHEMA_PATH, validate
from robotsix_modules.validation.schema import load_schema


def test_schema_path_resolves_and_is_readable() -> None:
    assert SCHEMA_PATH.is_file()
    assert SCHEMA_PATH.read_text(encoding="utf-8").strip()


def test_bundled_schema_parses_and_has_expected_keys() -> None:
    schema = read_yaml_file(SCHEMA_PATH)
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["$id"] == (
        "https://robotsix.github.io/modules/schemas/modules.schema.yaml"
    )
    module = schema["$defs"]["module"]
    for field in ("id", "description", "paths", "dependencies"):
        assert field in module["properties"]


def test_load_schema_matches_path_contents() -> None:
    assert load_schema()["title"] == "Module Taxonomy Schema"


def test_empty_dict_reports_missing_modules() -> None:
    errors = validate({})
    assert errors
    assert any("required property" in e and "modules" in e for e in errors)


def test_valid_taxonomy_returns_empty_list() -> None:
    taxonomy = {
        "modules": [{"id": "foo", "description": "bar", "paths": ["src/foo.py"]}]
    }
    assert validate(taxonomy) == []


def test_bad_id_mentions_kebab_pattern() -> None:
    taxonomy = {
        "modules": [{"id": "BadId", "description": "bar", "paths": ["src/foo.py"]}]
    }
    errors = validate(taxonomy)
    assert errors
    assert any("[a-z]" in e for e in errors)


def test_empty_paths_and_missing_paths_valid() -> None:
    """Empty paths list and missing paths key are both valid now."""
    # Module with empty paths list
    taxonomy = {"modules": [{"id": "foo", "description": "bar", "paths": []}]}
    assert validate(taxonomy) == []
    # Module without paths key at all
    taxonomy_no_paths = {"modules": [{"id": "foo", "description": "bar"}]}
    assert validate(taxonomy_no_paths) == []


def test_package_field_valid() -> None:
    """package field with valid value produces no schema errors."""
    taxonomy = {
        "package": "my_pkg",
        "modules": [{"id": "x", "description": "y"}],
    }
    assert validate(taxonomy) == []


def test_paths_optional() -> None:
    """Module without paths key produces no schema errors."""
    taxonomy = {"modules": [{"id": "x", "description": "y"}]}
    assert validate(taxonomy) == []


def test_paths_empty_list_valid() -> None:
    """paths: [] produces no schema errors (was previously invalid)."""
    taxonomy = {"modules": [{"id": "x", "description": "y", "paths": []}]}
    assert validate(taxonomy) == []


def test_package_pattern_invalid() -> None:
    """package with uppercase/hyphens produces a schema error."""
    taxonomy = {
        "package": "My-Pkg",
        "modules": [{"id": "x", "description": "y"}],
    }
    errors = validate(taxonomy)
    assert errors
    assert any("package" in e.lower() for e in errors)
