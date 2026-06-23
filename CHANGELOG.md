# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.0.0 (unreleased)

### Added

- Markdown linting and formatting via `.markdownlint-cli2.jsonc`, pre-commit
  hooks (`markdownlint-cli2`, `mdformat`), and `scripts/lint`/`scripts/check`
  integration.

## [0.2.0]

### Added

- `check_registration()` – verifies every tracked file is claimed by exactly one
  module, detecting unclassified files, stale paths, and duplicate
  registrations.
- `validate_paths()` – checks that every module path entry (literal or glob)
  resolves to at least one file on disk.
- `RegistrationFinding` and `PathFinding` frozen-dataclass types for structured
  findings.
- CLI subcommands: `robotsix-modules check-registration` and
  `robotsix-modules validate-paths`, each with `--root` flag and exit-code
  semantics (0/1/2).
- Public API re-exports for the new functions and types from the package root.

## [0.1.0]

Initial public release.

### Added

- JSON-Schema-driven (draft 2020-12) validation for the `docs/modules.yaml`
  module-taxonomy file, with the canonical schema bundled in the package.
- CLI (`robotsix-modules validate`, plus the `robotsix-modules-validate`
  pre-commit wrapper entry point) and Python API (`validate`, `validate_file`,
  `load_taxonomy`, `SCHEMA_PATH`).
- Test suite with coverage enforced at the 80% threshold in CI.
- Quality and security tooling in CI: Ruff (lint + format), mypy, deptry,
  bandit, and pip-audit.
