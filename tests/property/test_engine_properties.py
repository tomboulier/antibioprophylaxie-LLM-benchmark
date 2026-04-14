"""Property-based tests for BenchmarkEngine."""

from unittest.mock import MagicMock

from hypothesis import given, settings
from hypothesis import strategies as st

from llm_benchmark.domain.engine import BenchmarkEngine
from llm_benchmark.domain.entities import Dataset, LLMResponse, Question
from llm_benchmark.domain.value_objects import (
    ApproachId,
    Cost,
    DatasetId,
    DatasetVersion,
    Latency,
    ModelId,
    QuestionId,
    QuestionType,
    Source,
)

# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

_nonempty_text = st.text(min_size=1, max_size=50).filter(str.strip)


def _open_question_strategy():
    return st.builds(
        Question,
        id=_nonempty_text.map(QuestionId),
        question_type=st.just(QuestionType.OPEN),
        question_text=_nonempty_text,
        expected_answer=_nonempty_text,
        choices=st.just(None),
    )


def _dataset_strategy():
    return st.builds(
        Dataset,
        id=st.just(DatasetId("prop-dataset")),
        version=st.just(DatasetVersion("1.0")),
        source=st.just(Source("test")),
        scope=st.just("property tests"),
        questions=st.lists(_open_question_strategy(), min_size=1, max_size=5),
    )


def _make_stub_approach() -> MagicMock:
    approach = MagicMock()
    approach.approach_id = ApproachId("stub-approach")
    approach.build_prompt.return_value = "prompt"
    approach.prepare.return_value = None
    return approach


def _make_stub_llm(response_text: str = "answer") -> MagicMock:
    llm = MagicMock()
    llm.model_id = ModelId("stub-model")
    llm.price_per_input_token = Cost(0.000001)
    llm.price_per_output_token = Cost(0.000002)
    llm.complete.return_value = LLMResponse(
        text=response_text,
        input_tokens=10,
        output_tokens=5,
        latency=Latency(0.1),
    )
    return llm


# ---------------------------------------------------------------------------
# Property 8: run_id uniqueness
# ---------------------------------------------------------------------------


def test_property_run_id_uniqueness() -> None:
    """Two successive calls to engine.run produce distinct RunIds.

    Validates: Requirements 3.2
    """
    engine = BenchmarkEngine()
    dataset = Dataset(
        id=DatasetId("d"),
        version=DatasetVersion("1.0"),
        source=Source("s"),
        scope="test",
        questions=[
            Question(
                id=QuestionId("q1"),
                question_type=QuestionType.OPEN,
                question_text="q?",
                expected_answer="a",
            )
        ],
    )

    first_results = engine.run(dataset, [_make_stub_approach()], [_make_stub_llm()])
    second_results = engine.run(dataset, [_make_stub_approach()], [_make_stub_llm()])

    assert first_results[0].run_id != second_results[0].run_id


# ---------------------------------------------------------------------------
# Property 9: summary consistency
# ---------------------------------------------------------------------------


@given(dataset=_dataset_strategy())
@settings(max_examples=30)
def test_property_summary_correct_lte_total(dataset: Dataset) -> None:
    """summary.correct <= summary.total for any dataset.

    Validates: Requirements 3.3, 4.6
    """
    engine = BenchmarkEngine()
    results = engine.run(dataset, [_make_stub_approach()], [_make_stub_llm()])

    for result in results:
        assert result.summary.correct <= result.summary.total


@given(dataset=_dataset_strategy())
@settings(max_examples=30)
def test_property_summary_accuracy_equals_correct_over_total(dataset: Dataset) -> None:
    """summary.accuracy == correct / total for any dataset with at least one question.

    Validates: Requirements 3.3, 4.6
    """
    engine = BenchmarkEngine()
    results = engine.run(dataset, [_make_stub_approach()], [_make_stub_llm()])

    for result in results:
        summary = result.summary
        if summary.total > 0:
            expected = summary.correct / summary.total
            assert abs(summary.accuracy.value - expected) < 1e-9
