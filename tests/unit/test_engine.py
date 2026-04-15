"""Unit tests for BenchmarkEngine."""

from datetime import datetime
from unittest.mock import MagicMock

from llm_benchmark.domain.engine import BenchmarkEngine
from llm_benchmark.domain.entities import (
    Dataset,
    LLMResponse,
    Question,
)
from llm_benchmark.domain.value_objects import (
    ApproachId,
    DatasetId,
    DatasetVersion,
    Latency,
    MCQChoices,
    ModelId,
    QuestionId,
    QuestionType,
    RunId,
    Source,
)

# ---------------------------------------------------------------------------
# Fixtures / builders
# ---------------------------------------------------------------------------


def _make_open_question(question_id: str = "q1") -> Question:
    return Question(
        id=QuestionId(question_id),
        question_type=QuestionType.OPEN,
        question_text="What is the antibiotic of choice?",
        expected_answer="amoxicillin",
    )


def _make_mcq_question(question_id: str = "q2") -> Question:
    return Question(
        id=QuestionId(question_id),
        question_type=QuestionType.MCQ,
        question_text="Which antibiotic?",
        expected_answer="A",
        choices=MCQChoices({"A": "amoxicillin", "B": "penicillin"}),
    )


def _make_dataset(questions: list[Question] | None = None) -> Dataset:
    return Dataset(
        id=DatasetId("test-dataset"),
        version=DatasetVersion("1.0"),
        source=Source("test"),
        scope="unit tests",
        questions=questions or [_make_open_question()],
    )


def _make_approach(approach_id: str = "test-approach", prompt: str = "prompt") -> MagicMock:
    approach = MagicMock()
    approach.approach_id = ApproachId(approach_id)
    approach.build_prompt.return_value = prompt
    approach.prepare.return_value = None
    return approach


def _make_llm(model_id: str = "test-model", response_text: str = "amoxicillin") -> MagicMock:
    from llm_benchmark.domain.value_objects import Cost

    llm = MagicMock()
    llm.model_id = ModelId(model_id)
    llm.price_per_input_token = Cost(0.000001)
    llm.price_per_output_token = Cost(0.000002)
    llm.complete.return_value = LLMResponse(
        text=response_text,
        input_tokens=100,
        output_tokens=50,
        latency=Latency(0.5),
    )
    return llm


# ---------------------------------------------------------------------------
# Basic run structure
# ---------------------------------------------------------------------------


class TestBenchmarkEngineRunStructure:
    """Tests that verify the shape and metadata of RunResult."""

    def test_returns_one_run_result_per_approach_llm_combination(self) -> None:
        engine = BenchmarkEngine()
        dataset = _make_dataset()
        approaches = [_make_approach("a1"), _make_approach("a2")]
        llms = [_make_llm("m1"), _make_llm("m2")]

        results = engine.run(dataset, approaches, llms)

        assert len(results) == 4  # 2 approaches × 2 llms

    def test_run_result_has_unique_run_id(self) -> None:
        engine = BenchmarkEngine()
        dataset = _make_dataset()

        results = engine.run(dataset, [_make_approach()], [_make_llm()])

        assert len(results) == 1
        assert isinstance(results[0].run_id, RunId)
        assert results[0].run_id.value  # non-empty

    def test_two_successive_runs_produce_distinct_run_ids(self) -> None:
        engine = BenchmarkEngine()
        dataset = _make_dataset()

        first = engine.run(dataset, [_make_approach()], [_make_llm()])
        second = engine.run(dataset, [_make_approach()], [_make_llm()])

        assert first[0].run_id != second[0].run_id

    def test_run_result_timestamp_is_timezone_aware(self) -> None:
        engine = BenchmarkEngine()
        dataset = _make_dataset()

        results = engine.run(dataset, [_make_approach()], [_make_llm()])

        ts = results[0].timestamp
        assert isinstance(ts, datetime)
        assert ts.tzinfo is not None

    def test_run_result_carries_correct_ids(self) -> None:
        engine = BenchmarkEngine()
        dataset = _make_dataset()
        approach = _make_approach("my-approach")
        llm = _make_llm("my-model")

        results = engine.run(dataset, [approach], [llm])

        result = results[0]
        assert result.dataset_id == DatasetId("test-dataset")
        assert result.approach_id == ApproachId("my-approach")
        assert result.model_id == ModelId("my-model")

    def test_prepare_is_called_once_per_approach_per_run(self) -> None:
        engine = BenchmarkEngine()
        dataset = _make_dataset()
        approach = _make_approach()
        llm = _make_llm()

        engine.run(dataset, [approach], [llm])

        approach.prepare.assert_called_once()


# ---------------------------------------------------------------------------
# Question filtering
# ---------------------------------------------------------------------------


class TestQuestionFiltering:
    """Tests for the question_ids filter parameter."""

    def test_filters_to_requested_question_ids(self) -> None:
        engine = BenchmarkEngine()
        questions = [
            _make_open_question("q1"),
            _make_open_question("q2"),
            _make_open_question("q3"),
        ]
        dataset = _make_dataset(questions)

        results = engine.run(
            dataset,
            [_make_approach()],
            [_make_llm()],
            question_ids=[QuestionId("q1"), QuestionId("q3")],
        )

        assert results[0].summary.total == 2

    def test_none_question_ids_runs_all_questions(self) -> None:
        engine = BenchmarkEngine()
        questions = [_make_open_question(f"q{i}") for i in range(5)]
        dataset = _make_dataset(questions)

        results = engine.run(dataset, [_make_approach()], [_make_llm()], question_ids=None)

        assert results[0].summary.total == 5


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


