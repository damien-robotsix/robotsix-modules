# AGENT.md — robotsix-modules

This repo follows the [robotsix stack standards](https://github.com/damien-robotsix/robotsix-standards).

## Package identity

`robotsix-modules` is a **pure validation + CLI library**. It provides
JSON-Schema-driven module-taxonomy validation for robotsix projects. There is
**no server, no LLM calls, no database** — agents must not propose adding web
frameworks, ORMs, or LLM dependencies.

## Testing conventions

Tests live under `tests/` mirroring the source layout:

```
src/robotsix_modules/validation/…   →  tests/validation/…
src/robotsix_modules/cli/…          →  tests/cli/…
```

Run the suite with:

```bash
pytest
```

The `check-registration` CLI subcommand (`robotsix-modules check-registration`)
validates that every tracked source and test file is registered in
`docs/modules.yaml`. This check is enforced in CI — any new source module
**must** be registered there.

## Configuration

No `BaseSettings`, no env vars, no YAML config files. The only config surface is
CLI flags on the `robotsix-modules` console script.

## Delegation — YAML I/O

Use `robotsix_modules._yaml.read_yaml_file` for any YAML I/O (e.g. reading
`docs/modules.yaml`). Agents must **not** add a second YAML parser.

## CI invariants

The `.pre-commit-config.yaml` runs: `ruff` (lint + format), `mypy`, `bandit`,
`detect-secrets`, `vulture`, and `robotsix-modules-validate` (which validates
`docs/modules.yaml` against the bundled JSON Schema).

The CI pipeline (`.github/workflows/ci.yml`) additionally enforces: coverage
threshold, `check-registration` via the reusable `python-ci.yml` workflow,
version consistency across `pyproject.toml` / `CHANGELOG.md` / `README.md` /
`SECURITY.md`, a smoketest wheel install, and a `uv audit` / SBOM step.

Any new source or test file must pass all of these gates.

## Project layout

- `.pre-commit-hooks.yaml` — pre-commit hook manifest at the repo root. When
  this repo provides a pre-commit hook with an `id:` defined in
  `.pre-commit-config.yaml`, ship a `.pre-commit-hooks.yaml` so downstream users
  can consume it as a remote pre-commit source
  (`repo: https://github.com/damien-robotsix/robotsix-modules`) rather than
  requiring a `repo: local` / `language: system` setup. Every hook entry in
  `.pre-commit-hooks.yaml` must use `language: python` (not `language: system`).
- Dogfood: the repo's own `.pre-commit-config.yaml` references the hook via
  `repo: .` (with `rev: ""`) instead of duplicating it under `repo: local`.

## Docs conventions

- `docs/modules.yaml` — the canonical module registry. Every logical module
  lists its file paths and dependencies.
- `docs/schema-reference.md` — documents the YAML schema that `modules.yaml`
  must follow.
- Keep these two files in sync: if the schema changes, update the reference doc.
