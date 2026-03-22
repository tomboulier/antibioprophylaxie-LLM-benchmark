"""Unit tests for the dataset loader."""

import json

import pytest

from llm_benchmark.domain.value_objects import (
    DatasetId,
    DatasetVersion,
    QuestionType,
    Source,
)

# ---------------------------------------------------------------------------
# Helpers — build minimal valid dataset dicts
# ---------------------------------------------------------------------------


def make_open_question_dict(question_id: str = "Q01") -> dict:
    """Return a minimal valid open question dict."""
    return {
        "id": question_id,
        "type": "open",
        "question": "What antibiotic for hip prosthesis?",
        "réponse": "Cefazolin",
        "source": "ortho-prog-mi-prothese-hanche-genou",
    }


def make_mcq_question_dict(question_id: str = "Q02") -> dict:
    """Return a minimal valid MCQ question dict."""
    return {
        "id": question_id,
        "type": "mcq",
        "question": "Which antibiotic is first-line for hip prosthesis?",
        "choices": {"A": "Amoxicillin", "B": "Cefazolin", "C": "Clindamycin", "D": "Vancomycin"},
        "réponse": "B",
        "source": "ortho-prog-mi-prothese-hanche-genou",
    }


def make_dataset_dict(questions: list[dict]) -> dict:
    """Return a minimal valid dataset dict wrapping the given questions."""
    return {
        "id": "sfar-antibioprophylaxie",
        "version": "1.0",
        "source": "RFE SFAR 2024",
        "scope": "Chirurgie orthopédique et traumatologie",
        "questions": questions,
    }


def write_dataset_file(tmp_path, data: dict):
    """Write a dataset dict to a temporary JSON file and return its path."""
    path = tmp_path / "benchmark.json"
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Valid dataset — open questions only
# ---------------------------------------------------------------------------


def test_load_valid_dataset_open_questions(tmp_path):
    """Loading a dataset with only open questions returns a valid Dataset."""
    from llm_benchmark.domain.dataset_loader import load_dataset

    data = make_dataset_dict([make_open_question_dict("Q01"), make_open_question_dict("Q02")])
    path = write_dataset_file(tmp_path, data)

    dataset = load_dataset(path)

    assert dataset.id == DatasetId("sfar-antibioprophylaxie")
    assert dataset.version == DatasetVersion("1.0")
    assert dataset.source == Source("RFE SFAR 2024")
    assert dataset.scope == "Chirurgie orthopédique et traumatologie"
    assert len(dataset.questions) == 2
    assert all(q.question_type == QuestionType.OPEN for q in dataset.questions)


# ---------------------------------------------------------------------------
# Valid dataset — MCQ questions with choices
# ---------------------------------------------------------------------------


def test_load_valid_dataset_mcq_questions(tmp_path):
    """Loading a dataset with MCQ questions returns questions with choices."""
    from llm_benchmark.domain.dataset_loader import load_dataset

    data = make_dataset_dict([make_mcq_question_dict("Q01")])
    path = write_dataset_file(tmp_path, data)

    dataset = load_dataset(path)

    assert len(dataset.questions) == 1
    question = dataset.questions[0]
    assert question.question_type == QuestionType.MCQ
    assert question.choices is not None
    assert question.choices.choices["B"] == "Cefazolin"


# ---------------------------------------------------------------------------
# Valid dataset — mixed open + MCQ
# ---------------------------------------------------------------------------


def test_load_valid_dataset_mixed_questions(tmp_path):
    """Loading a dataset with both open and MCQ questions succeeds."""
    from llm_benchmark.domain.dataset_loader import load_dataset

    data = make_dataset_dict([make_open_question_dict("Q01"), make_mcq_question_dict("Q02")])
    path = write_dataset_file(tmp_path, data)

    dataset = load_dataset(path)

    assert len(dataset.questions) == 2
    types = {q.question_type for q in dataset.questions}
    assert QuestionType.OPEN in types
    assert QuestionType.MCQ in types


# ---------------------------------------------------------------------------
# Dataset field mapping
# ---------------------------------------------------------------------------


