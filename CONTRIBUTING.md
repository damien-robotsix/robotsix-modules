# Contributing to robotsix-modules

Thanks for your interest in contributing! This project provides shared
JSON-Schema-driven module-taxonomy validation for robotsix projects — see
[`README.md`](README.md) for what it does and how to use it. The guide below
explains how to set up your environment, run the same checks CI runs, and
submit a pull request.

## Development environment setup

This project uses [`uv`](https://docs.astral.sh/uv/) to manage the
environment and dependencies.

1. Clone the repository:

   ```console
   git clone https://github.com/robotsix/robotsix-modules.git
   cd robotsix-modules
   ```

2. Install the project together with the `dev` extra:

   ```console
   uv sync --extra dev
   ```

CI installs the exact same dependency set from the committed `uv.lock` with:

```console
uv sync --frozen --extra dev
```

`uv.lock` is committed to the repository and is the source of truth for
reproducible installs. It is regenerated with `uv lock` whenever the
dependencies in `pyproject.toml` change — never hand-edit it.

## Running tests

Run the test suite the same way CI does:

```console
uv run pytest
```

CI enforces coverage with:

```console
uv run pytest --cov --cov-branch --cov-report=term-missing --cov-fail-under=80
```

New code should keep coverage at or above the 80% threshold, so please add
tests for any behavior you introduce.

## Linting, formatting, and static checks

CI gates every change on the following commands. Run them locally to make sure
your change passes before pushing:

```console
uv run ruff check .
uv run ruff format .          # CI runs `ruff format --check .`
uv run mypy src tests
uv run deptry .
uv run bandit -c pyproject.toml -r src/
uv run pip-audit --strict --vulnerability-service osv --desc
```

Optionally, you can run the [pre-commit](https://pre-commit.com/) hooks
defined in `.pre-commit-config.yaml` against the whole tree:

```console
uv run pre-commit run --all-files
```

## Submitting a pull request

- Run the full lint, format, type-check, and test gate locally before
  committing so CI stays green.
- Include tests for any new behavior, keeping coverage at or above the
  threshold.
- Keep changes focused — one logical change per pull request makes review
  easier.
- Open your pull request against the `main` branch. CI runs on every pull
  request, so all checks must pass before a change can be merged.

## License & conduct

By contributing, you agree that your contributions are accepted under the
project's MIT [`LICENSE`](LICENSE).

Please be respectful and constructive in issues, pull requests, and reviews.
We want this to be a welcoming, collaborative space for everyone.
