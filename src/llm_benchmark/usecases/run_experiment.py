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

import json
import logging
from dataclasses import dataclass
from pathlib import Path

from llm_benchmark.adapters.approaches.simple_prompt import SimplePromptApproach
from llm_benchmark.adapters.exports.json_export import JsonExportAdapter
from llm_benchmark.adapters.llms import ENABLED_REGISTRY, LLM_REGISTRY
from llm_benchmark.domain.dataset_loader import load_dataset
from llm_benchmark.domain.engine import BenchmarkEngine
from llm_benchmark.domain.entities import Dataset, RunResult
from llm_benchmark.domain.value_objects import QuestionId
from llm_benchmark.ports.llm import LLMPort

logger = logging.getLogger(__name__)


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
    model_ids : list[str] or None
        Si fourni, lance uniquement ces modèles (override ``enabled``).
        Si ``None``, lance tous les modèles activés dans ``models.yaml``.
    question_ids : list[str] or None
        Si fourni, ne lance que ces questions (ex: ``["Q01", "Q05"]``).
    """

    def __init__(
        self,
        dataset_path: Path,
        output_dir: Path,
        figures_dir: Path,
        *,
        model_ids: list[str] | None = None,
        question_ids: list[str] | None = None,
    ) -> None:
        self._dataset_path = dataset_path
        self._output_dir = output_dir
        self._figures_dir = figures_dir
        self._model_ids = model_ids
        self._question_ids = question_ids

    def execute(self) -> ExperimentReport:
        """Exécuter le pipeline complet.

        Returns
        -------
        ExperimentReport
            Résultat agrégé de l'expérience.
        """
        dataset, llms = self._step_load()
        qids = (
            [QuestionId(q) for q in self._question_ids]
            if self._question_ids
            else None
        )
        run_results = self._step_benchmark(dataset, llms, qids)
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
        """Étape 1 : charger le dataset et résoudre les modèles."""
        dataset = load_dataset(self._dataset_path)

        if self._model_ids:
            unknown = [m for m in self._model_ids if m not in LLM_REGISTRY]
            if unknown:
                msg = (
                    f"Modèle(s) inconnu(s) : {', '.join(unknown)}. "
                    "Voir 'llm-benchmark list models'."
                )
                raise RuntimeError(msg)
            llms = [LLM_REGISTRY[m] for m in self._model_ids]
        else:
            llms = list(ENABLED_REGISTRY.values())

        if not llms:
            msg = (
                "Aucun modèle à lancer. Activer des modèles dans "
                "config/models.yaml ou en passer via --model."
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
        question_ids: list[QuestionId] | None = None,
    ) -> list[RunResult]:
        """Étape 2 : lancer le benchmark sur chaque modèle."""
        approach = SimplePromptApproach()
        engine = BenchmarkEngine()
        return engine.run(dataset, [approach], llms, question_ids)

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
        """Étape 4 : générer les figures comparatives.

        Combine les résultats du run en cours avec les derniers résultats
        disponibles sur disque pour les modèles non lancés, afin de
        toujours produire une figure comparative complète.
        """
        from llm_benchmark.adapters.exports.figures import generate_figures

        all_results = _load_latest_results(self._output_dir)

        # Les résultats du run en cours écrasent ceux sur disque
        for result in run_results:
            all_results[result.model_id.value] = result

        combined = list(all_results.values())
        return generate_figures(combined, self._figures_dir)

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
                f"  {result.model_id.value:<30} {s.correct:>4}/{s.answered:<3}"
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


def _load_latest_results(results_dir: Path) -> dict[str, RunResult]:
    """Charger le dernier fichier JSON par modèle depuis le disque.

    Parameters
    ----------
    results_dir : Path
        Répertoire contenant les fichiers JSON de résultats.

    Returns
    -------
    dict[str, RunResult]
        Dictionnaire model_id -> RunResult (le plus récent par modèle).
    """
    from datetime import datetime

    from llm_benchmark.domain.entities import (
        QuestionResult,
        RunSummary,
        ScoreResult,
    )
    from llm_benchmark.domain.value_objects import (
        Accuracy,
        ApproachId,
        CarbonFootprint,
        Cost,
        DatasetId,
        Latency,
        ModelId,
        QuestionType,
        RunId,
    )

    if not results_dir.exists():
        return {}

    latest: dict[str, tuple[str, dict]] = {}
    for path in sorted(results_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text())
            model_id = data.get("model_id", "")
            if not model_id:
                continue
            if model_id not in latest or path.name > latest[model_id][0]:
                latest[model_id] = (path.name, data)
        except (json.JSONDecodeError, KeyError):
            logger.warning("Fichier de résultats ignoré (format invalide) : %s", path)
            continue

    results: dict[str, RunResult] = {}
    for model_id, (_filename, data) in latest.items():
        try:
            s = data["summary"]
            total_cost = (
                Cost(amount=s["total_cost"], currency=s.get("total_cost_currency", "USD"))
                if s.get("total_cost") is not None
                else None
            )
            carbon = (
                CarbonFootprint(s["carbon_g_co2e"])
                if s.get("carbon_g_co2e") is not None
                else None
            )
            summary = RunSummary(
                total=s["total"],
                answered=s.get("answered", s["total"]),
                correct=s["correct"],
                accuracy=Accuracy(s["accuracy"]),
                sourcing_rate=Accuracy(s.get("sourcing_rate", 0.0)),
                sourcing_correct_rate=Accuracy(s.get("sourcing_correct_rate", 0.0)),
                total_cost=total_cost,
                total_tokens=s.get("total_tokens"),
                avg_latency=Latency(s["avg_latency_s"]) if s.get("avg_latency_s") else None,
                carbon_footprint=carbon,
                by_type=s.get("by_type", {}),
            )
            question_results = []
            for qr in data.get("results", []):
                score = None
                if qr.get("is_correct") is not None:
                    score = ScoreResult(
                        is_correct=qr["is_correct"],
                        is_sourcing_present=qr.get("is_sourcing_present", False),
                        is_sourcing_correct=qr.get("is_sourcing_correct", False),
                    )
                question_results.append(
                    QuestionResult(
                        question_id=QuestionId(qr["question_id"]),
                        question_type=QuestionType(qr["question_type"]),
                        expected_answer=qr["expected_answer"],
                        actual_answer=qr.get("actual_answer"),
                        score=score,
                        latency=Latency(qr["latency_s"]) if qr.get("latency_s") else None,
                        input_tokens=qr.get("input_tokens"),
                        output_tokens=qr.get("output_tokens"),
                        cost=Cost(qr["cost"]) if qr.get("cost") is not None else None,
                        error=qr.get("error"),
                    )
                )
            results[model_id] = RunResult(
                run_id=RunId(data["run_id"]),
                timestamp=datetime.fromisoformat(data["timestamp"]),
                dataset_id=DatasetId(data["dataset_id"]),
                dataset_version=data.get("dataset_version", ""),
                approach_id=ApproachId(data.get("approach_id", "")),
                model_id=ModelId(model_id),
                framework_version=data.get("framework_version", ""),
                config=data.get("config", {}),
                summary=summary,
                results=question_results,
            )
        except (KeyError, TypeError, ValueError):
            logger.warning("Résultat ignoré (désérialisation échouée) : %s", _filename)
            continue

    return results
