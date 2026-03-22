"""Unit tests for JSON and CSV export adapters."""

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from llm_benchmark.adapters.exports.csv_export import CsvExportAdapter
from llm_benchmark.adapters.exports.json_export import JsonExportAdapter
from llm_benchmark.domain.entities import (
    QuestionResult,
    RunResult,
    RunSummary,
    ScoreResult,
)
from llm_benchmark.domain.value_objects import (
    Accuracy,
    ApproachId,
    DatasetId,
    ModelId,
    QuestionId,
    QuestionType,
    RunId,
)

# ---------------------------------------------------------------------------
# Builders
# ---------------------------------------------------------------------------

_TOP_LEVEL_KEYS = {
    "run_id",
    "timestamp",
    "dataset_id",
    "dataset_version",
    "approach_id",
    "model_id",
    "framework_version",
    "config",
    "summary",
    "results",
}

_CSV_COLUMNS = {
    "run_id",
    "approach_id",
    "model_id",
    "dataset_id",
    "accuracy",
    "correct",
    "total",
    "total_cost",
    "total_tokens",
    "avg_latency_s",
}


def _make_summary() -> RunSummary:
    return RunSummary(
        total=2,
        correct=1,
        accuracy=Accuracy(0.5),
        sourcing_rate=Accuracy(0.5),
        sourcing_correct_rate=Accuracy(0.5),
        total_cost=None,
        total_tokens=None,
        avg_latency=None,
        carbon_footprint=None,
        by_type={"open": {"total": 2, "correct": 1, "accuracy": 0.5}},
    )


def _make_question_result(question_id: str = "q1") -> QuestionResult:
    return QuestionResult(
        question_id=QuestionId(question_id),
        question_type=QuestionType.OPEN,
        expected_answer="amoxicillin",
        actual_answer="amoxicillin",
        score=ScoreResult(is_correct=True),
    )


def _make_run_result(run_id: str = "run-1") -> RunResult:
    return RunResult(
        run_id=RunId(run_id),
        timestamp=datetime(2025, 1, 15, 10, 30, 0, tzinfo=timezone.utc),
        dataset_id=DatasetId("sfar"),
        dataset_version="1.0",
        approach_id=ApproachId("long-context"),
        model_id=ModelId("gpt-4o"),
        framework_version="0.1.0",
        config={"max_tokens": 300},
        summary=_make_summary(),
        results=[_make_question_result("q1"), _make_question_result("q2")],
    )


# ---------------------------------------------------------------------------
# JsonExportAdapter
# ---------------------------------------------------------------------------


class TestJsonExportAdapter:
    def test_export_creates_file(self, tmp_path: Path) -> None:
        adapter = JsonExportAdapter()
        run_result = _make_run_result()

        output_path = adapter.export(run_result, tmp_path)

        assert output_path.exists()

    def test_export_returns_path_inside_output_dir(self, tmp_path: Path) -> None:
        adapter = JsonExportAdapter()
        run_result = _make_run_result()

        output_path = adapter.export(run_result, tmp_path)

        assert output_path.parent == tmp_path

    def test_export_produces_valid_json(self, tmp_path: Path) -> None:
        adapter = JsonExportAdapter()
        run_result = _make_run_result()

        output_path = adapter.export(run_result, tmp_path)
        content = json.loads(output_path.read_text())

        assert isinstance(content, dict)

    def test_export_json_contains_required_top_level_keys(self, tmp_path: Path) -> None:
        adapter = JsonExportAdapter()
        run_result = _make_run_result()

        output_path = adapter.export(run_result, tmp_path)
        content = json.loads(output_path.read_text())

        assert set(content.keys()) == _TOP_LEVEL_KEYS

    def test_export_json_run_id_matches(self, tmp_path: Path) -> None:
        adapter = JsonExportAdapter()
        run_result = _make_run_result("my-run-id")

        output_path = adapter.export(run_result, tmp_path)
        content = json.loads(output_path.read_text())

        assert content["run_id"] == "my-run-id"

    def test_export_json_results_count_matches(self, tmp_path: Path) -> None:
        adapter = JsonExportAdapter()
        run_result = _make_run_result()

        output_path = adapter.export(run_result, tmp_path)
        content = json.loads(output_path.read_text())

        assert len(content["results"]) == 2

    def test_export_filename_contains_timestamp_model_and_approach(self, tmp_path: Path) -> None:
        adapter = JsonExportAdapter()
        run_result = _make_run_result()

        output_path = adapter.export(run_result, tmp_path)

        # Expected pattern: 20250115_103000_gpt-4o_long-context.json
        assert "20250115_103000" in output_path.name
        assert "gpt-4o" in output_path.name
        assert "long-context" in output_path.name

    def test_export_filename_sanitises_slashes(self, tmp_path: Path) -> None:
        adapter = JsonExportAdapter()
        run_result = _make_run_result()
        # Simulate a model_id with a slash (e.g. from a litellm prefix)
        run_result = RunResult(
            run_id=run_result.run_id,
            timestamp=run_result.timestamp,
            dataset_id=run_result.dataset_id,
            dataset_version=run_result.dataset_version,
            approach_id=run_result.approach_id,
            model_id=ModelId("mistral/mistral-small-latest"),
            framework_version=run_result.framework_version,
            config=run_result.config,
            summary=run_result.summary,
            results=run_result.results,
        )

        output_path = adapter.export(run_result, tmp_path)

        assert "/" not in output_path.name


# ---------------------------------------------------------------------------
# CsvExportAdapter
# ---------------------------------------------------------------------------


class TestCsvExportAdapter:
    def test_export_creates_file(self, tmp_path: Path) -> None:
        adapter = CsvExportAdapter()
        runs = [_make_run_result("r1"), _make_run_result("r2")]

        output_path = adapter.export(runs, tmp_path)

        assert output_path.exists()

    def test_export_returns_path_inside_output_dir(self, tmp_path: Path) -> None:
        adapter = CsvExportAdapter()

        output_path = adapter.export([_make_run_result()], tmp_path)

        assert output_path.parent == tmp_path

    def test_export_csv_has_expected_columns(self, tmp_path: Path) -> None:
        adapter = CsvExportAdapter()

        output_path = adapter.export([_make_run_result()], tmp_path)
        with output_path.open() as file_handle:
            reader = csv.DictReader(file_handle)
            columns = set(reader.fieldnames or [])

        assert _CSV_COLUMNS.issubset(columns)

    def test_export_csv_has_one_row_per_run(self, tmp_path: Path) -> None:
        adapter = CsvExportAdapter()
        runs = [_make_run_result("r1"), _make_run_result("r2")]

        output_path = adapter.export(runs, tmp_path)
        with output_path.open() as file_handle:
            rows = list(csv.DictReader(file_handle))

        assert len(rows) == 2

    def test_export_csv_accuracy_value(self, tmp_path: Path) -> None:
        adapter = CsvExportAdapter()
        run_result = _make_run_result()

        output_path = adapter.export([run_result], tmp_path)
        with output_path.open() as file_handle:
            row = next(csv.DictReader(file_handle))

        assert float(row["accuracy"]) == pytest.approx(0.5)
