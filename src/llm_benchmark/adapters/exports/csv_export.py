"""CSV export adapter for comparative benchmark run results."""

from __future__ import annotations

import csv
from pathlib import Path

from llm_benchmark.domain.entities import RunResult


class CsvExportAdapter:
    """Export a list of RunResults as a comparative CSV report.

    Each row represents one (approach × LLM) run. The file is named
    ``benchmark_report.csv`` and placed in the given output directory.

    Notes
    -----
    This adapter does not implement ``ExportPort`` because that port is
    designed for single-run export. The CSV adapter operates on a list
    of runs to produce a comparative report.
    """

    _FIELDNAMES = [
        "run_id",
        "timestamp",
        "dataset_id",
        "dataset_version",
        "approach_id",
        "model_id",
        "framework_version",
        "total",
        "correct",
        "accuracy",
        "sourcing_rate",
        "sourcing_correct_rate",
        "total_cost",
        "total_tokens",
        "avg_latency_s",
        "carbon_g_co2e",
    ]

    def export(self, results: list[RunResult], output_dir: Path) -> Path:
        """Write a comparative CSV report for the given runs.

        Parameters
        ----------
        results : list[RunResult]
            One or more benchmark run results to compare.
        output_dir : Path
            Directory where the CSV file will be created.

        Returns
        -------
        Path
            Path to the created CSV file.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "benchmark_report.csv"

        with output_path.open("w", newline="", encoding="utf-8") as file_handle:
            writer = csv.DictWriter(file_handle, fieldnames=self._FIELDNAMES)
            writer.writeheader()
            for run_result in results:
                writer.writerow(self._to_row(run_result))

        return output_path

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _to_row(self, run_result: RunResult) -> dict:
        summary = run_result.summary
        return {
            "run_id": run_result.run_id.value,
            "timestamp": run_result.timestamp.isoformat(),
            "dataset_id": run_result.dataset_id.value,
            "dataset_version": run_result.dataset_version,
            "approach_id": run_result.approach_id.value,
            "model_id": run_result.model_id.value,
            "framework_version": run_result.framework_version,
            "total": summary.total,
            "correct": summary.correct,
            "accuracy": summary.accuracy.value,
            "sourcing_rate": summary.sourcing_rate.value,
            "sourcing_correct_rate": summary.sourcing_correct_rate.value,
            "total_cost": summary.total_cost.amount if summary.total_cost else "",
            "total_tokens": summary.total_tokens if summary.total_tokens is not None else "",
            "avg_latency_s": summary.avg_latency.seconds if summary.avg_latency else "",
            "carbon_g_co2e": summary.carbon_footprint.g_co2e if summary.carbon_footprint else "",
        }
