"""Unit tests for scripts/run_benchmark.py.

The script is not a package, so it is imported via importlib.
All external dependencies (BenchmarkEngine, JsonExportAdapter, LLM_REGISTRY,
load_dataset, DATASET_PATH) are patched with unittest.mock.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Module import helper
# ---------------------------------------------------------------------------

_SCRIPT_PATH = Path(__file__).parent.parent.parent.parent / "scripts" / "run_benchmark.py"


def _load_run_benchmark():
    """Import scripts/run_benchmark.py as a module via importlib.

    Returns
    -------
    module
        The loaded run_benchmark module.
    """
    spec = importlib.util.spec_from_file_location("run_benchmark", _SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


run_benchmark = _load_run_benchmark()

# ---------------------------------------------------------------------------
# Shared builders
# ---------------------------------------------------------------------------

_MODULE_PATH = "run_benchmark"


def _make_run_result(model_id_value: str = "gpt-4o") -> MagicMock:
    """Build a minimal RunResult mock.

    Parameters
    ----------
    model_id_value : str
        The model ID string to embed in the mock.

    Returns
    -------
    MagicMock
        A mock that satisfies the fields accessed by print_comparison and main.
    """
    from llm_benchmark.domain.value_objects import Accuracy, ModelId

    result = MagicMock()
    result.model_id = ModelId(model_id_value)
    result.summary.correct = 3
    result.summary.total = 5
    result.summary.accuracy = Accuracy(0.6)
    result.summary.by_type = {"open": {"total": 5, "correct": 3, "accuracy": 0.6}}
    return result


# ---------------------------------------------------------------------------
# 4.2 — --list-models prints model IDs and exits 0
# ---------------------------------------------------------------------------


class TestListModels:
    """Tests for the --list-models flag."""

    def test_list_models_prints_model_ids_and_exits_zero(
        self, capsys: pytest.CaptureFixture
    ) -> None:
        """--list-models should print each model ID and raise SystemExit(0).

        Parameters
        ----------
        capsys : pytest.CaptureFixture
            Pytest fixture to capture stdout/stderr.
        """
        fake_registry = {"model-alpha": MagicMock(), "model-beta": MagicMock()}

        with (
            patch.object(run_benchmark, "LLM_REGISTRY", fake_registry),
            patch.object(run_benchmark, "parse_args") as mock_parse_args,
            pytest.raises(SystemExit) as exc_info,
        ):
            mock_parse_args.return_value = MagicMock(list_models=True, models=None, questions=None)
            run_benchmark.main()

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "model-alpha" in captured.out
        assert "model-beta" in captured.out


# ---------------------------------------------------------------------------
# 4.3 — Unknown model exits with error before calling BenchmarkEngine
# ---------------------------------------------------------------------------


class TestUnknownModel:
    """Tests for unknown model validation."""

    def test_unknown_model_exits_with_error_without_calling_engine(self) -> None:
        """An unknown model name should exit 1 before BenchmarkEngine is called."""
        fake_registry = {"known-model": MagicMock()}

        with (
            patch.object(run_benchmark, "LLM_REGISTRY", fake_registry),
            patch.object(run_benchmark, "parse_args") as mock_parse_args,
            patch.object(run_benchmark, "BenchmarkEngine") as mock_engine_class,
            pytest.raises(SystemExit) as exc_info,
        ):
            mock_parse_args.return_value = MagicMock(
                list_models=False,
                models=["unknown-xyz"],
                questions=None,
            )
            run_benchmark.main()

        assert exc_info.value.code == 1
        mock_engine_class.return_value.run.assert_not_called()


# ---------------------------------------------------------------------------
# 4.4 — Missing dataset file exits with error mentioning benchmark_md_to_json.py
# ---------------------------------------------------------------------------


class TestMissingDataset:
    """Tests for missing dataset file handling."""

    def test_missing_dataset_exits_with_error_mentioning_conversion_script(
        self, capsys: pytest.CaptureFixture
    ) -> None:
        """A missing dataset file should exit 1 with a message about benchmark_md_to_json.py.

        Parameters
        ----------
        capsys : pytest.CaptureFixture
            Pytest fixture to capture stdout/stderr.
        """
        fake_registry = {"gpt-4o": MagicMock()}
        non_existent_path = Path("/tmp/does_not_exist_benchmark.json")

        with (
            patch.object(run_benchmark, "LLM_REGISTRY", fake_registry),
            patch.object(run_benchmark, "DATASET_PATH", non_existent_path),
            patch.object(run_benchmark, "parse_args") as mock_parse_args,
            pytest.raises(SystemExit) as exc_info,
        ):
            mock_parse_args.return_value = MagicMock(
                list_models=False,
                models=["gpt-4o"],
                questions=None,
            )
            run_benchmark.main()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "benchmark_md_to_json.py" in captured.err


# ---------------------------------------------------------------------------
# 4.5 — --questions Q01,Q03 passes correct question_ids to engine.run()
# ---------------------------------------------------------------------------


class TestQuestionFiltering:
    """Tests for --questions filtering passed to BenchmarkEngine."""

    def test_questions_flag_passes_correct_question_ids_to_engine(self) -> None:
        """--questions Q01,Q03 should call engine.run() with QuestionId('Q01') and QuestionId('Q03')."""
        from llm_benchmark.domain.value_objects import QuestionId

        fake_adapter = MagicMock()
        fake_registry = {"gpt-4o": fake_adapter}
        fake_dataset = MagicMock()
        fake_result = _make_run_result("gpt-4o")

        with (
            patch.object(run_benchmark, "LLM_REGISTRY", fake_registry),
            patch.object(
                run_benchmark,
                "DATASET_PATH",
                Path("datasets/sfar_antibioprophylaxie/benchmark.json"),
            ),
            patch.object(run_benchmark, "load_dataset", return_value=fake_dataset),
            patch.object(run_benchmark, "BenchmarkEngine") as mock_engine_class,
            patch.object(run_benchmark, "JsonExportAdapter") as mock_export_class,
            patch.object(run_benchmark, "parse_args") as mock_parse_args,
        ):
            mock_engine_class.return_value.run.return_value = [fake_result]
            mock_export_class.return_value.export.return_value = Path("research/results/run.json")
            mock_parse_args.return_value = MagicMock(
                list_models=False,
                models=["gpt-4o"],
                questions="Q01,Q03",
            )
            run_benchmark.main()

        call_kwargs = mock_engine_class.return_value.run.call_args
        passed_question_ids = call_kwargs[1].get("question_ids") or call_kwargs[0][3]
        assert QuestionId("Q01") in passed_question_ids
        assert QuestionId("Q03") in passed_question_ids
        assert len(passed_question_ids) == 2


# ---------------------------------------------------------------------------
# 4.6 — Multiple models produce comparative summary
# ---------------------------------------------------------------------------


class TestComparativeSummary:
    """Tests for the comparative summary printed when multiple models are run."""

    def test_multiple_models_print_comparison_with_both_model_ids(
        self, capsys: pytest.CaptureFixture
    ) -> None:
        """Running two models should produce output containing both model IDs.

        Parameters
        ----------
        capsys : pytest.CaptureFixture
            Pytest fixture to capture stdout/stderr.
        """
        result_a = _make_run_result("model-a")
        result_b = _make_run_result("model-b")

        run_benchmark.print_comparison([result_a, result_b])

        captured = capsys.readouterr()
        assert "model-a" in captured.out
        assert "model-b" in captured.out

    def test_print_comparison_does_nothing_for_single_result(
        self, capsys: pytest.CaptureFixture
    ) -> None:
        """print_comparison should produce no output when given fewer than two results.

        Parameters
        ----------
        capsys : pytest.CaptureFixture
            Pytest fixture to capture stdout/stderr.
        """
        result = _make_run_result("only-model")

        run_benchmark.print_comparison([result])

        captured = capsys.readouterr()
        assert captured.out == ""
