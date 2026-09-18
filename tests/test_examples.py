"""Execute and lint every code example in README.md and docs/.

Uses `pytest-examples <https://github.com/pydantic/pytest-examples>`_ to
discover fenced Python code blocks, lint them (ruff + formatting), run
them, and verify any ``#>`` output annotations against real stdout. This
guards against API/documentation drift: an example that stops matching
the code fails CI.
"""

from __future__ import annotations

import pytest

pytest.importorskip("pytest_examples")

from pytest_examples import (  # noqa: E402
    CodeExample,
    EvalExample,
    find_examples,
)


@pytest.mark.parametrize("example", list(find_examples("README.md", "docs")), ids=str)
def test_docs_examples(example: CodeExample, eval_example: EvalExample) -> None:
    eval_example.lint(example)
    eval_example.run_print_check(example)
