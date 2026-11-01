"""Check that the schema-reference "Complete example" matches docs/modules.yaml.

Shared by ``scripts/check`` (local gate) and the ``schema-reference-sync``
CI job so both run the exact same comparison.  Exits non-zero on drift.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent


def _diff(kind: str, mid: str, actual: list[str], example: list[str]) -> str | None:
    """Return an error line when two order-normalised lists differ."""
    a, e = sorted(actual), sorted(example)
    if a == e:
        return None
    details = []
    only_actual = sorted(set(a) - set(e))
    only_example = sorted(set(e) - set(a))
    if only_actual:
        details.append(f"in modules.yaml but not in example: {only_actual}")
    if only_example:
        details.append(f"in example but not in modules.yaml: {only_example}")
    return f"module {mid!r}: {kind} mismatch — " + "; ".join(details)


def main() -> int:
    """Compare modules.yaml with the schema-reference example; return exit code."""
    actual: dict[str, Any] = yaml.safe_load(
        (ROOT / "docs/modules.yaml").read_text(encoding="utf-8")
    )
    md_text = (ROOT / "docs/schema-reference.md").read_text(encoding="utf-8")

    # Select the fenced YAML block containing 'package: robotsix_modules'.
    example_block = next(
        (
            m.group(1)
            for m in re.finditer(r"```yaml\n(.*?)\n```", md_text, re.DOTALL)
            if "package: robotsix_modules" in m.group(1)
        ),
        None,
    )
    if example_block is None:
        print(
            'ERROR: could not find "Complete example" YAML block in '
            "docs/schema-reference.md",
            file=sys.stderr,
        )
        return 1
    example: dict[str, Any] = yaml.safe_load(example_block)

    actual_by_id = {m["id"]: m for m in actual["modules"]}
    example_by_id = {m["id"]: m for m in example["modules"]}

    errors: list[str] = []
    for mid in sorted(set(actual_by_id) | set(example_by_id)):
        a = actual_by_id.get(mid)
        e = example_by_id.get(mid)
        if a is None:
            errors.append(f"module {mid!r}: present in example but not in modules.yaml")
            continue
        if e is None:
            errors.append(f"module {mid!r}: present in modules.yaml but not in example")
            continue
        for kind in ("paths", "dependencies"):
            err = _diff(kind, mid, a.get(kind, []), e.get(kind, []))
            if err:
                errors.append(err)

    if errors:
        print(
            "Schema-reference example is out of sync with modules.yaml:",
            file=sys.stderr,
        )
        for err in errors:
            print(f"  {err}", file=sys.stderr)
        return 1
    print("Schema-reference example matches modules.yaml.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
