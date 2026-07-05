"""Command-line entry points for robotsix-modules."""

from __future__ import annotations

import argparse
import dataclasses
import json
import logging
import sys
from collections.abc import Callable, Generator
from pathlib import Path
from typing import Any

from robotsix_modules import __version__, validate
from robotsix_modules._exceptions import (
    ConfigFileNotFoundError,
    ConfigParseError,
    ConfigStructureError,
    GitOperationError,
)
from robotsix_modules._yaml import (
    YamlParseError as _YamlParseError,
)
from robotsix_modules._yaml import (
    YamlReadError as _YamlReadError,
)
from robotsix_modules._yaml import read_yaml_file
from robotsix_modules.cli._exit_codes import ExitCode
from robotsix_modules.validation import (
    check_coverage,
    check_registration,
    validate_paths,
)

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
        target = Path(path)
        if not target.exists():
            raise ConfigFileNotFoundError(f"file not found: {path}")
        result = read_yaml_file(target)
        logger.debug("loaded %d top-level keys from %s", len(result), path)
        return result
    except ConfigFileNotFoundError:
        if label:
            logger.error("%s file not found: %s", label, path)
        else:
            logger.error("file not found: %s", path)
        return None
    except (
        _YamlReadError,
        _YamlParseError,
        ConfigParseError,
        ConfigStructureError,
    ) as exc:
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
) -> ExitCode:
    """Shared load -> compute -> output -> exit-code skeleton for the handlers.

    Loads the taxonomy YAML (exit code 2 on failure), runs ``compute`` to
    produce the result items, then emits them as JSON (under ``json_key``) or
    text. ``compute`` returns the item list, or ``None`` to signal exit code 2
    (its own diagnostic already printed).
    """
    taxonomy = _safe_load_yaml(path)
    if taxonomy is None:
        return ExitCode.FATAL

    logger.info("validating %s", path)
    items = compute(taxonomy)
    if items is None:
        return ExitCode.FATAL

    if output_format == "json":
        json.dump({json_key: [serialize(item) for item in items]}, sys.stdout)
        return ExitCode.ERRORS if items else ExitCode.OK
    if items:
        for item in items:
            print(text_value(item), file=sys.stderr)
        return ExitCode.ERRORS
    return ExitCode.OK


def _validate_one(
    path: str, schema_path: str | None, output_format: str = "text", *, root: str = "."
) -> ExitCode:
    """Validate a single taxonomy file. Return the process exit code."""

    taxonomy = _safe_load_yaml(path)
    if taxonomy is None:
        return ExitCode.FATAL

    schema: dict[str, Any] | None = None
    if schema_path is not None:
        schema = _safe_load_yaml(schema_path, label="schema")
        if schema is None:
            return ExitCode.FATAL

    logger.info("validating %s", path)
    schema_errors = validate(taxonomy, schema=schema)
    coverage_errors = check_coverage(taxonomy, Path(root))

    all_errors = schema_errors + coverage_errors

    if output_format == "json":
        json.dump({"errors": all_errors}, sys.stdout)
        return ExitCode.ERRORS if all_errors else ExitCode.OK

    if all_errors:
        for message in all_errors:
            print(message, file=sys.stderr)
        return ExitCode.ERRORS
    return ExitCode.OK


def _migrate_one(path: str, *, in_place: bool) -> ExitCode:
    """Migrate *path* to convention-first format. Return exit code."""
    import yaml

    from robotsix_modules.validation.registration import compute_default_globs

    taxonomy = _safe_load_yaml(path)
    if taxonomy is None:
        return ExitCode.FATAL

    package: str | None = taxonomy.get("package")
    if package is None:
        logger.warning("no 'package' field in %s — nothing to migrate", path)
        output = yaml.dump(
            taxonomy,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
        )
        print(output, end="")
        return ExitCode.OK

    for module_entry in taxonomy.get("modules", []):
        defaults = set(compute_default_globs(module_entry["id"], package))
        existing: list[str] = module_entry.get("paths") or []
        remaining = [p for p in existing if p not in defaults]
        if not remaining:
            module_entry.pop("paths", None)
        elif remaining != existing:
            module_entry["paths"] = remaining

    output = yaml.dump(
        taxonomy,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
    )
    if in_place:
        Path(path).write_text(output, encoding="utf-8")
        print(f"Wrote simplified taxonomy to {path}", file=sys.stderr)
    else:
        print(output, end="")
    return ExitCode.OK


