"""Use case : exécuter une expérience complète de benchmark.

Orchestre les étapes séquentielles du pipeline :
1. Charger le dataset et les modèles activés
2. Lancer le benchmark sur chaque modèle
3. Exporter les résultats en JSON
4. Générer les figures comparatives
5. Afficher le récapitulatif

Chaque étape est une méthode typée. ``execute()`` les chaîne.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from llm_benchmark.adapters.approaches.simple_prompt import SimplePromptApproach
from llm_benchmark.adapters.exports.json_export import JsonExportAdapter
from llm_benchmark.adapters.llms import ENABLED_REGISTRY
from llm_benchmark.domain.dataset_loader import load_dataset
from llm_benchmark.domain.engine import BenchmarkEngine
from llm_benchmark.domain.entities import Dataset, RunResult
from llm_benchmark.ports.llm import LLMPort


@dataclass
class ExperimentReport:
    """Résultat complet d'une expérience.

    Parameters
    ----------
    dataset : Dataset
        Le dataset utilisé.
    run_results : list[RunResult]
        Un résultat par modèle.
    result_paths : list[Path]
        Chemins vers les fichiers JSON exportés.
    figure_paths : list[Path]
        Chemins vers les figures PNG générées.
    """

    dataset: Dataset
    run_results: list[RunResult]
    result_paths: list[Path]
    figure_paths: list[Path]


class RunExperiment:
    """Use case : pipeline complet d'expérience benchmark.

    Parameters
    ----------
    dataset_path : Path
        Chemin vers le fichier JSON du dataset.
    output_dir : Path
        Répertoire de sortie pour les résultats JSON.
    figures_dir : Path
        Répertoire de sortie pour les figures PNG.
    """

    def __init__(
        self,
        dataset_path: Path,
        output_dir: Path,
        figures_dir: Path,
    ) -> None:
        self._dataset_path = dataset_path
        self._output_dir = output_dir
        self._figures_dir = figures_dir

    def execute(self) -> ExperimentReport:
        """Exécuter le pipeline complet.

        Returns
        -------
        ExperimentReport
            Résultat agrégé de l'expérience.
        """
        dataset, llms = self._step_load()
        run_results = self._step_benchmark(dataset, llms)
        result_paths = self._step_export(run_results)
        figure_paths = self._step_figures(run_results)
        self._step_summary(run_results)

        return ExperimentReport(
            dataset=dataset,
            run_results=run_results,
            result_paths=result_paths,
            figure_paths=figure_paths,
        )

    # ------------------------------------------------------------------
    # Étapes du pipeline
    # ------------------------------------------------------------------

    def _step_load(self) -> tuple[Dataset, list[LLMPort]]:
        """Étape 1 : charger le dataset et les modèles activés."""
        dataset = load_dataset(self._dataset_path)
        llms = list(ENABLED_REGISTRY.values())

        if not llms:
            msg = (
                "Aucun modèle activé dans config/models.yaml. "
                "Ajouter 'enabled: true' à au moins un modèle."
            )
            raise RuntimeError(msg)

        model_names = [llm.model_id.value for llm in llms]
        print(f"\n{'=' * 60}")
        print("  EXPÉRIENCE BENCHMARK")
        print(f"{'=' * 60}")
        print(f"\n  Dataset  : {dataset.id.value} v{dataset.version.value}")
        print(f"  Questions: {len(dataset.questions)}")
        print(f"  Modèles  : {', '.join(model_names)}")
        print()

        return dataset, llms

    def _step_benchmark(
        self,
        dataset: Dataset,
        llms: list[LLMPort],
    ) -> list[RunResult]:
        """Étape 2 : lancer le benchmark sur chaque modèle."""
        approach = SimplePromptApproach()
        engine = BenchmarkEngine()
        return engine.run(dataset, [approach], llms)

    def _step_export(self, run_results: list[RunResult]) -> list[Path]:
        """Étape 3 : exporter les résultats en JSON."""
        export = JsonExportAdapter()
        paths = []
        for result in run_results:
            path = export.export(result, self._output_dir)
            print(f"  Résultats : {path}")
            paths.append(path)
        return paths

    def _step_figures(self, run_results: list[RunResult]) -> list[Path]:
        """Étape 4 : générer les figures comparatives."""
        from llm_benchmark.adapters.exports.figures import generate_figures

        return generate_figures(run_results, self._figures_dir)

    def _step_summary(self, run_results: list[RunResult]) -> None:
        """Étape 5 : afficher le récapitulatif dans le terminal."""
        if len(run_results) < 2:
            return

        print(f"\n{'=' * 60}")
        print("  COMPARAISON DES MODÈLES")
        print(f"{'=' * 60}\n")

        header = f"  {'Modèle':<30} {'Correct':>8} {'Précision':>10}"
        print(header)
        print(f"  {'-' * 50}")

        sorted_results = sorted(
            run_results,
            key=lambda r: r.summary.accuracy.value,
            reverse=True,
        )
        for result in sorted_results:
            s = result.summary
            print(
                f"  {result.model_id.value:<30} {s.correct:>4}/{s.total:<3}"
                f" {s.accuracy.value:>9.0%}"
            )

        print("\n  Par type de question :")
        all_types = sorted(
            {qt for r in run_results for qt in r.summary.by_type}
        )
        for question_type in all_types:
            print(f"    {question_type.upper():<6}", end="  ")
            for result in sorted_results:
                stats = result.summary.by_type.get(question_type, {})
                acc = stats.get("accuracy", 0.0)
                print(f"{result.model_id.value}: {acc:.0%}", end="  ")
            print()

        print()
