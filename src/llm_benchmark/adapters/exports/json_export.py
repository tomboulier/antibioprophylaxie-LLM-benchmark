"""JSON export adapter for benchmark run results."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from llm_benchmark.domain.entities import QuestionResult, RunResult, RunSummary
from llm_benchmark.ports.export import ExportPort


class JsonExportAdapter(ExportPort):
    """Serialise a RunResult to a structured JSON file.

    The output file is named ``{run_id}.json`` and placed in the given
    output directory. The schema is stable: the top-level keys are always
    ``run_id``, ``timestamp``, ``dataset_id``, ``dataset_version``,
    ``approach_id``, ``model_id``, ``framework_version``, ``config``,
    ``summary``, and ``results``.
    """

    def export(self, result: RunResult, output_dir: Path) -> Path:
        """Serialise *result* to JSON and write it to *output_dir*.

        Parameters
        ----------
        result : RunResult
            The benchmark run result to export.
        output_dir : Path
            Directory where the JSON file will be created.

        Returns
        -------
        Path
            Path to the created JSON file.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        safe_name = result.run_id.value.replace("/", "_").replace("\\", "_")
        output_path = output_dir / f"{safe_name}.json"
        payload = self._serialise(result)
        output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
        return output_path

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _serialise(self, result: RunResult) -> dict[str, Any]:
        return {
            "run_id": result.run_id.value,
            "timestamp": result.timestamp.isoformat(),
            "dataset_id": result.dataset_id.value,
            "dataset_version": result.dataset_version,
            "approach_id": result.approach_id.value,
            "model_id": result.model_id.value,
            "framework_version": result.framework_version,
            "config": result.config,
            "summary": self._serialise_summary(result.summary),
            "results": [self._serialise_question_result(qr) for qr in result.results],
        }

    def _serialise_summary(self, summary: RunSummary) -> dict[str, Any]:
        return {
            "total": summary.total,
            "correct": summary.correct,
            "accuracy": summary.accuracy.value,
            "sourcing_rate": summary.sourcing_rate.value,
            "sourcing_correct_rate": summary.sourcing_correct_rate.value,
            "total_cost": summary.total_cost.amount if summary.total_cost else None,
            "total_cost_currency": summary.total_cost.currency if summary.total_cost else None,
            "total_tokens": summary.total_tokens,
            "avg_latency_s": summary.avg_latency.seconds if summary.avg_latency else None,
            "carbon_g_co2e": summary.carbon_footprint.g_co2e if summary.carbon_footprint else None,
            "by_type": summary.by_type,
        }

    def _serialise_question_result(self, question_result: QuestionResult) -> dict[str, Any]:
        score = question_result.score
        return {
            "question_id": question_result.question_id.value,
            "question_type": question_result.question_type.value,
            "expected_answer": question_result.expected_answer,
            "actual_answer": question_result.actual_answer,
            "is_correct": score.is_correct if score else None,
            "is_sourcing_present": score.is_sourcing_present if score else None,
            "is_sourcing_correct": score.is_sourcing_correct if score else None,
            "latency_s": question_result.latency.seconds if question_result.latency else None,
            "input_tokens": question_result.input_tokens,
            "output_tokens": question_result.output_tokens,
            "cost": question_result.cost.amount if question_result.cost else None,
            "error": question_result.error,
        }
