"""Check that pyproject.toml's version matches CHANGELOG.md, README.md, SECURITY.md.

Shared by ``scripts/check`` (local gate) and the ``version-check`` CI job so
both run the exact same comparison.  Exits non-zero on drift.
"""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

_VERSION_CORE_RE = re.compile(r"\d+\.\d+\.\d+")
# First `## [x.y.z]` heading; release-please puts the newest release first.
_CHANGELOG_RE = re.compile(r"^## \[([^\]]+)\]", re.MULTILINE)
# Every `@vX.Y.Z` install-pin token in the README install examples.
_README_RE = re.compile(r"@v(\d+\.\d+\.\d+)")
# The `**vX.Y.Z**` supported-version token in SECURITY.md.
_SECURITY_RE = re.compile(r"\*\*v(\d+\.\d+\.\d+)\*\*")


def _version_core(text: str) -> str | None:
    """Return the ``X.Y.Z`` numeric core of a version string (ignoring ``v``)."""
    m = _VERSION_CORE_RE.search(text)
    return m.group(0) if m else None


def main() -> int:
    """Compare pyproject.toml's version with the three docs; return exit code."""
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    version = pyproject["project"]["version"]
    version_core = _version_core(version)
    if version_core is None:
        print(
            f"ERROR: cannot parse version {version!r} from pyproject.toml",
            file=sys.stderr,
        )
        return 1

    errors: list[str] = []

    # CHANGELOG.md — first `## [x.y.z]` heading must equal `version`.
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    m = _CHANGELOG_RE.search(changelog)
    if m is None:
        errors.append("CHANGELOG.md: no `## [x.y.z]` heading found")
    else:
        actual = _version_core(m.group(1))
        if actual != version_core:
            errors.append(
                f"CHANGELOG.md: first `## [...]` heading has version "
                f"{m.group(1)!r}, expected {version!r}"
            )

    # README.md — every `@vX.Y.Z` token must equal `@v{version}`; fail if none.
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_core = _README_RE.findall(readme)
    if not readme_core:
        errors.append("README.md: no `@vX.Y.Z` install-pin token found")
    else:
        for actual in readme_core:
            if actual != version_core:
                errors.append(
                    f"README.md: install-pin token @v{actual} does not match "
                    f"@v{version_core}"
                )

    # SECURITY.md — the `**vX.Y.Z**` supported-version token must match.
    security = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
    m = _SECURITY_RE.search(security)
    if m is None:
        errors.append("SECURITY.md: no `**vX.Y.Z**` supported-version token found")
    else:
        actual = m.group(1)
        if actual != version_core:
            errors.append(
                f"SECURITY.md: supported-version token **v{actual}** does not "
                f"match **v{version_core}**"
            )

    if errors:
        print(
            f"Version consistency failed: pyproject.toml has {version!r}, but:",
            file=sys.stderr,
        )
        for err in errors:
            print(f"  {err}", file=sys.stderr)
        return 1
    print(
        f"Version consistency OK: pyproject.toml, CHANGELOG.md, README.md, "
        f"and SECURITY.md all match {version!r}."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
