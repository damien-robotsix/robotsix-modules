# Schema Reference

The module taxonomy file (`modules.yaml`) is the single source of truth
for what logical modules exist in a robotsix project and where their
files live. This page documents the structure that every
`modules.yaml` must follow.

## Top-level structure

The file must be a YAML object with a single required key:

| Key       | Type  | Required | Description                            |
|-----------|-------|----------|----------------------------------------|
| `modules` | array | yes      | Ordered list of module entries.        |

No other top-level keys are permitted (`additionalProperties: false`).

**Minimal skeleton:**

```yaml
modules: []
```

## Module entry

Each element in the `modules` array is an object with the following
fields. No additional fields are permitted.

### `id`

- **Type:** string
- **Required:** yes
- **Pattern:** `^[a-z][a-z0-9]*(-[a-z0-9]+)*$`

A stable **kebab-case** identifier. Must start with a lowercase letter,
contain only lowercase alphanumerics and hyphens, and must not start or
end with a hyphen or contain consecutive hyphens.

**Valid examples:** `validation`, `cli`, `ci-fix`, `test-gap`

**Invalid examples:** `Validation`, `_private`, `-dash`, `dash-`,
`two--hyphens`, `123numeric`

### `description`

- **Type:** string
- **Required:** yes

One paragraph explaining what the module does and why it exists. Keep
it concise — one to three sentences.

### `paths`

- **Type:** array of strings
- **Required:** yes
- **Minimum items:** 1

Repo-relative glob patterns covering all source files, tests, docs,
agent definitions, config snippets, and skills that belong to the
module. Patterns use standard glob syntax (`*`, `**`, `?`).

Every file in the repo should be claimed by exactly one module (this
constraint is validated by `check_registration`).

### `dependencies`

- **Type:** array of strings
- **Required:** no
- **Default:** `[]`

Other module `id` values that this module consumes (imports, reads, or
otherwise depends on). Each dependency ID must satisfy the same
kebab-case pattern as `id`.

Documentation-only for v1; no enforcement is implemented. Omit or use
`[]` when a module has no internal dependencies.

## Complete example

Below is the taxonomy file that `robotsix-modules` uses for its own
source tree — three modules (`validation`, `cli`, `tests`) with one
dependency (the CLI depends on `validation`):

```yaml
# Module taxonomy for robotsix-modules itself.
# Validate with:  robotsix-modules validate docs/modules.yaml
modules:
  - id: validation
    description: >
      Core module-taxonomy validation logic. Provides the public API
      (load_taxonomy, validate, validate_file), the
      registration-completeness and path-resolution checks
      (check_registration, validate_paths), the bundled JSON Schema
      (modules.schema.yaml), and schema-loading utilities.
    paths:
      - src/robotsix_modules/__init__.py
      - src/robotsix_modules/py.typed
      - src/robotsix_modules/validation/**
      - docs/validation/**

  - id: cli
    description: >
      Command-line interface for robotsix-modules. Provides the
      `robotsix-modules` and `robotsix-modules-validate` entry points.
    paths:
      - src/robotsix_modules/cli/**
    dependencies:
      - validation

  - id: tests
    description: >
      Test suite covering the validation API, schema, CLI behaviour,
      and shared test fixtures.
    paths:
      - tests/**
```

## Validation

To check that a taxonomy file conforms to this schema:

```bash
robotsix-modules validate path/to/modules.yaml
```

Or in Python:

```python
from robotsix_modules import validate_file

errors = validate_file("path/to/modules.yaml")
if errors:
    for e in errors:
        print(e)
```
