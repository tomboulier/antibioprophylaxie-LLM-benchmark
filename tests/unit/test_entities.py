"""Unit tests for domain entities."""

import pytest

from llm_benchmark.domain.value_objects import (
    Accuracy,
    ApproachId,
    CarbonFootprint,
    Cost,
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
# Helpers — minimal valid instances
# ---------------------------------------------------------------------------


def make_open_question():
    from llm_benchmark.domain.entities import Question

    return Question(
        id=QuestionId("q-001"),
        question_type=QuestionType.OPEN,
        question_text="What is the recommended antibiotic?",
        expected_answer="amoxicillin",
    )


def make_mcq_question():
    from llm_benchmark.domain.entities import Question

    return Question(
        id=QuestionId("q-002"),
        question_type=QuestionType.MCQ,
        question_text="Which antibiotic is preferred?",
        expected_answer="A",
        choices=MCQChoices({"A": "amoxicillin", "B": "cefazolin"}),
    )


# ---------------------------------------------------------------------------
# Question — open type
# ---------------------------------------------------------------------------


def test_question_open_construction():
    question = make_open_question()
    assert question.id == QuestionId("q-001")
    assert question.question_type == QuestionType.OPEN
    assert question.question_text == "What is the recommended antibiotic?"
    assert question.expected_answer == "amoxicillin"
    assert question.source is None
    assert question.choices is None


def test_question_open_with_source():
    from llm_benchmark.domain.entities import Question

    question = Question(
        id=QuestionId("q-003"),
        question_type=QuestionType.OPEN,
        question_text="What is the dose?",
        expected_answer="2g",
        source=Source("SFAR-2024"),
    )
    assert question.source == Source("SFAR-2024")


def test_question_open_choices_not_required():
    """Open questions must not require choices — no error raised."""
    question = make_open_question()
    assert question.choices is None


# ---------------------------------------------------------------------------
# Question — MCQ type
# ---------------------------------------------------------------------------


def test_question_mcq_construction():
    question = make_mcq_question()
    assert question.question_type == QuestionType.MCQ
    assert question.choices is not None
    assert question.choices.choices["A"] == "amoxicillin"


def test_question_mcq_missing_choices_raises():
    from llm_benchmark.domain.entities import Question

    with pytest.raises(ValueError, match="choices"):
        Question(
            id=QuestionId("q-004"),
            question_type=QuestionType.MCQ,
            question_text="Which antibiotic?",
            expected_answer="B",
            choices=None,
        )


def test_question_mcq_with_source():
    from llm_benchmark.domain.entities import Question

    question = Question(
        id=QuestionId("q-005"),
        question_type=QuestionType.MCQ,
        question_text="Which antibiotic?",
        expected_answer="A",
        choices=MCQChoices({"A": "amoxicillin", "B": "cefazolin"}),
        source=Source("SFAR-2024"),
    )
    assert question.source == Source("SFAR-2024")


# ---------------------------------------------------------------------------
# Dataset
# ---------------------------------------------------------------------------


def test_dataset_construction():
    from llm_benchmark.domain.entities import Dataset

    questions = [make_open_question(), make_mcq_question()]
    dataset = Dataset(
        id=DatasetId("sfar-antibio"),
        version=DatasetVersion("1.0"),
        source=Source("SFAR-2024"),
        scope="Antibioprophylaxie chirurgicale",
        questions=questions,
    )
    assert dataset.id == DatasetId("sfar-antibio")
    assert dataset.version == DatasetVersion("1.0")
    assert dataset.source == Source("SFAR-2024")
    assert dataset.scope == "Antibioprophylaxie chirurgicale"
    assert len(dataset.questions) == 2


def test_dataset_empty_questions():
    from llm_benchmark.domain.entities import Dataset

    dataset = Dataset(
        id=DatasetId("empty-ds"),
        version=DatasetVersion("0.1"),
        source=Source("test"),
        scope="test scope",
        questions=[],
    )
    assert dataset.questions == []


# ---------------------------------------------------------------------------
# RunResult
# ---------------------------------------------------------------------------


def _make_run_result():
    from datetime import datetime, timezone

    from llm_benchmark.domain.entities import (
        QuestionResult,
        RunResult,
        RunSummary,
        ScoreResult,
    )

    score = ScoreResult(is_correct=True)
    question_result = QuestionResult(
        question_id=QuestionId("q-001"),
        question_type=QuestionType.OPEN,
        expected_answer="amoxicillin",
        actual_answer="amoxicillin",
        score=score,
    )
    summary = RunSummary(
        total=1,
        correct=1,
        accuracy=Accuracy(1.0),
        sourcing_rate=Accuracy(0.0),
        sourcing_correct_rate=Accuracy(0.0),
        total_cost=None,
        total_tokens=None,
        avg_latency=None,
        carbon_footprint=None,
        by_type={},
    )
    return RunResult(
        run_id=RunId("run-abc-123"),
        timestamp=datetime(2025, 1, 15, 10, 30, 0, tzinfo=timezone.utc),
        dataset_id=DatasetId("sfar-antibio"),
        dataset_version="1.0",
        approach_id=ApproachId("long-context"),
        model_id=ModelId("claude-sonnet-4"),
        framework_version="0.1.0",
        config={"max_tokens": 300},
        summary=summary,
        results=[question_result],
    )


def test_run_result_construction():
    from datetime import datetime, timezone

    run_result = _make_run_result()
    assert run_result.run_id == RunId("run-abc-123")
    assert run_result.timestamp == datetime(2025, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
    assert run_result.dataset_id == DatasetId("sfar-antibio")
    assert run_result.dataset_version == "1.0"
    assert run_result.approach_id == ApproachId("long-context")
    assert run_result.model_id == ModelId("claude-sonnet-4")
    assert run_result.framework_version == "0.1.0"
    assert run_result.config == {"max_tokens": 300}
    assert len(run_result.results) == 1


def test_run_result_summary_fields():
    run_result = _make_run_result()
    summary = run_result.summary
    assert summary.total == 1
    assert summary.correct == 1
    assert summary.accuracy == Accuracy(1.0)
    assert summary.total_cost is None
    assert summary.carbon_footprint is None


def test_run_result_question_result_fields():
    run_result = _make_run_result()
    qr = run_result.results[0]
    assert qr.question_id == QuestionId("q-001")
    assert qr.question_type == QuestionType.OPEN
    assert qr.expected_answer == "amoxicillin"
    assert qr.actual_answer == "amoxicillin"
    assert qr.score is not None
    assert qr.score.is_correct is True
    assert qr.error is None


# ---------------------------------------------------------------------------
# ScoreResult defaults
# ---------------------------------------------------------------------------


def test_score_result_defaults():
    from llm_benchmark.domain.entities import ScoreResult

    score = ScoreResult(is_correct=False)
    assert score.is_sourcing_present is False
    assert score.is_sourcing_correct is False
    assert score.details == {}


# ---------------------------------------------------------------------------
# LLMRequest / LLMResponse defaults
# ---------------------------------------------------------------------------


def test_llm_request_defaults():
    from llm_benchmark.domain.entities import LLMRequest

    req = LLMRequest(system_prompt="You are a doctor.", user_prompt="What antibiotic?")
    assert req.max_tokens == 300


def test_llm_response_defaults():
    from llm_benchmark.domain.entities import LLMResponse

    resp = LLMResponse(text="amoxicillin")
    assert resp.input_tokens is None
    assert resp.output_tokens is None
    assert resp.latency is None
    assert resp.raw == {}


def test_llm_response_with_metrics():
    from llm_benchmark.domain.entities import LLMResponse

    resp = LLMResponse(
        text="amoxicillin",
        input_tokens=50,
        output_tokens=10,
        latency=Latency(1.2),
        raw={"model": "claude"},
    )
    assert resp.input_tokens == 50
    assert resp.output_tokens == 10
    assert resp.latency == Latency(1.2)
    assert resp.raw == {"model": "claude"}
