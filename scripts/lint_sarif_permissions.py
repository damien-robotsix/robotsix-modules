#!/usr/bin/env python3
"""Validate that SARIF-uploading workflow files declare ``security-events: write``.

Reads the ``SARIF_WORKFLOWS`` env var (space-separated list of workflow
filenames relative to ``.github/workflows/``), parses each as YAML, and
checks that either the top-level ``permissions`` or every job's
``permissions`` includes ``security-events: write``.  Exits non-zero if any
workflow is missing the permission (or if the file cannot be read).
"""
import os
import sys
from pathlib import Path

import yaml

WORKFLOW_DIR = Path(".github/workflows")


def _check_permissions(permissions_block: object, label: str) -> bool:
    """Return True if *permissions_block* grants ``security-events: write``."""
    if isinstance(permissions_block, dict):
        se = permissions_block.get("security-events")
        if se is not None and se not in ("write", "read"):
            print(
                f"ERROR: {label} has security-events={se!r} (expected 'write')",
                file=sys.stderr,
            )
            return False
        return se == "write"
    # ``permissions: read-all`` or ``permissions: write-all``
    if isinstance(permissions_block, str):
        return permissions_block == "write-all"
    return False


def check_workflow(path: Path) -> bool:
    """Return True if *path*'s workflow has ``security-events: write``."""
    try:
        doc = yaml.safe_load(path.read_text())
    except Exception as exc:
        print(f"ERROR: cannot parse {path}: {exc}", file=sys.stderr)
        return False

    if not isinstance(doc, dict):
        print(f"ERROR: {path} is not a mapping", file=sys.stderr)
        return False

    # Top-level permissions
    top_ok = False
    top_perms = doc.get("permissions")
    if top_perms is not None:
        top_ok = _check_permissions(top_perms, f"{path} (top-level permissions)")

    jobs = doc.get("jobs")
    if not isinstance(jobs, dict):
        if top_ok:
            return True
        print(f"ERROR: {path} has no jobs and no security-events: write", file=sys.stderr)
        return False

    if top_ok:
        return True  # top-level covers everything

    all_ok = True
    for job_name, job in jobs.items():
        if not isinstance(job, dict):
            continue
        job_perms = job.get("permissions")
        if job_perms is not None:
            if not _check_permissions(job_perms, f"{path} / {job_name}"):
                all_ok = False
        else:
            print(
                f"ERROR: {path} / {job_name} has no permissions and top-level "
                f"does not grant security-events: write",
                file=sys.stderr,
            )
            all_ok = False

    return all_ok


def main() -> int:
    sarif_workflows = os.environ.get("SARIF_WORKFLOWS", "").strip()
    if not sarif_workflows:
        print("SARIF_WORKFLOWS is empty — nothing to check", file=sys.stderr)
        return 0

    filenames = sarif_workflows.split()
    errors = False
    for filename in filenames:
        path = WORKFLOW_DIR / filename
        if not path.exists():
            print(f"WARNING: {path} does not exist — skipping", file=sys.stderr)
            continue
        if not check_workflow(path):
            errors = True

    if errors:
        print("\nOne or more SARIF workflows are missing security-events: write.", file=sys.stderr)
        return 1
    print("All SARIF workflows have security-events: write.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