def test_loaded_dataset_has_correct_fields(tmp_path):
    """The loaded Dataset has the correct id, version, source, scope, questions."""
    from llm_benchmark.domain.dataset_loader import load_dataset

    data = {
        "id": "test-dataset",
        "version": "2.5",
        "source": "Test Source 2025",
        "scope": "Test scope description",
        "questions": [make_open_question_dict()],
    }
    path = write_dataset_file(tmp_path, data)

    dataset = load_dataset(path)

    assert dataset.id == DatasetId("test-dataset")
    assert dataset.version == DatasetVersion("2.5")
    assert dataset.source == Source("Test Source 2025")
    assert dataset.scope == "Test scope description"
    assert len(dataset.questions) == 1


# ---------------------------------------------------------------------------
# Rejection — missing required question fields
# ---------------------------------------------------------------------------


REQUIRED_QUESTION_FIELDS = ["id", "type", "question", "réponse", "source"]


@pytest.mark.parametrize("missing_field", REQUIRED_QUESTION_FIELDS)
def test_reject_question_missing_required_field(tmp_path, missing_field):
    """A dataset where a question is missing a required field raises DatasetValidationError."""
    from llm_benchmark.domain.dataset_loader import load_dataset
    from llm_benchmark.domain.exceptions import DatasetValidationError

    question = make_open_question_dict()
    del question[missing_field]
    data = make_dataset_dict([question])
    path = write_dataset_file(tmp_path, data)

    with pytest.raises(DatasetValidationError) as exc_info:
        load_dataset(path)

    assert len(exc_info.value.errors) > 0


def test_reject_dataset_collects_all_errors(tmp_path):
    """All validation errors are collected before raising, not just the first."""
    from llm_benchmark.domain.dataset_loader import load_dataset
    from llm_benchmark.domain.exceptions import DatasetValidationError

    # Two questions each missing a different required field
    q1 = make_open_question_dict("Q01")
    del q1["réponse"]
    q2 = make_open_question_dict("Q02")
    del q2["source"]
    data = make_dataset_dict([q1, q2])
    path = write_dataset_file(tmp_path, data)

    with pytest.raises(DatasetValidationError) as exc_info:
        load_dataset(path)

    # Should report at least one error per invalid question
    assert len(exc_info.value.errors) >= 2


# ---------------------------------------------------------------------------
# Rejection — unknown question type
# ---------------------------------------------------------------------------


def test_reject_unknown_question_type(tmp_path):
    """A dataset with an unknown question type raises DatasetValidationError."""
    from llm_benchmark.domain.dataset_loader import load_dataset
    from llm_benchmark.domain.exceptions import DatasetValidationError

    question = make_open_question_dict()
    question["type"] = "essay"  # not a valid type
    data = make_dataset_dict([question])
    path = write_dataset_file(tmp_path, data)

    with pytest.raises(DatasetValidationError) as exc_info:
        load_dataset(path)

    assert len(exc_info.value.errors) > 0


# ---------------------------------------------------------------------------
# Rejection — MCQ missing choices
# ---------------------------------------------------------------------------


def test_reject_mcq_question_missing_choices(tmp_path):
    """An MCQ question without choices raises DatasetValidationError."""
    from llm_benchmark.domain.dataset_loader import load_dataset
    from llm_benchmark.domain.exceptions import DatasetValidationError

    question = make_mcq_question_dict()
    del question["choices"]
    data = make_dataset_dict([question])
    path = write_dataset_file(tmp_path, data)

    with pytest.raises(DatasetValidationError) as exc_info:
        load_dataset(path)

    assert len(exc_info.value.errors) > 0


# ---------------------------------------------------------------------------
# system_prompt field
# ---------------------------------------------------------------------------


def test_dataset_system_prompt_defaults_to_empty_string(tmp_path):
    """When system_prompt is absent from the JSON, Dataset.system_prompt is ''."""
    from llm_benchmark.domain.dataset_loader import load_dataset

    data = make_dataset_dict([make_open_question_dict()])
    path = write_dataset_file(tmp_path, data)

    dataset = load_dataset(path)

    assert dataset.system_prompt == ""


def test_dataset_system_prompt_is_loaded_when_present(tmp_path):
    """When system_prompt is present in the JSON, it is loaded into Dataset."""
    from llm_benchmark.domain.dataset_loader import load_dataset

    data = make_dataset_dict([make_open_question_dict()])
    data["system_prompt"] = "Réponds uniquement par le nom de la molécule."
    path = write_dataset_file(tmp_path, data)

    dataset = load_dataset(path)

    assert dataset.system_prompt == "Réponds uniquement par le nom de la molécule."
