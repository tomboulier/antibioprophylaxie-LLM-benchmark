"""Dataset loader for llm-benchmark.

Loads and validates a dataset from a JSON file, returning a ``Dataset`` entity.
Zero external dependencies — stdlib only (``json``, ``pathlib``).
"""

import json
from pathlib import Path

from llm_benchmark.domain.entities import Dataset, Question
from llm_benchmark.domain.exceptions import DatasetValidationError
from llm_benchmark.domain.value_objects import (
    DatasetId,
    DatasetVersion,
    MCQChoices,
    QuestionId,
    QuestionType,
    Source,
)

# Required fields at the top level of the dataset JSON.
_REQUIRED_DATASET_FIELDS = ("id", "version", "source", "scope", "questions")

# Required fields for every question, regardless of type.
_REQUIRED_QUESTION_FIELDS = ("id", "type", "question", "réponse", "source")

# Mapping from JSON string to QuestionType enum value.
_QUESTION_TYPE_MAP: dict[str, QuestionType] = {
    "open": QuestionType.OPEN,
    "mcq": QuestionType.MCQ,
}


def load_dataset(path: Path) -> Dataset:
    """Load and validate a dataset from a JSON file.

    Reads the file at *path*, validates all required fields, and returns a
    fully constructed :class:`~llm_benchmark.domain.entities.Dataset`.

    All validation errors are collected before raising so that callers
    receive a complete picture of what is wrong.

    Parameters
    ----------
    path : Path
        Absolute or relative path to the dataset JSON file.

    Returns
    -------
    Dataset
        The validated dataset entity.

    Raises
    ------
    DatasetValidationError
        If any required field is missing or any question type is unknown.
        The ``errors`` attribute contains one message per validation failure.
    FileNotFoundError
        If *path* does not exist.
    json.JSONDecodeError
        If the file is not valid JSON.
    """
    raw = json.loads(path.read_text(encoding="utf-8"))
    errors: list[str] = []

    questions = _validate_and_build_questions(raw, errors)

    if errors:
        raise DatasetValidationError(errors)

    return Dataset(
        id=DatasetId(raw["id"]),
        version=DatasetVersion(raw["version"]),
        source=Source(raw["source"]),
        scope=raw["scope"],
        questions=questions,
    )


def _validate_and_build_questions(raw: dict, errors: list[str]) -> list[Question]:
    """Validate the dataset dict and build Question entities.

    Appends error messages to *errors* for every validation failure found.
    Returns the list of successfully built questions (may be empty if errors
    were found).

    Parameters
    ----------
    raw : dict
        Parsed JSON content of the dataset file.
    errors : list[str]
        Mutable list to which error messages are appended.

    Returns
    -------
    list[Question]
        Successfully constructed questions (empty when errors exist).
    """
    questions: list[Question] = []

    raw_questions = raw.get("questions")
    if not isinstance(raw_questions, list):
        errors.append("Top-level 'questions' field is missing or not a list.")
        return questions

    for index, question_dict in enumerate(raw_questions):
        question = _validate_and_build_question(question_dict, index, errors)
        if question is not None:
            questions.append(question)

    return questions


def _validate_and_build_question(
    question_dict: dict, index: int, errors: list[str]
) -> Question | None:
    """Validate a single question dict and build a Question entity.

    Parameters
    ----------
    question_dict : dict
        Raw question data from the JSON file.
    index : int
        Zero-based position of this question in the questions list (for
        error messages).
    errors : list[str]
        Mutable list to which error messages are appended.

    Returns
    -------
    Question or None
        The constructed question, or ``None`` if any validation error was found.
    """
    question_errors: list[str] = []
    label = question_dict.get("id", f"index {index}")

    for field in _REQUIRED_QUESTION_FIELDS:
        if field not in question_dict:
            question_errors.append(f"Question '{label}': missing required field '{field}'.")

    if question_errors:
        errors.extend(question_errors)
        return None

    raw_type = question_dict["type"]
    question_type = _QUESTION_TYPE_MAP.get(raw_type)
    if question_type is None:
        errors.append(
            f"Question '{label}': unknown type '{raw_type}'. "
            f"Valid types are: {sorted(_QUESTION_TYPE_MAP.keys())}."
        )
        return None

    if question_type == QuestionType.MCQ:
        if "choices" not in question_dict:
            errors.append(f"Question '{label}': MCQ question is missing required field 'choices'.")
            return None
        choices = MCQChoices(question_dict["choices"])
    else:
        choices = None

    return Question(
        id=QuestionId(question_dict["id"]),
        question_type=question_type,
        question_text=question_dict["question"],
        expected_answer=question_dict["réponse"],
        source=Source(question_dict["source"]),
        choices=choices,
    )
