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
import importlib.util
import sys
from pathlib import Path

import dotenv

DATASET_DIR = Path("datasets/sfar_antibioprophylaxie")
DATASET_MD = DATASET_DIR / "benchmark.md"
DATASET_PATH = DATASET_DIR / "benchmark.json"
DATASET_CONVERTER = DATASET_DIR / "md_to_json.py"
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
        "--model",
        "-m",
        action="append",
        dest="models",
        metavar="MODEL",
        help="Modèle à évaluer (répétable). Sans -m, lance tous les modèles activés.",
    )
    run_parser.add_argument(
        "--questions",
        "-q",
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
    else:
        parser.print_help()
        sys.exit(1)


def _handle_run(args: argparse.Namespace) -> None:
    """Déléguer au use case RunExperiment."""
    from llm_benchmark.usecases.run_experiment import RunExperiment

    _ensure_dataset_json_fresh()

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


def _ensure_dataset_json_fresh() -> None:
    """Régénère ``benchmark.json`` si absent ou plus ancien que ``benchmark.md``.

    Le JSON est un artefact généré à partir du Markdown (source de vérité).
    Cette fonction garantit qu'il est à jour avant le chargement du dataset.
    Silencieuse si le Markdown source n'existe pas (dataset tiers).
    """
    if not DATASET_MD.exists():
        return

    json_stale = (
        not DATASET_PATH.exists() or DATASET_MD.stat().st_mtime > DATASET_PATH.stat().st_mtime
    )
    if not json_stale:
        return

    spec = importlib.util.spec_from_file_location("_sfar_md_to_json", DATASET_CONVERTER)
    if spec is None or spec.loader is None:
        msg = f"Impossible de charger le convertisseur : {DATASET_CONVERTER}"
        raise RuntimeError(msg)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    count = module.generate(DATASET_MD, DATASET_PATH)
    print(f"[dataset] benchmark.json régénéré ({count} questions)")


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
