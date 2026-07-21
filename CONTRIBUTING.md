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
   uv sync --group dev
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

The 80% coverage threshold lives in `pyproject.toml` (`fail_under` under
`[tool.coverage.report]`), so `pytest --cov` enforces the identical gate both
locally and in CI:

```console
uv run pytest --cov --cov-report=xml --cov-report=term-missing
```

New code should keep coverage at or above the 80% threshold, so please add tests
for any behavior you introduce.

## Linting, formatting, and static checks

For a quick run of the lint and type-check gates, use the convenience scripts:

```console
scripts/lint       # ruff + mypy
scripts/check      # full CI gate: lint, type-check, deptry, bandit, uv audit, pytest
```

These are thin wrappers around the `uv run ...` commands below. CI gates every
change on the following commands. Run them locally to make sure your change
passes before pushing:

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

## Creating a changelog fragment

Every pull request that changes user-visible behavior (features, bug fixes,
deprecations, removals, documentation) needs a changelog fragment. The fragment
is a single file in `changelog.d/` whose filename determines what section of the
changelog it appears under.

### Filename format

```
<TIMESTAMP>-<SHORT-DESCRIPTION>.<TYPE>.md
```

- `TIMESTAMP` — current UTC timestamp in `YYYYMMDDTHHMMSSZ` format.
- `SHORT-DESCRIPTION` — kebab-case slug (e.g. `fix-auth-timeout`).
- `TYPE` — one of the following:

| Type | Section heading | When to use |
|------|----------------|-------------|
| `feature` | Features | New user-facing functionality, new CLI subcommands, new public API surfaces |
| `bugfix` | Bug Fixes | Fixes for incorrect behavior, crashes, or unexpected errors |
| `change` | Changes | Modifications to existing behavior that are not strictly bug fixes |
| `deprecation` | Deprecations | Marking a feature as deprecated |
| `removal` | Removals | Removing a deprecated feature |
| `security` | Security | Security-related fixes or improvements |
| `doc` | Documentation | Changes to documentation only (README, CONTRIBUTING, docstrings) |
| `misc` | (hidden) | Internal tooling, CI, dependency bumps, refactoring with no user impact |

> **Note:** The `misc` type has `showcontent = false`, meaning its entries do
> not appear in the rendered changelog. Use it only for internal changes that
> users don't need to know about.

### Using towncrier create

Instead of manually naming the file, you can use:

```console
uv run towncrier create changelog.d/PULL_NUMBER.feature.md
```

Replace `feature` with the correct type from the table above.

### Examples

```
# New CLI subcommand
20260721T130000Z-add-migrate-subcommand.feature.md

# Fix crash on empty modules.yaml
20260721T130000Z-fix-crash-on-empty-yaml.bugfix.md

# Internal refactor with no user impact
20260721T130000Z-refactor-validate-loop.misc.md
```

## Releasing a new version

Releases are cut by maintainers and published to PyPI automatically. Follow
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

2. Build the changelog entry from the accumulated news fragments with
   [towncrier](https://towncrier.readthedocs.io/):

   ```console
   uv run towncrier build --yes --version X.Y.Z
   ```

   This updates `CHANGELOG.md` with the fragments under `changelog.d/` and
   deletes those fragment files.

3. Commit the updated `CHANGELOG.md` and the deleted fragment files, push to
   `main`, and confirm CI is green.

4. Create a GitHub Release whose tag follows the `v{version}` convention
   (version `0.3.0` → tag `v0.3.0`). Use `gh release create` with draft release
   notes produced by towncrier:

   ```console
   gh release create v<version> \
     --title "v<version>" \
     --notes "$(uv run towncrier build --draft --version X.Y.Z 2>/dev/null | tail -n +6)"
   ```

5. Publishing the GitHub Release fires `.github/workflows/release.yml`, which
   calls the `damien-robotsix/robotsix-mill` reusable `python-release.yml`
   workflow and publishes the package to PyPI via
   [Trusted Publishing](https://docs.pypi.org/trusted-publishers/) — no manual
   `twine` or token step is required. Confirm the `Publish to PyPI` workflow run
   succeeds.

> **Install contract:** The PyPI artifact is installable via a plain
> `pip install robotsix-modules`. All runtime dependencies are published
> to PyPI.

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
