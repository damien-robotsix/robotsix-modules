# robotsix-modules

Shared JSON-Schema-driven module-taxonomy validation for robotsix projects.

## Overview

`robotsix-modules` provides a consistent way to define, validate, and
check module taxonomies across the robotsix ecosystem. It bundles a
JSON Schema (`modules.schema.yaml`) that describes the expected
structure of a module taxonomy file and exposes a public API for
loading, validating, and auditing taxonomy files.

## Quick start

```python
from robotsix_modules import load_taxonomy, validate

taxonomy = load_taxonomy("modules.yaml")
errors = validate(taxonomy)
if errors:
    for e in errors:
        print(e)
```

## Public API

- **`load_taxonomy(path)`** — load a taxonomy YAML file
- **`validate(taxonomy)`** — validate a taxonomy dict against the schema
- **`validate_file(path)`** — load and validate a taxonomy file in one step
- **`check_registration(taxonomy, repo_root)`** — check that every module
  has a registered path and every registered file belongs to a module
- **`validate_paths(taxonomy, repo_root)`** — check that module paths
  resolve to real files

See the [API Reference](api.md) for full details.
