# robotsix-modules

Shared JSON-Schema-driven module-taxonomy validation for robotsix projects.

A *module taxonomy* is a structured inventory of the logical modules in a
repository — their descriptions, the file globs they own, and the
dependency relationships between them. It lives in a `docs/modules.yaml`
file. This package bundles the canonical JSON Schema (draft 2020-12) for
that file and ships a small CLI + Python API to validate it.

## Install

```console
pip install "robotsix-modules @ git+https://github.com/damien-robotsix/robotsix-modules@v0.2.0"
```

## CLI

```console
$ robotsix-modules validate docs/modules.yaml   # exit 0 when valid, empty output
$ robotsix-modules validate broken.yaml          # prints "<pointer>: <message>" lines to stderr; exit 1
$ robotsix-modules validate missing.yaml         # "robotsix-modules: error: file not found: ..."; exit 2
$ robotsix-modules --version                     # robotsix-modules 0.2.0
```

```console
$ robotsix-modules check-registration docs/modules.yaml
# exit 0 — every tracked file is claimed by exactly one module

$ robotsix-modules check-registration docs/modules.yaml --root /path/to/repo
# exit 1 — prints findings (unclassified files, stale paths, duplicates) to stderr

$ robotsix-modules validate-paths docs/modules.yaml
# exit 0 — every module path resolves to at least one file on disk

$ robotsix-modules validate-paths docs/modules.yaml --root .
# exit 1 — prints path_not_found / glob_empty findings to stderr
```

Exit codes: `0` = valid, `1` = validation errors, `2` = file/parse
errors. All diagnostics go to stderr; stdout stays empty on success.

Pass `--output-format {text,json}` to any subcommand (and the
`robotsix-modules-validate` wrapper). The default `text` preserves the
human-readable stderr behavior above. `json` writes a single JSON object
to stdout — `{"findings": [...]}` for `check-registration`/`validate-paths`
and `{"errors": [...]}` for `validate` — while operational errors stay on
stderr. Exit codes are identical in both modes.

```console
$ robotsix-modules check-registration docs/modules.yaml --output-format json
{"findings": []}
```

Pass `--schema <path>` to `validate` to override the bundled schema.

For `check-registration` and `validate-paths`, add `--root <dir>` to
specify the repository root (defaults to the current directory). Both
subcommands follow the same exit-code contract: 0 = no findings, 1 =
findings found, 2 = file/parse/git error.

For pre-commit, use the wrapper entry point, which accepts one or more
positional paths (pre-commit passes each matched file separately):

```yaml
  - repo: local
    hooks:
      - id: validate-module-taxonomy
        name: Validate module taxonomy
        entry: robotsix-modules-validate
        language: system
        files: ^docs/modules\.ya?ml$
        types_or: [yaml]
```

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
- `validate(taxonomy, *, schema=None)` — validate a dict; returns a list
  of human-readable error strings (empty = valid).
- `validate_file(path, *, schema_path=None)` — `load_taxonomy` then
  `validate`.
- `check_registration(taxonomy, repo_root, *, tracked_files=None)` —
  verify every tracked file is claimed by exactly one module.  Returns a
  list of `RegistrationFinding` objects.  Uses `git ls-files` by default;
  pass `tracked_files` to override.
- `validate_paths(taxonomy, repo_root)` — verify every module path entry
  resolves to at least one file on disk.  Returns a list of `PathFinding`
  objects.
- `SCHEMA_PATH` — `pathlib.Path` to the bundled schema.

## License

MIT
