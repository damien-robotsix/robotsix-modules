# CLI Usage

The `robotsix-modules` package provides two CLI entry points:

- `robotsix-modules` — the primary CLI with subcommands for validation,
  registration checks, and path validation.
- `robotsix-modules-validate` — a convenience wrapper for pre-commit
  integration (accepts one or more positional file paths).

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

## Exit Codes

| Code | Meaning            |
|------|--------------------|
| 0    | Valid / no findings |
| 1    | Validation errors or findings found |
| 2    | File not found / parse errors / git errors |

All diagnostics go to stderr; stdout stays empty on success.

## Options

### `--verbose` / `-v`

Pass `-v` / `--verbose` to any subcommand (and the
`robotsix-modules-validate` wrapper) for more diagnostic detail:

- `-v` — shows informational messages (files being loaded)
- `-vv` — adds debug messages (glob expansion, git commands)

At default verbosity (no `-v`), only errors are reported.

### `--output-format {text,json}`

Pass `--output-format {text,json}` to any subcommand (and the
`robotsix-modules-validate` wrapper).

- `text` (default) — human-readable diagnostics to stderr
- `json` — writes a single JSON object to stdout:
  `{"findings": [...]}` for `check-registration`/`validate-paths`,
  `{"errors": [...]}` for `validate`. Operational errors stay on stderr.
  Exit codes are identical in both modes.

Example:

```console
$ robotsix-modules check-registration docs/modules.yaml --output-format json
{"findings": []}
```

### `--schema <path>`

Pass `--schema <path>` to `validate` to override the bundled schema.

### `--root <dir>`

For `check-registration` and `validate-paths`, add `--root <dir>` to
specify the repository root (defaults to the current directory). Both
subcommands follow the same exit-code contract: 0 = no findings, 1 =
findings found, 2 = file/parse/git error.

## Pre-commit Integration

Use the wrapper entry point, which accepts one or more positional paths
(pre-commit passes each matched file separately):

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