class TestErrorHandling:
    """Tests that LLM errors are recorded without stopping the run."""

    def test_llm_error_is_recorded_in_question_result(self) -> None:
        engine = BenchmarkEngine()
        dataset = _make_dataset([_make_open_question("q1"), _make_open_question("q2")])
        approach = _make_approach()
        llm = _make_llm()
        llm.complete.side_effect = [RuntimeError("API timeout"), LLMResponse(text="amoxicillin")]

        results = engine.run(dataset, [approach], [llm])

        question_results = results[0].results
        assert question_results[0].error is not None
        assert question_results[0].actual_answer is None
        assert question_results[0].score is None

    def test_run_continues_after_llm_error(self) -> None:
        engine = BenchmarkEngine()
        dataset = _make_dataset([_make_open_question("q1"), _make_open_question("q2")])
        approach = _make_approach()
        llm = _make_llm()
        llm.complete.side_effect = [RuntimeError("API timeout"), LLMResponse(text="amoxicillin")]

        results = engine.run(dataset, [approach], [llm])

        assert results[0].summary.total == 2
        assert results[0].results[1].error is None

    def test_errored_question_does_not_count_as_correct(self) -> None:
        engine = BenchmarkEngine()
        dataset = _make_dataset([_make_open_question("q1")])
        approach = _make_approach()
        llm = _make_llm()
        llm.complete.side_effect = RuntimeError("API error")

        results = engine.run(dataset, [approach], [llm])

        assert results[0].summary.correct == 0

    def test_accuracy_excludes_errored_questions(self) -> None:
        engine = BenchmarkEngine()
        dataset = _make_dataset([
            _make_open_question("q1"),
            _make_open_question("q2"),
            _make_open_question("q3"),
        ])
        approach = _make_approach()
        llm = _make_llm()
        # q1 errors, q2 and q3 answer correctly
        llm.complete.side_effect = [
            RuntimeError("Rate limit"),
            LLMResponse(text="amoxicillin", input_tokens=10, output_tokens=5, latency=Latency(0.1)),
            LLMResponse(text="amoxicillin", input_tokens=10, output_tokens=5, latency=Latency(0.1)),
        ]

        results = engine.run(dataset, [approach], [llm])

        summary = results[0].summary
        assert summary.total == 3
        assert summary.correct == 2
        # Accuracy = 2/2 (not 2/3), because errored questions are excluded
        assert abs(summary.accuracy.value - 1.0) < 1e-9


# ---------------------------------------------------------------------------
# Summary correctness
# ---------------------------------------------------------------------------


class TestRunSummary:
    """Tests that RunSummary aggregates results correctly."""

    def test_summary_total_matches_question_count(self) -> None:
        engine = BenchmarkEngine()
        questions = [_make_open_question(f"q{i}") for i in range(3)]
        dataset = _make_dataset(questions)
        llm = _make_llm(response_text="amoxicillin")

        results = engine.run(dataset, [_make_approach()], [llm])

        assert results[0].summary.total == 3

    def test_summary_correct_lte_total(self) -> None:
        engine = BenchmarkEngine()
        dataset = _make_dataset([_make_open_question("q1"), _make_open_question("q2")])
        llm = _make_llm(response_text="amoxicillin")

        results = engine.run(dataset, [_make_approach()], [llm])

        summary = results[0].summary
        assert summary.correct <= summary.total

    def test_summary_accuracy_equals_correct_over_total(self) -> None:
        engine = BenchmarkEngine()
        # 2 questions, LLM answers correctly for both ("amoxicillin" matches expected)
        questions = [_make_open_question("q1"), _make_open_question("q2")]
        dataset = _make_dataset(questions)
        llm = _make_llm(response_text="amoxicillin")

        results = engine.run(dataset, [_make_approach()], [llm])

        summary = results[0].summary
        expected_accuracy = summary.correct / summary.total
        assert abs(summary.accuracy.value - expected_accuracy) < 1e-9

    def test_summary_by_type_contains_question_types(self) -> None:
        engine = BenchmarkEngine()
        dataset = _make_dataset([_make_open_question("q1"), _make_mcq_question("q2")])
        llm = _make_llm(response_text="A")

        results = engine.run(dataset, [_make_approach()], [llm])

        by_type = results[0].summary.by_type
        assert "open" in by_type
        assert "mcq" in by_type


# ---------------------------------------------------------------------------
# system_prompt propagation
# ---------------------------------------------------------------------------


class TestSystemPromptPropagation:
    """Tests that dataset.system_prompt is passed to LLMRequest."""

    def test_dataset_system_prompt_is_passed_to_llm_request(self) -> None:
        """BenchmarkEngine must pass dataset.system_prompt as the system message."""
        from llm_benchmark.domain.entities import LLMRequest

        engine = BenchmarkEngine()
        dataset = _make_dataset([_make_open_question("q1")])
        dataset.system_prompt = "Réponds uniquement par le nom de la molécule."
        approach = _make_approach(prompt="Quelle molécule ?")
        llm = _make_llm()

        engine.run(dataset, [approach], [llm])

        call_args = llm.complete.call_args[0][0]
        assert isinstance(call_args, LLMRequest)
        assert call_args.system_prompt == "Réponds uniquement par le nom de la molécule."

    def test_empty_system_prompt_when_dataset_has_none(self) -> None:
        """When dataset.system_prompt is empty, LLMRequest.system_prompt is ''."""
        from llm_benchmark.domain.entities import LLMRequest

        engine = BenchmarkEngine()
        dataset = _make_dataset([_make_open_question("q1")])
        # system_prompt defaults to ""
        approach = _make_approach()
        llm = _make_llm()

        engine.run(dataset, [approach], [llm])

        call_args = llm.complete.call_args[0][0]
        assert isinstance(call_args, LLMRequest)
        assert call_args.system_prompt == ""
