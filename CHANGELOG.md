# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.0.0 (unreleased)

### Changed

- `src/robotsix_modules/validation/registration.py`: add explicit `check=False` to
  `subprocess.run()` call and remove unused `# noqa: S607` directive.

### Added

- OpenSSF Scorecard workflow (`.github/workflows/scorecard.yml`) running weekly
  and on push to `main`, with SARIF results uploaded to CodeQL for supply-chain
  security visibility.
- OpenSSF Scorecard badge in `README.md`.
- `.github/workflows/ci.yml`: add `dependency-review` job using
  `actions/dependency-review-action@v5` with `fail-on-severity: moderate` to catch
  vulnerable dependency changes on pull requests.
- `validate-pyproject` pre-commit hook and CI job to validate `pyproject.toml`
  against PEP 517/518/621/639/735 JSON Schemas, catching invalid classifier
  values, malformed dependency specs, and incorrect project metadata fields.
- `zizmor` static analysis for GitHub Actions workflow security: added to
  pre-commit hooks, CI pipeline (with SARIF upload), and dev dependencies.
- `validate-pyproject-schema-store[all]` as an additional dependency for the
  `validate-pyproject` hook and CI job, extending validation to third-party
  `[tool.*]` sections (ruff, mypy, pytest, coverage, deptry, bandit).
- Added `load_schema` to the public API surface of `robotsix_modules.validation`
  and `robotsix_modules` (`__all__` and top-level re-export).
- Replaced `pip-audit` with native `uv audit` for vulnerability scanning and
  `uv export --format cyclonedx1.5` for SBOM generation in CI.
- Markdown linting and formatting via `.markdownlint-cli2.jsonc`, pre-commit
  hooks (`markdownlint-cli2`, `mdformat`), and `scripts/lint`/`scripts/check`
  integration.
- `.gitignore` entries for `site/`, `wheel-env/`, `sbom.json`, `.env`, and
  `.DS_Store` to prevent accidental commits of docs build output, CI artifacts,
  and OS/environment files.

### Fixed

- Added `types: [markdown]` filter to the `markdownlint-cli2` pre-commit hook,
  preventing it from linting non-Markdown files (Python, YAML, JSON, etc.).
- Added missing `docs/cli/**` path glob to the `cli` module in
  `docs/modules.yaml`, classifying the previously unclaimed `docs/cli/usage.md`
  and completing the per-module layout for the CLI module.
- Added `docs` dependency group (`mkdocs-material`, `mkdocstrings[python]`) to
  `pyproject.toml` and updated `scripts/docs` to use `--group docs`, fixing a
  broken local docs preview (`uv run mkdocs serve` failed without the
  dependencies).
- Added `ignore_errors = true` for the `vulture_whitelist` module in mypy
  configuration, fixing a type-check failure caused by intentional bare names
  in the vulture whitelist file.
- CI: fix local-action-resolution failure by adding explicit `actions/checkout`
  step before each `uses: ./.github/actions/setup` call and removing checkout
  from within the composite action.
- Add empty `tracing` extra to `[project.optional-dependencies]` to satisfy
  reusable workflow's `uv sync --extra tracing` call.

### Changed

- Refactored `validate_main` to use a shared `_validate_paths` generator,
  reducing nesting depth and eliminating the duplicated `for path in args.paths`
  loop.
- Updated dev dependencies: ruff 0.15.16 → 0.15.18, pip-audit 2.10.0 → 2.10.1.

## 0.0.0 (unreleased)

### Fixed
- Fixed stale docstring in `robotsix_modules.validation.schemas` package init referencing non-existent `robotsix_modules.schemas` path.
- Stale GitHub org URLs in `CONTRIBUTING.md` and `.github/ISSUE_TEMPLATE/config.yml` replaced `robotsix/robotsix-modules` → `damien-robotsix/robotsix-modules`.

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
