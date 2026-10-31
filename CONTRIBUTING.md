# Contributing to robotsix-modules

Thanks for your interest in contributing! This project provides shared
JSON-Schema-driven module-taxonomy validation for robotsix projects — see
[`README.md`](https://github.com/damien-robotsix/robotsix-modules/blob/main/README.md) for what it does and how to use it. The guide below
explains how to set up your environment, run the same checks CI runs, and submit
a pull request.

## Development environment setup

This project uses [`uv`](https://docs.astral.sh/uv/) to manage the environment
and dependencies.

1. Clone the repository:

   ```console
   git clone https://github.com/damien-robotsix/robotsix-modules.git
   cd robotsix-modules
   ```

2. Install the project together with the `dev` extra:

   ```console
   uv sync --group dev --group test
   ```

CI installs the exact same dependency set from the committed `uv.lock` with:

```console
uv sync --frozen --group dev
```

`uv.lock` is committed to the repository and is the source of truth for
reproducible installs. It is regenerated with `uv lock` whenever the
dependencies in `pyproject.toml` change — never hand-edit it.

## Running tests

For a quick run, use the convenience script:

```console
scripts/test
```

This is a thin wrapper around `uv run pytest` with coverage enabled. Run the
test suite the same way CI does with either:

```console
uv run pytest
```

The 90% coverage threshold lives in `pyproject.toml` (`fail_under` under
`[tool.coverage.report]`), so `pytest --cov` enforces the identical gate both
locally and in CI:

```console
uv run pytest --cov --cov-report=xml --cov-report=term-missing
```

New code should keep coverage at or above the 90% threshold, so please add tests
for any behavior you introduce.

## Linting, formatting, and static checks

The single command that runs every CI gate locally is:

```console
scripts/check
```

It runs, in order, `ruff check`, `ruff format --check`, `mypy`, `deptry`,
`vulture`, `check-registration` on `docs/modules.yaml`, the schema-reference
sync check (`scripts/check_schema_reference_sync.py`, also used by CI), and
`pytest`, followed by `bandit`, `uv audit`, the Markdown linters and
`mkdocs build --strict`. It stops at the first failing gate, names it, and exits
non-zero. The gate list lives in the `GATES` array in `scripts/check` — keep it
in sync with `.github/workflows/ci.yml`.

For a quick run of only the lint, type-check and Markdown gates, use
`scripts/lint`.

The individual commands CI gates every change on include:

```console
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests
uv run deptry .
uv run bandit -c pyproject.toml -r src/
uv audit
```

Optionally, you can run the [pre-commit](https://pre-commit.com/) hooks defined
in `.pre-commit-config.yaml` against the whole tree:

```console
uv run pre-commit run --all-files
```

## Submitting a pull request

- Run the full lint, format, type-check, and test gate locally before committing
  so CI stays green.
- Include tests for any new behavior, keeping coverage at or above the
  threshold.
- Keep changes focused — one logical change per pull request makes review
  easier.
- Open your pull request against the `main` branch. CI runs on every pull
  request, so all checks must pass before a change can be merged.

## Commit message conventions

Commit subjects and PR titles must follow
[Conventional Commits](https://www.conventionalcommits.org/):

```
<type>: <description>
```

Use one of: `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`, `ci:`.
[Release-please](https://github.com/googleapis/release-please) reads these
commit messages to generate `CHANGELOG.md` automatically — no manual fragment
files are needed.

## Releasing a new version

Releases are cut by maintainers via release-please (no PyPI publish). Follow
these steps in order:

1. Bump the `version` field under `[project]` in `pyproject.toml`, following
   [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

   > **Note:** `__version__` in `src/robotsix_modules/__init__.py` is now
   > auto-derived from `pyproject.toml` at runtime via `importlib.metadata` and
   > no longer needs manual updating. The test assertion in
   > `tests/cli/test_cli.py` reads `__version__` dynamically — no manual update
   > needed there either.
   >
   > The following files still require **manual** version-string updates; the CI
   > version-consistency job enforces them:
   >
   > - `README.md` — the `vX.Y.Z` strings in install examples (3 occurrences).
   > - `SECURITY.md` — the `**vX.Y.Z**` supported-version string.

2. Commit the version bump, push to `main`, and confirm CI is green.

3. [Release-please](https://github.com/googleapis/release-please) will open
   (or update) a release PR that bumps the version and updates `CHANGELOG.md`
   from conventional commit messages. Merge that PR when ready.

4. Merging the release PR creates a GitHub Release and the `v{version}` tag
   automatically. The package is **not** published to PyPI: the fleet
   standards (`distribution-packaging.md`) prohibit publishing to public
   registries, and consumers pin this repository by git revision
   (`uv.lock` `source = { git = ... }`).

## Dependabot

Dependabot is configured to open automated dependency-update PRs for both Python
packages (via `uv`) and GitHub Actions. Dependabot updates the constraints in
`pyproject.toml` but does **not** regenerate `uv.lock`. Before merging a
Dependabot PR that touches Python dependencies, run:

```console
uv lock
```

and commit the updated `uv.lock` to the PR branch. For GitHub Actions updates no
lockfile regeneration is needed.

## License & code of conduct

By contributing, you agree that your contributions are accepted under the
project's MIT [LICENSE](https://github.com/damien-robotsix/robotsix-modules/blob/main/LICENSE).

Please note that this project is governed by the
[Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). All
contributors are expected to uphold this code. Report unacceptable
behavior to [damien.robotsix@gmail.com](mailto:damien.robotsix@gmail.com).
