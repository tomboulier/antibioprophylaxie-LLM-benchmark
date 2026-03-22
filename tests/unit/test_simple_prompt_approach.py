"""Unit tests for SimplePromptApproach."""

import pytest

from llm_benchmark.adapters.approaches.simple_prompt import SimplePromptApproach
from llm_benchmark.domain.entities import Question
from llm_benchmark.domain.value_objects import (
    ApproachId,
    MCQChoices,
    QuestionId,
    QuestionType,
)


@pytest.fixture()
def approach() -> SimplePromptApproach:
    """Return a fresh SimplePromptApproach instance."""
    return SimplePromptApproach()


@pytest.fixture()
def open_question() -> Question:
    """Return a minimal open-ended question."""
    return Question(
        id=QuestionId("Q01"),
        question_type=QuestionType.OPEN,
        question_text="What is the recommended antibiotic?",
        expected_answer="Amoxicillin",
    )


@pytest.fixture()
def mcq_question() -> Question:
    """Return a minimal MCQ question with four choices."""
    return Question(
        id=QuestionId("Q02"),
        question_type=QuestionType.MCQ,
        question_text="Which antibiotic is first-line?",
        expected_answer="A",
        choices=MCQChoices(
            choices={
                "A": "Amoxicillin",
                "B": "Ciprofloxacin",
                "C": "Metronidazole",
                "D": "Vancomycin",
            }
        ),
    )


def test_approach_id(approach: SimplePromptApproach) -> None:
    """approach_id must return ApproachId('simple-prompt')."""
    assert approach.approach_id == ApproachId("simple-prompt")


def test_prepare_is_noop(approach: SimplePromptApproach) -> None:
    """prepare() must complete without raising any exception."""
    approach.prepare()  # should not raise


def test_build_prompt_open_question_returns_question_text(
    approach: SimplePromptApproach,
    open_question: Question,
) -> None:
    """build_prompt for an open question returns the question text verbatim."""
    prompt = approach.build_prompt(open_question)
    assert prompt == open_question.question_text


def test_build_prompt_mcq_contains_question_text(
    approach: SimplePromptApproach,
    mcq_question: Question,
) -> None:
    """build_prompt for an MCQ question starts with the question text."""
    prompt = approach.build_prompt(mcq_question)
    assert prompt.startswith(mcq_question.question_text)


def test_build_prompt_mcq_contains_all_choices(
    approach: SimplePromptApproach,
    mcq_question: Question,
) -> None:
    """build_prompt for an MCQ question includes every lettered choice."""
    prompt = approach.build_prompt(mcq_question)
    for key, value in mcq_question.choices.choices.items():
        assert f"{key}. {value}" in prompt


def test_build_prompt_mcq_format(
    approach: SimplePromptApproach,
    mcq_question: Question,
) -> None:
    """build_prompt for an MCQ question produces the expected full string."""
    expected = (
        "Which antibiotic is first-line?\n"
        "A. Amoxicillin\n"
        "B. Ciprofloxacin\n"
        "C. Metronidazole\n"
        "D. Vancomycin"
    )
    assert approach.build_prompt(mcq_question) == expected
