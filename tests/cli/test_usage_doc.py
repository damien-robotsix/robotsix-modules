"""Doc-sync tests: ``docs/cli/usage.md`` must stay in sync with ``FindingKind``.

The ``kind`` literals in the JSON-output tables of ``docs/cli/usage.md``
(``check-registration`` and ``validate-paths``) are hand-written inline
table cells, not rendered from the enum — a new or renamed
:class:`~robotsix_modules.validation._findings.FindingKind` member would
otherwise ship with stale docs. These tests enforce the sync locally under
``pytest``.
"""

from __future__ import annotations

import re
from pathlib import Path

from robotsix_modules.validation._findings import FindingKind

_DOC_PATH = Path(__file__).resolve().parent.parent.parent / "docs" / "cli" / "usage.md"


def _documented_kinds() -> set[str]:
    """Return the kind literals documented in ``docs/cli/usage.md``.

    Kinds are documented as backtick-quoted strings in the ``kind`` table
    rows, e.g. ``One of `"unclassified_file"`, ...`` — the same style used
    for schema field names in ``docs/schema-reference.md``.
    """
    doc = _DOC_PATH.read_text(encoding="utf-8")
    return set(re.findall(r'`"([a-z][a-z0-9_]*)"`', doc))


def test_usage_doc_lists_every_finding_kind() -> None:
    """Every ``FindingKind`` member value appears in ``docs/cli/usage.md``."""
    documented = _documented_kinds()
    missing = {kind.value for kind in FindingKind} - documented
    assert not missing, (
        "FindingKind member value(s) "
        + ", ".join(sorted(missing))
        + " are not documented in docs/cli/usage.md. Add them to the "
        'kind table rows (as `"value"` literals) to keep the docs in sync.'
    )


def test_usage_doc_lists_no_undocumented_kinds() -> None:
    """Every kind literal in ``docs/cli/usage.md`` is a ``FindingKind`` member."""
    documented = _documented_kinds()
    stale = documented - {kind.value for kind in FindingKind}
    assert not stale, (
        "docs/cli/usage.md documents kind literal(s) "
        + ", ".join(sorted(stale))
        + " that are not FindingKind members. Remove them or add the "
        "corresponding members to FindingKind."
    )
