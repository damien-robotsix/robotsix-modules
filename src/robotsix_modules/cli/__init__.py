"""Command-line entry points for robotsix-modules."""

from __future__ import annotations

import argparse
import dataclasses
import json
import logging
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast

import yaml

from robotsix_modules import __version__, validate
from robotsix_modules.validation import check_registration, validate_paths

PROG = "robotsix-modules"

logger = logging.getLogger("robotsix_modules")


def _configure_logging(verbosity: int) -> None:
    """Map a verbosity count to a logging level and add a stderr handler."""
    level = logging.WARNING
    if verbosity >= 2:
        level = logging.DEBUG
    elif verbosity >= 1:
        level = logging.INFO
    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(message)s",
        stream=sys.stderr,
        force=True,
    )


def _safe_load_yaml(path: str | Path, label: str = "") -> dict[str, Any] | None:
    """Load a YAML file, logging a user-friendly error on failure.

    Returns the parsed dict on success, or None on failure (error already logged).
    """
    try:
        logger.info("loading %s", path)
        result = cast(
            dict[str, Any],
            yaml.safe_load(Path(path).read_text(encoding="utf-8")),
        )
        logger.debug("loaded %d top-level keys from %s", len(result), path)
        return result
    except FileNotFoundError:
        if label:
            logger.error("%s file not found: %s", label, path)
        else:
            logger.error("file not found: %s", path)
        return None
    except yaml.YAMLError as exc:
        if label:
            logger.error("invalid YAML in %s %s: %s", label, path, exc)
        else:
            logger.error("invalid YAML in %s: %s", path, exc)
        return None


def _run_one(
    path: str,
    output_format: str,
    compute: Callable[[dict[str, Any]], list[Any] | None],
    *,
    json_key: str,
    serialize: Callable[[Any], Any],
    text_value: Callable[[Any], Any],
) -> int:
    """Shared load -> compute -> output -> exit-code skeleton for the handlers.

    Loads the taxonomy YAML (exit code 2 on failure), runs ``compute`` to
    produce the result items, then emits them as JSON (under ``json_key``) or
    text. ``compute`` returns the item list, or ``None`` to signal exit code 2
    (its own diagnostic already printed).
    """
    taxonomy = _safe_load_yaml(path)
    if taxonomy is None:
        return 2

    logger.info("validating %s", path)
    items = compute(taxonomy)
    if items is None:
        return 2

    if output_format == "json":
        json.dump({json_key: [serialize(item) for item in items]}, sys.stdout)
        return 1 if items else 0
    if items:
        for item in items:
            print(text_value(item), file=sys.stderr)
        return 1
    return 0


def _validate_one(
    path: str, schema_path: str | None, output_format: str = "text"
) -> int:
    """Validate a single taxonomy file. Return the process exit code."""

    def compute(taxonomy: dict[str, Any]) -> list[Any] | None:
        schema: dict[str, Any] | None = None
        if schema_path is not None:
            schema = _safe_load_yaml(schema_path, label="schema")
            if schema is None:
                return None
        return validate(taxonomy, schema=schema)

    return _run_one(
        path,
        output_format,
        compute,
        json_key="errors",
        serialize=lambda message: message,
        text_value=lambda message: message,
    )


def _check_registration_one(path: str, root: str, output_format: str = "text") -> int:
    """Run registration check on one taxonomy file. Return exit code."""

    def compute(taxonomy: dict[str, Any]) -> list[Any] | None:
        try:
            return check_registration(taxonomy, Path(root))
        except RuntimeError as exc:
            logger.error("%s", exc)
            return None

    return _run_one(
        path,
        output_format,
        compute,
        json_key="findings",
        serialize=dataclasses.asdict,
        text_value=lambda f: f.message,
    )


