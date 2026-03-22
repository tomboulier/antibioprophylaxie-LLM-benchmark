"""Thin CLI entry point for the LLM benchmark.

Delegates entirely to the hexagonal architecture — no provider SDK imports,
no duplicated domain logic.

Usage
-----
Run a single model::

    uv run python scripts/run_benchmark.py --model mistral-large-latest

Run multiple models (comparative summary printed at the end)::

    uv run python scripts/run_benchmark.py -m gpt-4o -m mistral-large-latest

List available models::

    uv run python scripts/run_benchmark.py --list-models

Filter to specific questions::

    uv run python scripts/run_benchmark.py -m gpt-4o --questions Q01,Q05,Q16

API keys are read from environment variables by LiteLLM (ANTHROPIC_API_KEY,
OPENAI_API_KEY, MISTRAL_API_KEY, …).

Results are saved to ``research/results/<run_id>.json``.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from llm_benchmark.adapters.approaches.simple_prompt import SimplePromptApproach
from llm_benchmark.adapters.exports.json_export import JsonExportAdapter
from llm_benchmark.adapters.llms import LLM_REGISTRY
from llm_benchmark.domain.dataset_loader import load_dataset
from llm_benchmark.domain.engine import BenchmarkEngine
from llm_benchmark.domain.entities import RunResult
from llm_benchmark.domain.value_objects import QuestionId

DATASET_PATH = Path("datasets/sfar_antibioprophylaxie/benchmark.json")
OUTPUT_DIR = Path("research/results")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns
    -------
    argparse.Namespace
        Parsed arguments with ``models``, ``list_models``, and ``questions``.
    """
    parser = argparse.ArgumentParser(
        description="Benchmark LLM models on the SFAR antibiotic prophylaxis dataset."
    )
    parser.add_argument(
        "--model",
        "-m",
        action="append",
        dest="models",
        metavar="MODEL",
        help="Model alias to benchmark (repeatable). See --list-models.",
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="Print available model aliases and exit.",
    )
    parser.add_argument(
        "--questions",
        "-q",
        type=str,
        default=None,
        metavar="IDS",
        help="Comma-separated question IDs to run (e.g. Q01,Q05,Q16).",
    )
    return parser.parse_args()


def print_comparison(run_results: list[RunResult]) -> None:
    """Print a comparative summary table for multiple run results.

    Parameters
    ----------
    run_results : list[RunResult]
        Results from two or more benchmark runs to compare.
    """
    if len(run_results) < 2:
        return

    separator = "=" * 60
    print(f"\n{separator}")
    print("  MODEL COMPARISON")
    print(f"{separator}\n")

    header = f"  {'Model':<30} {'Correct':>8} {'Accuracy':>10}"
    print(header)
    print(f"  {'-' * 50}")

    sorted_results = sorted(
        run_results,
        key=lambda result: result.summary.accuracy.value,
        reverse=True,
    )
    for result in sorted_results:
        summary = result.summary
        model_name = result.model_id.value
        print(
            f"  {model_name:<30} {summary.correct:>4}/{summary.total:<3}"
            f" {summary.accuracy.value:>9.0%}"
        )

    print("\n  By question type:")
    all_types = sorted(
        {question_type for result in run_results for question_type in result.summary.by_type}
    )
    for question_type in all_types:
        print(f"    {question_type.upper():<6}", end="  ")
        for result in run_results:
            stats = result.summary.by_type.get(question_type, {})
            accuracy = stats.get("accuracy", 0.0)
            print(f"{result.model_id.value}: {accuracy:.0%}", end="  ")
        print()


def main() -> None:
    """Entry point — parse args, run benchmark, export results.

    Returns
    -------
    None
    """
    args = parse_args()

    if args.list_models:
        print("\nAvailable models:\n")
        for model_name in sorted(LLM_REGISTRY.keys()):
            print(f"  {model_name}")
        print("\nUsage: uv run python scripts/run_benchmark.py -m <model> [-m <model> ...]\n")
        sys.exit(0)

    if not args.models:
        print(
            "Error: at least one --model is required (or use --list-models).",
            file=sys.stderr,
        )
        sys.exit(1)

    # Validate every requested model against the registry
    unknown_models = [model for model in args.models if model not in LLM_REGISTRY]
    if unknown_models:
        print(
            f"Error: unknown model(s): {', '.join(unknown_models)}. "
            "Run --list-models to see available models.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Load dataset — exit with a clear message when the file is missing
    if not DATASET_PATH.exists():
        print(
            f"Error: dataset not found at {DATASET_PATH}.",
            file=sys.stderr,
        )
        print(
            "Run first: uv run python scripts/benchmark_md_to_json.py",
            file=sys.stderr,
        )
        sys.exit(1)

    dataset = load_dataset(DATASET_PATH)

    # Convert comma-separated question IDs to QuestionId list (or None = all)
    question_ids: list[QuestionId] | None = None
    if args.questions:
        question_ids = [QuestionId(qid.strip()) for qid in args.questions.split(",") if qid.strip()]

    approach = SimplePromptApproach()
    llm_adapters = [LLM_REGISTRY[model_name] for model_name in args.models]
    engine = BenchmarkEngine()

    print("\nLLM Benchmark — SFAR Antibiotic Prophylaxis")
    print(f"Dataset : {dataset.id.value} v{dataset.version.value}")
    print(f"Models  : {', '.join(args.models)}")
    if question_ids:
        print(f"Filter  : {', '.join(qid.value for qid in question_ids)}")

    run_results = engine.run(dataset, [approach], llm_adapters, question_ids)

    export_adapter = JsonExportAdapter()
    for result in run_results:
        output_path = export_adapter.export(result, OUTPUT_DIR)
        print(f"Results saved: {output_path}")

    if len(run_results) > 1:
        print_comparison(run_results)


if __name__ == "__main__":
    main()