def _check_registration_one(
    path: str, root: str, output_format: str = "text"
) -> ExitCode:
    """Run registration check on one taxonomy file. Return exit code."""

    def compute(taxonomy: dict[str, Any]) -> list[Any] | None:
        try:
            return check_registration(taxonomy, Path(root))
        except GitOperationError as exc:
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


def _validate_paths_one(path: str, root: str, output_format: str = "text") -> ExitCode:
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
    validate_parser.add_argument(
        "--root",
        default=".",
        help="Repository root directory (default: .).",
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

    migrate_parser = subparsers.add_parser(
        "migrate",
        help=(
            "Rewrite a modules.yaml to strip path entries covered by "
            "convention defaults. NOTE: YAML comments are not preserved."
        ),
    )
    migrate_parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (-v for info, -vv for debug).",
    )
    migrate_parser.add_argument(
        "modules_yaml",
        metavar="modules.yaml",
        help="Path to the taxonomy YAML file.",
    )
    migrate_parser.add_argument(
        "--in-place",
        action="store_true",
        default=False,
        help="Overwrite the input file instead of printing to stdout.",
    )

    return parser


def main(argv: list[str] | None = None) -> ExitCode:
    """Top-level CLI: ``robotsix-modules``."""
    parser = _build_parser()
    args = parser.parse_args(argv)
    _configure_logging(args.verbose)
    if args.command == "validate":
        return _validate_one(args.path, args.schema, args.output_format, root=args.root)
    if args.command == "check-registration":
        return _check_registration_one(args.modules_yaml, args.root, args.output_format)
    if args.command == "validate-paths":
        return _validate_paths_one(args.modules_yaml, args.root, args.output_format)
    if args.command == "migrate":
        return _migrate_one(args.modules_yaml, in_place=args.in_place)
    parser.error(f"unknown command: {args.command}")  # pragma: no cover
    return ExitCode.FATAL  # pragma: no cover - argparse exits before reaching here


def _validate_paths(
    paths: list[str], schema_path: str | None
) -> Generator[tuple[ExitCode, list[str]]]:
    """Yield ``(exit_code, errors)`` for each taxonomy path.

    *exit_code* is ``FATAL`` when the taxonomy or schema file cannot be
    loaded (the error is already logged by ``_safe_load_yaml``),
    ``ERRORS`` when validation errors are found, or ``OK`` for a clean pass.
    """
    for path in paths:
        taxonomy = _safe_load_yaml(path)
        if taxonomy is None:
            yield ExitCode.FATAL, []
            continue
        schema: dict[str, Any] | None = None
        if schema_path is not None:
            schema = _safe_load_yaml(schema_path, label="schema")
            if schema is None:
                yield ExitCode.FATAL, []
                continue
        errors = validate(taxonomy, schema=schema)
        yield (ExitCode.ERRORS if errors else ExitCode.OK), errors


def validate_main(argv: list[str] | None = None) -> ExitCode:
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
    parser.add_argument(
        "--root",
        default=".",
        help="Repository root directory (default: .).",
    )
    args = parser.parse_args(argv)

    _configure_logging(args.verbose)

    exit_code: ExitCode = ExitCode.OK
    all_errors: list[str] = []

    for path_code, errors in _validate_paths(args.paths, args.schema):
        exit_code = max(exit_code, path_code)
        if args.output_format == "json":
            all_errors.extend(errors)
        else:
            for message in errors:
                print(message, file=sys.stderr)

    # Supplement schema validation with a coverage check (once, not per-path).
    if exit_code != ExitCode.FATAL:
        coverage_errors: list[str] = []
        for path in args.paths:
            taxonomy = _safe_load_yaml(path)
            if taxonomy is not None:
                coverage_errors.extend(check_coverage(taxonomy, Path(args.root)))
                break  # only need one valid taxonomy for coverage
        if coverage_errors:
            exit_code = ExitCode.ERRORS
            if args.output_format == "json":
                all_errors.extend(coverage_errors)
            else:
                for msg in coverage_errors:
                    print(msg, file=sys.stderr)

    if args.output_format == "json":
        json.dump({"errors": all_errors}, sys.stdout)

    return exit_code


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
