# CLI Usage

The `robotsix-modules` package provides two CLI entry points:

- `robotsix-modules` — the primary CLI with subcommands for validation,
  registration checks, and path validation.
- `robotsix-modules-validate` — a convenience wrapper for pre-commit integration
  (accepts one or more positional file paths).

## Subcommands

### `validate`

```console
$ robotsix-modules validate docs/modules.yaml   # exit 0 when valid, empty output
$ robotsix-modules validate broken.yaml          # prints "<pointer>: <message>" lines to stderr; exit 1
$ robotsix-modules validate missing.yaml         # "robotsix-modules: error: file not found: ..."; exit 2
$ robotsix-modules --version                     # robotsix-modules 0.2.0
```

### `check-registration`

```console
$ robotsix-modules check-registration docs/modules.yaml
# exit 0 — every tracked file is claimed by exactly one module

$ robotsix-modules check-registration docs/modules.yaml --root /path/to/repo
# exit 1 — prints findings (unclassified files, stale paths, duplicates) to stderr
```

### `validate-paths`

```console
$ robotsix-modules validate-paths docs/modules.yaml
# exit 0 — every module path resolves to at least one file on disk

$ robotsix-modules validate-paths docs/modules.yaml --root .
# exit 1 — prints path_not_found / glob_empty findings to stderr
```

### `migrate`

```console
$ robotsix-modules migrate docs/modules.yaml
# exit 0 — prints simplified YAML to stdout with default-convention
# globs stripped from explicit path lists (YAML comments not preserved)

$ robotsix-modules migrate docs/modules.yaml --in-place
# exit 0 — rewrites the file in place (stderr: "Wrote simplified taxonomy to …")

$ robotsix-modules migrate no-such-file.yaml
# exit 2 — file not found
```

## Exit Codes

| Code | Meaning                                    |
| ---- | ------------------------------------------ |
| 0    | Valid / no findings                        |
| 1    | Validation errors or findings found        |
| 2    | File not found / parse errors / git errors |

All diagnostics go to stderr; stdout stays empty on success.

## Options

### `--verbose` / `-v`

Pass `-v` / `--verbose` to any subcommand (and the `robotsix-modules-validate`
wrapper) for more diagnostic detail:

- `-v` — shows informational messages (files being loaded)
- `-vv` — adds debug messages (glob expansion, git commands)

At default verbosity (no `-v`), only errors are reported.

### `--output-format {text,json}`

Pass `--output-format {text,json}` to any subcommand (and the
`robotsix-modules-validate` wrapper).

- `text` (default) — human-readable diagnostics to stderr
- `json` — writes a single JSON object to stdout: `{"findings": [...]}` for
  `check-registration`/`validate-paths`, `{"errors": [...]}` for `validate`.
  Operational errors stay on stderr. Exit codes are identical in both modes.

#### JSON output shapes

##### `validate`

The JSON output is `{"errors": string[]}` — a list of plain error strings.

Example:

```console
$ robotsix-modules validate broken.yaml --output-format json
{"errors": ["$.modules.0.name: required field missing", "$.modules.0.paths: expected array, got string"]}
```

##### `check-registration`

The JSON output is `{"findings": RegistrationFinding[]}`. Each finding is a
dict produced by `dataclasses.asdict` with these fields:

| Field | Type | Always present? | Description |
|-------|------|-----------------|-------------|
| `kind` | string | always | One of `"unclassified_file"`, `"stale_path"`, `"duplicate_registration"` |
| `message` | string | always | Human-readable one-liner |
| `file` | string or null | only for `unclassified_file` and `duplicate_registration` | Repo-relative path |
| `module_id` | string or null | only for `stale_path` and `duplicate_registration` | Module identifier |
| `other_module_id` | string or null | only for `duplicate_registration` | Second claimant module id |

Example:

```console
$ robotsix-modules check-registration docs/modules.yaml --output-format json
{"findings": [{"kind": "unclassified_file", "message": "File 'orphan.txt' is not claimed by any module", "file": "orphan.txt", "module_id": null, "other_module_id": null}]}
```

##### `validate-paths`

The JSON output is `{"findings": PathFinding[]}`. Each finding is a dict
produced by `dataclasses.asdict` with these fields:

| Field | Type | Always present? | Description |
|-------|------|-----------------|-------------|
| `kind` | string | always | One of `"path_not_found"`, `"glob_empty"` |
| `message` | string | always | Human-readable one-liner |
| `module_id` | string | always | Module identifier |
| `path` | string | always | The literal path or glob pattern that failed |

Example:

```console
$ robotsix-modules validate-paths docs/modules.yaml --output-format json
{"findings": [{"kind": "path_not_found", "message": "Path 'src/missing.py' does not exist", "module_id": "my-module", "path": "src/missing.py"}]}
```

### `--schema <path>`

Pass `--schema <path>` to `validate` to override the bundled schema.

### `--root <dir>`

For `check-registration` and `validate-paths`, add `--root <dir>` to specify the
repository root (defaults to the current directory). Both subcommands follow the
same exit-code contract: 0 = no findings, 1 = findings found, 2 = file/parse/git
error.

## Pre-commit Integration

Use the wrapper entry point, which accepts one or more positional paths
(pre-commit passes each matched file separately).

### Remote-repo (recommended)

Add the following to your `.pre-commit-config.yaml` (requires no global
installation — pre-commit provisions an isolated venv automatically):

```yaml
  - repo: https://github.com/damien-robotsix/robotsix-modules
    rev: v0.2.0
    hooks:
      - id: validate-module-taxonomy
```

### Local hook (alternative)

If you have the package installed globally and want to pin a specific
version or use non-default arguments, use the `repo: local` style:

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
