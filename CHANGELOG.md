# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!-- towncrier release notes start -->

## 0.0.0 (unreleased)

### Removed

- Add `[tool.uv] exclude-newer = "7 days"` to prevent CI from
  resolving packages published in the last 7 days, closing the
  window between a malicious upload and its advisory publication.
- Extract `_emit_results` helper in `validate_main` to eliminate duplicated output-format dispatch logic, reducing nesting depth from 5 to 3.
- Removed unused `YamlConfigError` class from `_yaml.py` (the sole subclass `YamlReadError` now inherits directly from `ConfigError`).
- Pin `vulture` dev dependency to `>=2.16` in `pyproject.toml` to match the version locked in `uv.lock` and prevent silent breakage on regeneration.
- Add `--strict-markers` to pytest `addopts` in `pyproject.toml` to catch unregistered marker typos.
- Expose CHANGELOG.md as a Changelog page on the MkDocs site via the existing hook pattern (on_pre_build copy, on_post_build remove) and a new nav entry.
- Classify `changelog.d/.gitkeep` under the `root` module in `docs/modules.yaml` so the registration check passes.
- Exported `YamlReadError` via `robotsix_modules.__all__` so callers of `load_taxonomy()` can catch it without importing from the private `_yaml` module.
- Added fragment-type guidance to CONTRIBUTING.md and PR template, and CI validation
  to catch unknown fragment types before merge, preventing invisible changelog entries
  when `towncrier build` is run for the first release.
- Add ``__main__.py`` shim so ``python -m robotsix_modules`` works (delegates to ``cli:main()``).
- Updated the "Complete example" in `docs/schema-reference.md` to match the
  current `docs/modules.yaml`: added the `root` module, moved
  `.pre-commit-hooks.yaml` from `docs` to `root`, and added `_exceptions.py`
  to the `validation` module paths.
- Removed the unused `YamlParseError` exception class from `_yaml.py`, which was never raised or imported anywhere in the codebase.
- Enable `survey` periodic agent with `.robotsix-mill/periodic/survey.yaml`.
- Add periodic docstring_coverage agent config to `.robotsix-mill/periodic/docstring_coverage.yaml`.
- Add `.robotsix-mill/periodic/health.yaml` to enable the health periodic agent, which inspects the codebase across eight dimensions (test coverage, linting, dependency freshness, CI completeness, documentation, etc.) and proposes draft tickets for newly-discovered gaps.
- `read_yaml_file` now raises `ConfigParseError` (instead of the internal `YamlParseError`) when a file contains invalid YAML, matching the public API contract documented in the package docstring.
- Enable the `changelog_autofill` periodic task to auto-commit changelog entries for PRs with a failing changelog CI check.
- Fixed duplicate `run:` key in `.github/actions/setup/action.yml` that caused `UV_MALWARE_CHECK` env var to be ignored during `uv sync`
- Bump `mirrors-mypy` pre-commit hook from v2.1.0 to v2.3.0 to align with the
  `mypy>=2.2.0` dev dependency, ensuring consistent type-checking across all
  environments.
- Move `.pre-commit-hooks.yaml` from the `docs` module to the `root` module in `docs/modules.yaml` (the file is a repo-root pre-commit hook manifest, not documentation).
- Add `repo_description_sync` periodic workflow to keep the forge description aligned with the README.
- Enable `state_sync` periodic workflow to cross-reference `FindingKind` enum members against string-literal reference sites across the codebase.
- Enable `audit` periodic agent (`.robotsix-mill/periodic/audit.yaml`)
- Add `copy_paste` periodic workflow (`.robotsix-mill/periodic/copy_paste.yaml`) to detect copy-paste duplication across the repository via jscpd.
- Re-export `compute_default_globs` from the top-level `robotsix_modules` package and document it in the API reference and quick-start index.
- Add `check_coverage` to the Public API list in `docs/index.md`
- `ConfigStructureError` is now raised by `read_yaml_file` when the parsed YAML root is not a mapping (previously `YamlParseError` was raised for both invalid-YAML and non-mapping cases). Fixed a stale `InvalidConfigStructureError` docstring reference in `load_taxonomy`.
- Add `FindingKind` to `docs/validation/api.md` members list to ensure it renders in the generated API docs and avoids broken cross-references.
- Enable `completeness_check` periodic agent to scan internal wiring of the robotsix-modules tool itself.
- Added `changelog.d/**` to the `root` module's paths in `docs/modules.yaml`.
- Enable `module_curator` periodic agent to curate the reference `docs/modules.yaml` taxonomy
- Remove Python 3.12 version-portable `**` glob rewrite workaround from `_glob_paths`.
  The project now requires Python >=3.14 where `Path.glob("**")` natively matches files.
