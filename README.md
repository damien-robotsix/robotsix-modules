# robotsix-modules

[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/damien-robotsix/robotsix-modules/badge)](https://securityscorecards.dev/viewer/?uri=github.com/damien-robotsix/robotsix-modules)

Shared JSON-Schema-driven module-taxonomy validation for robotsix projects.

A *module taxonomy* is a structured inventory of the logical modules in a
repository — their descriptions, the file globs they own, and the dependency
relationships between them. It lives in a `docs/modules.yaml` file. This package
bundles the canonical JSON Schema (draft 2020-12) for that file and ships a
small CLI + Python API to validate it.

## Install

> **Note:** A plain `pip install robotsix-modules` from PyPI does **not**
> currently resolve. The runtime dependency `robotsix-yaml-config` is Git-only
> (not published to PyPI), and `pip` cannot fetch it from the published wheel
> metadata. Use one of the supported install paths below.

With `uv`, which resolves the `[tool.uv.sources]` Git entry:

```console
uv add "robotsix-modules @ git+https://github.com/damien-robotsix/robotsix-modules@v0.2.0"
```

With `pip`, using the git-URL form:

```console
pip install "robotsix-modules @ git+https://github.com/damien-robotsix/robotsix-modules@v0.2.0"
```

## CLI

The `robotsix-modules` CLI provides subcommands for validating module
taxonomies, checking registration completeness, and verifying path resolutions.
All subcommands support `--verbose`, `--output-format`, and standardised exit
codes (0 = valid, 1 = validation errors, 2 = file/parse errors).

```console
$ robotsix-modules validate docs/modules.yaml   # exit 0 when valid, empty output
$ robotsix-modules validate broken.yaml          # prints errors to stderr; exit 1
```

For the full CLI reference — including all subcommands, options, exit codes,
output formats, and pre-commit integration — see
[docs/cli/usage.md](docs/cli/usage.md).

## Python API

```python
from robotsix_modules import (
    validate, validate_file, load_taxonomy, SCHEMA_PATH,
    check_registration, validate_paths,
    RegistrationFinding, PathFinding,
)

errors = validate({"modules": [{"id": "foo", "description": "x", "paths": ["src/foo.py"]}]})
assert errors == []

errors = validate({})
assert errors  # ["modules: 'modules' is a required property"]

errors = validate_file("docs/modules.yaml")
```

```python
from pathlib import Path
from robotsix_modules import check_registration, validate_paths

taxonomy = load_taxonomy("docs/modules.yaml")
root = Path(".")

findings = check_registration(taxonomy, root)
for f in findings:
    print(f.kind, f.message)

findings = validate_paths(taxonomy, root)
for f in findings:
    print(f.kind, f.module_id, f.path, f.message)
```

```python
finding = RegistrationFinding(
    kind="unclassified_file",
    message="File 'src/orphan.py' is not claimed by any module",
    file="src/orphan.py",
)
```

- `load_taxonomy(path)` — load a `modules.yaml` and return a dict.
- `validate(taxonomy, *, schema=None)` — validate a dict; returns a list of
  human-readable error strings (empty = valid).
- `validate_file(path, *, schema_path=None)` — `load_taxonomy` then `validate`.
- `check_registration(taxonomy, repo_root, *, tracked_files=None)` — verify
  every tracked file is claimed by exactly one module. Returns a list of
  `RegistrationFinding` objects. Uses `git ls-files` by default; pass
  `tracked_files` to override.
- `validate_paths(taxonomy, repo_root)` — verify every module path entry
  resolves to at least one file on disk. Returns a list of `PathFinding`
  objects.
- `SCHEMA_PATH` — `pathlib.Path` to the bundled schema.

## License

MIT
