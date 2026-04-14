"""Lancer une expérience complète de benchmark en une commande.

Controller CLI mince : charge le .env et délègue au use case.

Usage
-----
    uv run python scripts/run_experiment.py

Les modèles activés sont définis dans ``config/models.yaml`` (champ ``enabled``).
Les résultats sont écrits dans ``research/results/`` et ``research/figures/``.
"""

from __future__ import annotations

from pathlib import Path

import dotenv

from llm_benchmark.usecases.run_experiment import RunExperiment

DATASET_PATH = Path("datasets/sfar_antibioprophylaxie/benchmark.json")
OUTPUT_DIR = Path("research/results")
FIGURES_DIR = Path("research/figures")


def main() -> None:
    dotenv.load_dotenv(override=False)

    experiment = RunExperiment(
        dataset_path=DATASET_PATH,
        output_dir=OUTPUT_DIR,
        figures_dir=FIGURES_DIR,
    )
    experiment.execute()


if __name__ == "__main__":
    main()
