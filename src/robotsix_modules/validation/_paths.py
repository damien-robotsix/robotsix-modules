"""Shared path utilities used by registration and findings modules.

Extracted from ``registration.py`` to break a circular dependency with
``_findings.py``.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path, PurePosixPath


def _has_glob_metacharacters(pattern: str) -> bool:
    """Return True when *pattern* contains ``*``, ``?``, or ``[``."""
    return any(c in pattern for c in "*?[")


def _glob_paths(repo_root: Path, pattern: str) -> list[Path]:
    """Expand *pattern* under *repo_root* via Path.glob."""
    return list(repo_root.glob(pattern))


def compute_default_globs(module_id: str, package: str) -> list[str]:
    """Return the three convention globs for *module_id* in *package*.

    Covers the standard robotsix repo layout:
    - ``src/<package>/<module_id>/**``
    - ``tests/<module_id>/**``
    - ``docs/<module_id>/**``
    """
    return [
        f"src/{package}/{module_id}/**",
        f"tests/{module_id}/**",
        f"docs/{module_id}/**",
    ]


# ---------------------------------------------------------------------------
# Repo-health exclusions
# ---------------------------------------------------------------------------
#
# A module taxonomy is an inventory of a repository's LOGICAL MODULES — their
# descriptions, the files they own, and the dependencies between them. Linter
# configs, CI workflows, licence texts and per-PR changelog fragments are none
# of those things. They are repo health: uniform scaffolding that says nothing
# about how the software is decomposed.
#
# Requiring them to be claimed anyway produced measurable cost. On
# robotsix-central-deploy, 404 of 658 tracked files (61%) are scaffolding, so
# most of the taxonomy describes something other than modules. Worse, towncrier
# writes one fragment file PER PULL REQUEST, so every changelog entry became a
# taxonomy edit — and when a repo enumerated fragments instead of globbing them,
# "register this fragment in docs/modules.yaml" became a recurring ticket class.
# One such ticket sat blocked for a week; its branch proposed 199 explicit
# fragment entries.
#
# These defaults remove that class. They are deliberately conservative: only
# paths that are unambiguously repo scaffolding, never anything under src/ or
# tests/.
DEFAULT_EXCLUDED_PATHS: tuple[str, ...] = (
    # Forge configuration and automation
    ".github/**",
    ".gitlab/**",
    # Per-PR changelog fragments (towncrier and friends)
    "changelog.d/**",
    "changelog/**",
    "newsfragments/**",
    # Lint / format / type-check tooling configuration
    ".pre-commit-config.yaml",
    ".markdownlint-cli2.yaml",
    ".markdownlint.yaml",
    ".yamllint",
    ".yamllint.yaml",
    ".hadolint.yaml",
    ".editorconfig",
    ".vale.ini",
    ".stylelintrc*",
    ".eslintrc*",
    "eslint.config.*",
    ".prettierrc*",
    # Security / supply-chain tool configuration
    ".trivyignore",
    ".secrets.baseline",
    ".lycheeignore",
    # Toolchain pins
    ".nvmrc",
    ".python-version",
    ".dockerignore",
    ".gitignore",
    ".gitattributes",
    # Community health files
    "LICENSE*",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "CHANGELOG.md",
    # Mill's own per-repo control files
    ".robotsix-mill/**",
    # Packaging and dependency manifests
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "uv.lock",
    "package.json",
    "package-lock.json",
    "CITATION.cff",
    ".release-please-manifest.json",
    "release-please-config.json",
    # Build, run and deploy descriptors
    "Dockerfile",
    "Dockerfile.*",
    "docker-compose*.yml",
    "docker-compose*.yaml",
    "Makefile",
    "justfile",
    # Documentation tooling
    "mkdocs.yml",
    "README.md",
    "AGENT.md",
    "AGENTS.md",
    # Coverage and scanning configuration
    "codecov.yml",
    ".codecov.yml",
    ".gitleaks.toml",
    ".markdownlint.json",
    "vulture_whitelist.py",
    # Sample environment files — templates, never loaded at runtime
    ".env.example",
    ".env.*.example",
)


def is_excluded(path: str, patterns: Sequence[str]) -> bool:
    """True when repo-relative *path* matches any glob in *patterns*.

    Uses :meth:`PurePath.full_match`, so ``**`` crosses directory separators
    exactly as it does in module ``paths`` — ``.github/**`` covers nested
    workflow files, and the two path languages stay identical. (Available
    unconditionally: this package requires Python >= 3.14.)
    """
    candidate = PurePosixPath(path)
    return any(candidate.full_match(pattern) for pattern in patterns)
