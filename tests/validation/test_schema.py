"""Tests for the bundled schema and the validation API."""

from __future__ import annotations

from pathlib import Path

from robotsix_modules import SCHEMA_PATH, validate
from robotsix_modules._yaml import read_yaml_file
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


def test_schema_reference_doc_matches_schema() -> None:
    """Every schema field and constraint is documented in schema-reference.md."""
    schema = load_schema()
    doc_path = (
        Path(__file__).resolve().parent.parent.parent / "docs" / "schema-reference.md"
    )
    doc = doc_path.read_text(encoding="utf-8")

    # ── Collect all schema field names ──────────────────────────────────
    top_props: dict[str, dict] = schema["properties"]
    module_props: dict[str, dict] = schema["$defs"]["module"]["properties"]
    top_required: list[str] = schema.get("required", [])
    module_required: list[str] = schema["$defs"]["module"].get("required", [])

    # ── 1. Every schema property appears in the doc ─────────────────────
    for field in top_props:
        assert _field_in_doc(field, doc), (
            f"Schema top-level field '{field}' is not documented in "
            f"docs/schema-reference.md. Add it to keep the doc "
            f"in sync with modules.schema.yaml."
        )

    for field in module_props:
        assert _field_in_doc(field, doc), (
            f"Schema module field '{field}' is not documented in "
            f"docs/schema-reference.md. Add it to keep the doc "
            f"in sync with modules.schema.yaml."
        )

    # ── 2. additionalProperties: false is documented ────────────────────
    assert schema.get("additionalProperties") is False
    assert (
        "additionalProperties: false" in doc
        or "no other top-level keys are permitted" in doc.lower()
    ), (
        "Schema-reference doc should note that no extra top-level keys "
        "are permitted at the top level (additionalProperties: false)."
    )

    assert schema["$defs"]["module"].get("additionalProperties") is False
    assert (
        "no additional fields" in doc.lower() or "additionalproperties" in doc.lower()
    ), (
        "Schema-reference doc should note that no additional fields are "
        "permitted on module entries (additionalProperties: false)."
    )

    # ── 3. Required fields are marked as required ───────────────────────
    for req in module_required:
        assert _required_in_doc(req, doc), (
            f"Schema module field '{req}' is required but not marked "
            f"as required in docs/schema-reference.md."
        )

    for req in top_required:
        assert _required_in_doc(req, doc), (
            f"Schema top-level field '{req}' is required but not marked "
            f"as required in docs/schema-reference.md."
        )

    # ── 4. Patterns are documented ──────────────────────────────────────
    for field, prop in {**top_props, **module_props}.items():
        pat = prop.get("pattern")
        if pat is not None:
            assert pat in doc or _pattern_described(field, doc), (
                f"Schema field '{field}' has pattern '{pat}' that is "
                f"not documented in docs/schema-reference.md. "
                f"Add the pattern or a description of the naming rules."
            )

    # ── 5. No stale doc references to removed fields ────────────────────
    all_schema_fields = set(top_props) | set(module_props)
    _assert_no_stale_fields(doc, all_schema_fields)


# ── Helpers ─────────────────────────────────────────────────────────────


def _field_in_doc(field: str, doc: str) -> bool:
    """Return True if *field* appears as a documented heading or type row."""
    # The doc uses `### \`id\`` style headings and `| \`id\` |` table rows.
    return f"`{field}`" in doc


def _required_in_doc(field: str, doc: str) -> bool:
    """Return True if *field* is marked required near its doc mention."""
    import re

    # Pattern 1: Table row — e.g. | `modules` | array  | yes      | ... |
    table_row = re.search(
        rf"^\|\s*`{re.escape(field)}`\s*\|.*?\|\s*(yes|no)\s*\|",
        doc,
        re.MULTILINE,
    )
    if table_row:
        return table_row.group(1) == "yes"

    # Pattern 2: Bullet list — e.g. - **Required:** yes
    idx = doc.find(f"`{field}`")
    if idx == -1:
        return False
    window = doc[max(0, idx - 500) : idx + 200]
    return bool(re.search(r"\*\*Required:\*\*\s*yes", window, re.IGNORECASE))


def _assert_no_stale_fields(doc: str, schema_fields: set[str]) -> None:
    """Assert no backtick-quoted field names in the doc are absent from the schema."""
    import re

    # Extract field names from doc headings and table rows only — these are
    # the documented field definitions, not mere example values.
    doc_fields: set[str] = set()

    # ### `id` style headings
    doc_fields.update(re.findall(r"###\s+`([a-z][a-z0-9_-]*)`", doc))

    # | `package` | string | ... table rows
    doc_fields.update(re.findall(r"^\|\s*`([a-z][a-z0-9_-]*)`\s*\|", doc, re.MULTILINE))

    # - **Type:** ... after a heading (field name inferred from preceding heading)
    # Already captured by the heading regex above.

    stale = doc_fields - schema_fields
    assert not stale, (
        f"docs/schema-reference.md documents field(s) {sorted(stale)} "
        f"that are not present in the schema. Remove stale references "
        f"or add the missing schema definitions."
    )


def _pattern_described(field: str, doc: str) -> bool:
    """Return True if the doc describes a naming pattern near *field*."""
    import re

    idx = doc.find(f"`{field}`")
    if idx == -1:
        return False
    window = doc[max(0, idx - 50) : idx + 300]
    return bool(
        re.search(r"pattern", window, re.IGNORECASE)
        or re.search(r"kebab-case", window, re.IGNORECASE)
        or re.search(r"underscore-separated", window, re.IGNORECASE)
        or re.search(r"naming rules", window, re.IGNORECASE)
        or re.search(r"\[a-z\]", window)
    )
