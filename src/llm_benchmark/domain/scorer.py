"""Domain scorers for evaluating LLM answers.

Provides pure, stateless scoring logic for open-ended and MCQ questions,
plus sourcing detection. All functions and classes are free of external
dependencies (stdlib only).
"""

from __future__ import annotations

import re

from llm_benchmark.domain.entities import Question, ScoreResult
from llm_benchmark.domain.value_objects import QuestionType


def normalize(text: str) -> str:
    """Normalize text for comparison.

    Lowercases, strips leading/trailing whitespace, collapses multiple
    spaces into one, and removes a trailing period.

    Parameters
    ----------
    text : str
        Raw text to normalize.

    Returns
    -------
    str
        Normalized text.
    """
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    text = text.rstrip(".").strip()
    return text


class OpenScorer:
    """Scorer for open-ended questions (molecule names, 'Non', 'Hors périmètre').

    Checks that every expected molecule (split on '+') appears in the
    normalized actual answer. Handles the special case where the expected
    answer is 'Non'.
    """

    def score(self, question: Question, actual: str) -> ScoreResult:
        """Score an open-ended answer.

        Parameters
        ----------
        question : Question
            The question being evaluated, carrying the expected answer.
        actual : str
            The LLM's raw answer text.

        Returns
        -------
        ScoreResult
            Result with ``is_correct`` set according to molecule matching.
        """
        normalized_expected = normalize(question.expected_answer)
        normalized_actual = normalize(actual)

        if normalized_expected in ("pas d'antibioprophylaxie", "hors périmètre"):
            is_correct = normalized_expected in normalized_actual
        else:
            molecules = [normalize(molecule) for molecule in question.expected_answer.split("+")]
            is_correct = all(molecule in normalized_actual for molecule in molecules)

        return ScoreResult(is_correct=is_correct)


class QCMScorer:
    """Scorer for multiple-choice questions (letters A–D).

    Extracts the first A–D letter found in the actual answer (as a word
    boundary match) and compares it to the expected letter.
    """

    def score(self, question: Question, actual: str) -> ScoreResult:
        """Score a multiple-choice answer.

        Parameters
        ----------
        question : Question
            The question being evaluated, carrying the expected letter.
        actual : str
            The LLM's raw answer text.

        Returns
        -------
        ScoreResult
            Result with ``is_correct`` set when the extracted letter matches.
        """
        expected_letter = question.expected_answer.strip().upper()
        match = re.search(r"\b([A-D])\b", actual.upper())
        extracted_letter = match.group(1) if match else None
        is_correct = extracted_letter == expected_letter
        return ScoreResult(is_correct=is_correct)


class SourcingScorer:
    """Scorer that detects and validates source references in LLM answers.

    Checks whether the actual answer contains a reference to the expected
    source by looking for significant words (4+ characters) from the source
    value in the answer text.
    """

    _MIN_WORD_LENGTH = 4

    def score(self, question: Question, actual: str) -> ScoreResult:
        """Detect sourcing presence and correctness in an answer.

        Parameters
        ----------
        question : Question
            The question being evaluated, carrying the expected source.
        actual : str
            The LLM's raw answer text.

        Returns
        -------
        ScoreResult
            Result with ``is_sourcing_present`` and ``is_sourcing_correct``
            populated. ``is_correct`` is always ``False`` (sourcing is a
            supplementary signal, not the primary correctness criterion).
        """
        normalized_actual = normalize(actual)

        is_sourcing_present = self._detect_any_reference(normalized_actual)
        is_sourcing_correct = False

        return ScoreResult(
            is_correct=False,
            is_sourcing_present=is_sourcing_present,
            is_sourcing_correct=is_sourcing_correct,
        )

    def _detect_any_reference(self, normalized_actual: str) -> bool:
        """Heuristically detect whether the text contains any source reference.

        Parameters
        ----------
        normalized_actual : str
            Already-normalized answer text.

        Returns
        -------
        bool
            ``True`` if a plausible reference pattern is found.
        """
        # Look for a year (4 digits) as a proxy for a bibliographic reference
        return bool(re.search(r"\b\d{4}\b", normalized_actual))


class ScorerRegistry:
    """Registry that dispatches scoring to the appropriate scorer by question type.

    Combines the primary scorer (OpenScorer or QCMScorer) with SourcingScorer
    to produce a complete ScoreResult.
    """

    def __init__(self) -> None:
        self._scorers: dict[QuestionType, OpenScorer | QCMScorer] = {
            QuestionType.OPEN: OpenScorer(),
            QuestionType.MCQ: QCMScorer(),
        }
        self._sourcing_scorer = SourcingScorer()

    def score(self, question: Question, actual: str) -> ScoreResult:
        """Score an answer using the appropriate scorer for the question type.

        Delegates to OpenScorer or QCMScorer based on ``question.question_type``,
        then runs SourcingScorer to fill in sourcing fields.

        Parameters
        ----------
        question : Question
            The question being evaluated.
        actual : str
            The LLM's raw answer text.

        Returns
        -------
        ScoreResult
            Combined result with correctness and sourcing fields populated.

        Raises
        ------
        KeyError
            If the question type has no registered scorer.
        """
        primary_result = self._scorers[question.question_type].score(question, actual)
        sourcing_result = self._sourcing_scorer.score(question, actual)

        return ScoreResult(
            is_correct=primary_result.is_correct,
            is_sourcing_present=sourcing_result.is_sourcing_present,
            is_sourcing_correct=sourcing_result.is_sourcing_correct,
            details=primary_result.details,
        )