- Enable baseline periodic agents (`test_gap`, `bc_check`, `security_posture`) via `.robotsix-mill/periodic/` presence files.
- Create `changelog.d/` directory for towncrier-managed changelog fragments.
- Add `towncrier-check` pre-commit hook (repo: local) to validate changelog fragments.
- Updated the release checklist in `CONTRIBUTING.md` to use the towncrier-based
  workflow: `towncrier build --yes` to generate the changelog, commit the
  updated `CHANGELOG.md` and deleted fragments, and `gh release create` with
  draft notes from `towncrier build --draft`.
- Deduplicate `CODE_OF_CONDUCT.md`: keep single canonical copy at repo root,
  remove `docs/` symlink, and use a MkDocs build-time hook to supply the
  file during documentation builds.
- Remove all periodic mill workflows from `.robotsix-mill/periodic/` to pause auto-generated ticket flooding (audit, survey, completeness_check, test_gap, security_posture, and others). Workflows can be restored individually by re-adding their `.yaml` files.
- Enforce `check-registration` in CI (new `check-registration` job in `ci.yml`) and in the local `scripts/check` script, closing a gap where unregistered files could silently drift out of sync with `docs/modules.yaml`.
- Introduce `FindingKind(StrEnum)` in `src/robotsix_modules/validation/_findings.py` to replace magic-string finding kinds (`"unclassified_file"`, `"stale_path"`, `"duplicate_registration"`, `"path_not_found"`, `"glob_empty"`). All source, test, and README usage sites now reference the enum members instead of raw string literals.
- Register root-level `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `.robotsix-mill/**`, and `scripts/**` under the `root` module's path list in `docs/modules.yaml`, closing remaining `unclassified_file` findings from `check-registration`.
- Remove unused `RobotsixModulesError` import from `robotsix_modules.cli`.)
- Register `src/robotsix_modules/_exceptions.py` in the `validation` module's path list in `docs/modules.yaml`.
- Revert cosmetic `...` added by prior attempt to root `CONTRIBUTING.md`. The
  core deduplication (`docs/CONTRIBUTING.md` as symlink to `../CONTRIBUTING.md`)
  was already in place from a prior PR; no further changes needed.
- Updated `docs/schema-reference.md` to document the `package` field, correct the `paths` requirement from mandatory to optional (convention globs are synthesised from `package`), and refresh the complete example to match the current `docs/modules.yaml`.
- Add `.github/workflows/lint-workflows.yml` to run actionlint and zizmor on push/PR, using the shared reusable workflow from `robotsix-github-workflows`.
- Add custom exception hierarchy: `RobotsixModulesError` base class with typed subclasses `GitOperationError`, `ConfigError`, `ConfigFileNotFoundError`, `ConfigParseError`, and `ConfigStructureError`. Git-operation failures now raise `GitOperationError` instead of bare `RuntimeError`.
- Remove the retired `robotsix-yaml-config` dependency. The package now uses
  PyYAML directly for all YAML I/O via its internal `_yaml` wrapper, matching
  the config-standard migration to `robotsix-config`.

### Added
- Added `towncrier>=25.8.0` to dev dependencies and configured `[tool.towncrier]` for changelog management.
- Add `paths` globs to the `cli` module in `docs/modules.yaml` to properly claim its source, test, and doc files.
- Classify validation subpackage files under the `validation` module in `docs/modules.yaml` (11 files now claimed via glob paths).
- Resolve mypy strict-mode errors in test files: add type annotations to conftest helpers, add `types-PyYAML` dev dependency, and fix TestMigrate type signatures.
- Add coverage check to `validate` and `validate-main` subcommands: every tracked file must be covered by at least one module's globs (explicit paths + convention defaults). Previously only `check-registration` performed this check; now the pre-commit `robotsix-modules-validate` hook also catches unclassified files.
- Add ``robotsix-modules migrate`` CLI subcommand that rewrites a
  ``modules.yaml`` to strip explicit path entries already covered by
  convention default globs (``src/<pkg>/<id>/**``, ``tests/<id>/**``,
  ``docs/<id>/**``). Supports ``--in-place`` for file overwrite.
  YAML comments are not preserved.
- Make module ``paths`` optional in ``modules.yaml``: when a top-level
  ``package`` field is set, modules without explicit paths inherit three
  convention globs (``src/<package>/<id>/**``, ``tests/<id>/**``,
  ``docs/<id>/**``).  Add ``compute_default_globs`` to the public API.
- Dogfood `.pre-commit-hooks.yaml` in own `.pre-commit-config.yaml` via `repo: .` instead of `repo: local`.
  Document the pre-commit hook layout convention in `AGENT.md` (## Project layout).
- Added `.pre-commit-hooks.yaml` at repo root enabling remote-repo consumption of the `validate-module-taxonomy` hook (`language: python`)
- Updated `docs/cli/usage.md` — split the pre-commit integration section into two separate code blocks: a remote-repo (recommended) example and the existing local-hook block
- Add `.github/workflows/dependabot-auto-merge.yml` to auto-merge Dependabot PRs once required checks pass.
- Add robotsix-standards reference link to `README.md` and `AGENT.md`.
- Migrate secret scanning from `detect-secrets` to `gitleaks` in both pre-commit and CI, and add a minimal `.gitleaks.toml` configuration.
- Extract `RegistrationFinding` dataclass and its six helper functions from `registration.py` into a new `validation/_findings.py` module for improved cohesion.
- Consolidate duplicate CLI error-path test boilerplate: added shared helpers in `tests/conftest.py` (`run_missing_file_test`, `run_invalid_yaml_test`, `run_root_flag_respected_test`) and replaced 7 per-class duplicate methods in `tests/cli/test_cli.py` with 3 parametrized module-level tests.
- Bump bandit[toml] requirement from >=1.8 to >=1.9.4
- Bump pre-commit hook versions: `pre-commit-hooks` v5.0.0→v6.0.0,
  `ruff` v0.15.15→v0.15.19, `mirrors-mypy` v1.19.1→v2.1.0,
  `zizmor` v1.23.1→v1.26.1
- Add `detect-secrets` CI job to `.github/workflows/ci.yml` for server-side secret scanning with existing baseline
- Update pinned GitHub Actions to latest versions: `actions/checkout` to v7.0.0, `astral-sh/setup-uv` to v8.2.0, `github/codeql-action/upload-sarif` to v4.36.2, `actions/upload-artifact` to v7.0.1. Correct misleading version comment on `codeql-action/upload-sarif`. (mill: Update stale GitHub Actions to latest pinned versions across CI workflows (20260701T092348Z-update-stale-github-actions-to-latest-pi-a566))
- Add `security_posture` periodic workflow to `.robotsix-mill/periodic/` for automated security posture review.
- Document CLI JSON output field schemas for `validate`, `check-registration`, and `validate-paths` subcommands in `docs/cli/usage.md`.
- `CODE_OF_CONDUCT.md`: adopt Contributor Covenant v2.1 with enforcement guidelines and
  reporting contact (`damien.robotsix@gmail.com`).
- `CONTRIBUTING.md`: replace informal "License & conduct" section with a formal code of
  conduct reference and reporting instructions.
- `README.md`: add `## Contributing` section with Contributor Covenant badge and links
  to contributing guide and code of conduct.
- Added `ExitCode` IntEnum (`src/robotsix_modules/cli/_exit_codes.py`) to replace
  raw integer exit codes in the CLI, with named members `OK`, `ERRORS`, and `FATAL`.
- Register `docs/CODE_OF_CONDUCT.md` in the `docs` module's path list in `docs/modules.yaml`.
- `mkdocs.yml`: enable `strict: true` and `validation` block (omitted files, absolute
  links, unrecognized links, anchors) so `mkdocs build --strict` catches broken nav
  entries, orphaned files, and stale cross-references at build time.
- `.github/workflows/ci.yml`: add `mkdocs-build` job that runs `mkdocs build --strict`
  on every PR.
- `scripts/check`: add `mkdocs build --strict` step after pytest so local development
  mirrors the CI docs gate.

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

- Suppress ruff S607 (`start-process-with-partial-path`) on intentional `git ls-files`
  subprocess call in `registration.py`.
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
