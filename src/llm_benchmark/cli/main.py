"""CLI officielle pour llm-benchmark.

Point d'entrée unique. Délègue au use case RunExperiment.

Usage
-----
::

    llm-benchmark run                              # tous les modèles activés
    llm-benchmark run -m gpt-4o -m mistral-small   # modèles spécifiques
    llm-benchmark run -q Q01,Q05                   # questions spécifiques
    llm-benchmark list models                      # modèles disponibles
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import dotenv

DATASET_PATH = Path("datasets/sfar_antibioprophylaxie/benchmark.json")
OUTPUT_DIR = Path("research/results")
FIGURES_DIR = Path("research/figures")


def build_parser() -> argparse.ArgumentParser:
    """Construire le parser CLI avec sous-commandes run et list."""
    parser = argparse.ArgumentParser(
        prog="llm-benchmark",
        description="Évaluer des LLM sur les recommandations SFAR d'antibioprophylaxie.",
    )
    subparsers = parser.add_subparsers(dest="command")

    # --- run ---
    run_parser = subparsers.add_parser(
        "run",
        help="Lancer une expérience benchmark.",
    )
    run_parser.add_argument(
        "--model", "-m",
        action="append",
        dest="models",
        metavar="MODEL",
        help="Modèle à évaluer (répétable). Sans -m, lance tous les modèles activés.",
    )
    run_parser.add_argument(
        "--questions", "-q",
        type=str,
        default=None,
        metavar="IDS",
        help="IDs de questions séparés par des virgules (ex: Q01,Q05,Q16).",
    )

    # --- list ---
    list_parser = subparsers.add_parser("list", help="Lister les ressources disponibles.")
    list_subparsers = list_parser.add_subparsers(dest="resource")
    list_subparsers.add_parser("models", help="Lister les modèles LLM configurés.")

    return parser


def main(argv: list[str] | None = None) -> None:
    """Point d'entrée CLI."""
    dotenv.load_dotenv(override=False)

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        _handle_run(args)
    elif args.command == "list":
        _handle_list(args)
    else:
        parser.print_help()
        sys.exit(1)


def _handle_run(args: argparse.Namespace) -> None:
    """Déléguer au use case RunExperiment."""
    from llm_benchmark.usecases.run_experiment import RunExperiment

    question_ids = None
    if args.questions:
        question_ids = [q.strip() for q in args.questions.split(",") if q.strip()]

    experiment = RunExperiment(
        dataset_path=DATASET_PATH,
        output_dir=OUTPUT_DIR,
        figures_dir=FIGURES_DIR,
        model_ids=args.models,
        question_ids=question_ids,
    )
    experiment.execute()


def _handle_list(args: argparse.Namespace) -> None:
    """Lister les ressources disponibles."""
    if args.resource == "models":
        from llm_benchmark.adapters.llms import ENABLED_REGISTRY, LLM_REGISTRY

        print("\nModèles configurés :\n")
        for model_id in sorted(LLM_REGISTRY):
            enabled = model_id in ENABLED_REGISTRY
            marker = "  *" if enabled else "   "
            print(f"  {marker} {model_id}")
        print("\n  * = activé (enabled: true)\n")
    else:
        print("Ressources disponibles : models")
        sys.exit(1)
