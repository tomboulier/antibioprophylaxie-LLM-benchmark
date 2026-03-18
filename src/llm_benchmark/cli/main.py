"""CLI entry point for llm-benchmark.

Provides subcommands: run, list, compare.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import dotenv


def build_parser() -> argparse.ArgumentParser:
    """Build and return the top-level argument parser.

    Returns
    -------
    argparse.ArgumentParser
        Configured parser with run, list, and compare subcommands.
    """
    parser = argparse.ArgumentParser(
        prog="llm-benchmark",
        description="Evaluate LLM approaches on medical question datasets.",
    )
    subparsers = parser.add_subparsers(dest="command")

    _add_run_subcommand(subparsers)
    _add_list_subcommand(subparsers)
    _add_compare_subcommand(subparsers)

    return parser


def _add_run_subcommand(subparsers: argparse._SubParsersAction) -> None:
    run_parser = subparsers.add_parser("run", help="Run a benchmark evaluation.")
    run_parser.add_argument("--dataset", required=True, help="Path to the dataset JSON file.")
    run_parser.add_argument(
        "--approach",
        dest="approach",
        action="append",
        required=True,
        help="Approach identifier (repeatable).",
    )
    run_parser.add_argument(
        "--model",
        dest="model",
        action="append",
        required=True,
        help="Model identifier (repeatable).",
    )
    run_parser.add_argument(
        "--questions",
        nargs="+",
        default=None,
        help="Subset of question IDs to evaluate.",
    )
    run_parser.add_argument(
        "--output-dir",
        default=None,
        help="Directory where results will be written.",
    )
    run_parser.add_argument(
        "--config",
        default=None,
        help="Path to a YAML config file (overrides other flags).",
    )


def _add_list_subcommand(subparsers: argparse._SubParsersAction) -> None:
    list_parser = subparsers.add_parser("list", help="List available resources.")
    list_subparsers = list_parser.add_subparsers(dest="resource")
    list_subparsers.add_parser("models", help="List available LLM models.")
    list_subparsers.add_parser("approaches", help="List available approaches.")
    list_subparsers.add_parser("datasets", help="List available datasets.")


def _add_compare_subcommand(subparsers: argparse._SubParsersAction) -> None:
    compare_parser = subparsers.add_parser("compare", help="Compare multiple run results.")
    compare_parser.add_argument(
        "--runs",
        nargs="+",
        required=True,
        help="Paths to JSON result files to compare.",
    )
    compare_parser.add_argument(
        "--output",
        default=None,
        help="Path for the output CSV report.",
    )


def main(argv: list[str] | None = None) -> None:
    """Parse arguments and dispatch to the appropriate handler.

    Parameters
    ----------
    argv : list[str] or None, optional
        Argument list. Defaults to ``sys.argv[1:]`` when ``None``.
    """
    try:
        dotenv.load_dotenv(override=False)
    except ValueError as error:
        print(f"Error: could not parse .env file: {error}", file=sys.stderr)
        sys.exit(1)

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        _handle_run(args)
    elif args.command == "list":
        _handle_list(args)
        sys.exit(0)
    elif args.command == "compare":
        _handle_compare(args)
    else:
        parser.print_help()
        sys.exit(1)


def _handle_run(args: argparse.Namespace) -> None:
    """Dispatch the run subcommand.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed CLI arguments.
    """
    print(
        f"Running benchmark: dataset={args.dataset}, "
        f"approaches={args.approach}, models={args.model}"
    )
    print("(Full run execution requires wiring — use the Python API for now.)")


def _handle_list(args: argparse.Namespace) -> None:
    """Dispatch the list subcommand.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed CLI arguments.
    """
    if args.resource == "models":
        from llm_benchmark.adapters.llms import LLM_REGISTRY

        for model_id in sorted(LLM_REGISTRY):
            print(model_id)

    elif args.resource == "approaches":
        from llm_benchmark.adapters.approaches import APPROACH_REGISTRY

        for approach_id in sorted(APPROACH_REGISTRY):
            print(approach_id)

    elif args.resource == "datasets":
        _list_datasets()

    else:
        print("Available resources: models, approaches, datasets")
        sys.exit(1)


def _list_datasets() -> None:
    """Print dataset IDs discovered under the datasets/ directory."""
    datasets_dir = Path("datasets")
    if not datasets_dir.exists():
        print("No datasets directory found.")
        return
    for dataset_dir in sorted(datasets_dir.iterdir()):
        if dataset_dir.is_dir():
            print(dataset_dir.name)


def _handle_compare(args: argparse.Namespace) -> None:
    """Dispatch the compare subcommand.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed CLI arguments.
    """
    print(f"Comparing runs: {args.runs}")
    print("(Full compare execution requires wiring — use the Python API for now.)")
