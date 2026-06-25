## Summary

<!-- Briefly describe what this PR does and why. -->

## Test plan

<!-- How did you test this change? Describe manual steps, automated tests, or both. -->

---

**Pre-submit checklist** (see [`CONTRIBUTING.md`](./CONTRIBUTING.md) for
details):

- [ ] `uv run ruff check .`
- [ ] `uv run ruff format --check .`
- [ ] `uv run mypy src tests`
- [ ] `uv run pytest --cov --cov-report=xml --cov-report=term-missing`
- [ ] `uv run deptry .`
- [ ] `uv run bandit -c pyproject.toml -r src/`
- [ ] `uv audit`
- [ ] `uv.lock` is up to date (run `uv lock` if dependencies changed)