def _validate_paths_one(path: str, root: str, output_format: str = "text") -> int:
    """Run path validation on one taxonomy file. Return exit code."""
    return _run_one(
        path,
        output_format,
        lambda taxonomy: validate_paths(taxonomy, Path(root)),
        json_key="findings",
        serialize=dataclasses.asdict,
        text_value=lambda f: f.message,
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog=PROG)
    parser.add_argument(
        "--version",
        action="version",
        version=f"{PROG} {__version__}",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser(
        "validate", help="Validate a module-taxonomy file."
    )
    validate_parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (-v for info, -vv for debug).",
    )
    validate_parser.add_argument("path", help="Path to the taxonomy YAML file.")
    validate_parser.add_argument(
        "--schema",
        dest="schema",
        default=None,
        help="Override the bundled JSON Schema with the given file.",
    )
    validate_parser.add_argument(
        "--output-format",
        choices=["text", "json"],
        default="text",
        help="Output format for findings (default: text).",
    )

    check_reg_parser = subparsers.add_parser(
        "check-registration",
        help="Check that every tracked file is claimed by exactly one module.",
    )
    check_reg_parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (-v for info, -vv for debug).",
    )
    check_reg_parser.add_argument(
        "modules_yaml",
        metavar="modules.yaml",
        help="Path to the taxonomy YAML file.",
    )
    check_reg_parser.add_argument(
        "--root",
        default=".",
        help="Repository root directory (default: .).",
    )
    check_reg_parser.add_argument(
        "--output-format",
        choices=["text", "json"],
        default="text",
        help="Output format for findings (default: text).",
    )

    validate_paths_parser = subparsers.add_parser(
        "validate-paths",
        help="Check that every module path entry resolves to at least one file.",
    )
    validate_paths_parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (-v for info, -vv for debug).",
    )
    validate_paths_parser.add_argument(
        "modules_yaml",
        metavar="modules.yaml",
        help="Path to the taxonomy YAML file.",
    )
    validate_paths_parser.add_argument(
        "--root",
        default=".",
        help="Repository root directory (default: .).",
    )
    validate_paths_parser.add_argument(
        "--output-format",
        choices=["text", "json"],
        default="text",
        help="Output format for findings (default: text).",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    """Top-level CLI: ``robotsix-modules``."""
    parser = _build_parser()
    args = parser.parse_args(argv)
    _configure_logging(args.verbose)
    if args.command == "validate":
        return _validate_one(args.path, args.schema, args.output_format)
    if args.command == "check-registration":
        return _check_registration_one(args.modules_yaml, args.root, args.output_format)
    if args.command == "validate-paths":
        return _validate_paths_one(args.modules_yaml, args.root, args.output_format)
    parser.error(f"unknown command: {args.command}")
    return 2  # pragma: no cover - argparse exits before reaching here


def validate_main(argv: list[str] | None = None) -> int:
    """Lightweight pre-commit wrapper: ``robotsix-modules-validate``.

    Accepts one or more positional paths (pre-commit passes each matched
    file as a separate argument). Same exit-code semantics as
    ``robotsix-modules validate``.
    """
    parser = argparse.ArgumentParser(prog=f"{PROG}-validate")
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (-v for info, -vv for debug).",
    )
    parser.add_argument(
        "paths",
        nargs="+",
        help="One or more taxonomy YAML files to validate.",
    )
    parser.add_argument(
        "--schema",
        dest="schema",
        default=None,
        help="Override the bundled JSON Schema with the given file.",
    )
    parser.add_argument(
        "--output-format",
        choices=["text", "json"],
        default="text",
        help="Output format for findings (default: text).",
    )
    args = parser.parse_args(argv)

    _configure_logging(args.verbose)

    if args.output_format == "json":
        # Aggregate every path's error strings into ONE JSON document so the
        # whole invocation emits a single parseable object to stdout.
        exit_code = 0
        errors: list[str] = []
        for path in args.paths:
            taxonomy = _safe_load_yaml(path)
            if taxonomy is None:
                exit_code = max(exit_code, 2)
                continue
            schema: dict[str, Any] | None = None
            if args.schema is not None:
                schema = _safe_load_yaml(args.schema, label="schema")
                if schema is None:
                    exit_code = max(exit_code, 2)
                    continue
            path_errors = validate(taxonomy, schema=schema)
            if path_errors:
                errors.extend(path_errors)
                exit_code = max(exit_code, 1)
        json.dump({"errors": errors}, sys.stdout)
        return exit_code

    exit_code = 0
    for path in args.paths:
        code = _validate_one(path, args.schema, args.output_format)
        exit_code = max(exit_code, code)
    return exit_code


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
