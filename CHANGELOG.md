# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0]

Initial public release.

### Added
- JSON-Schema-driven (draft 2020-12) validation for the `docs/modules.yaml` module-taxonomy file, with the canonical schema bundled in the package.
- CLI (`robotsix-modules validate`, plus the `robotsix-modules-validate` pre-commit wrapper entry point) and Python API (`validate`, `validate_file`, `load_taxonomy`, `SCHEMA_PATH`).
- Test suite with coverage enforced at the 80% threshold in CI.
- Quality and security tooling in CI: Ruff (lint + format), mypy, deptry, bandit, and pip-audit.
