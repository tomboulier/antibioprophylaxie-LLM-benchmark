"""Unit tests for domain scorers.

Tests normalize(), OpenScorer, QCMScorer, SourcingScorer, and ScorerRegistry.
"""

import pytest

from llm_benchmark.domain.value_objects import (
    MCQChoices,
    QuestionId,
    QuestionType,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_open_question(expected_answer: str):
    """Build a minimal open Question for testing."""
    from llm_benchmark.domain.entities import Question

    return Question(
        id=QuestionId("q-001"),
        question_type=QuestionType.OPEN,
        question_text="Which antibiotic?",
        expected_answer=expected_answer,
    )


def make_mcq_question(expected_answer: str):
    """Build a minimal MCQ Question for testing."""
    from llm_benchmark.domain.entities import Question

    return Question(
        id=QuestionId("q-002"),
        question_type=QuestionType.MCQ,
        question_text="Which antibiotic?",
        expected_answer=expected_answer,
        choices=MCQChoices({"A": "Amoxicillin", "B": "Cefazolin", "C": "Clindamycin", "D": "None"}),
    )


# ---------------------------------------------------------------------------
# normalize()
# ---------------------------------------------------------------------------


class TestNormalize:
    """Tests for the normalize() helper function."""

    def test_lowercases_text(self):
        from llm_benchmark.domain.scorer import normalize

        assert normalize("CÉFAZOLINE") == "céfazoline"

    def test_strips_leading_whitespace(self):
        from llm_benchmark.domain.scorer import normalize

        assert normalize("  hello") == "hello"

    def test_strips_trailing_whitespace(self):
        from llm_benchmark.domain.scorer import normalize

        assert normalize("hello  ") == "hello"

    def test_collapses_multiple_spaces(self):
        from llm_benchmark.domain.scorer import normalize

        assert normalize("hello   world") == "hello world"

    def test_strips_trailing_period(self):
        from llm_benchmark.domain.scorer import normalize

        assert normalize("céfazoline.") == "céfazoline"

    def test_combined_transformations(self):
        from llm_benchmark.domain.scorer import normalize

        assert normalize("  CÉFAZOLINE.  ") == "céfazoline"

    def test_empty_string(self):
        from llm_benchmark.domain.scorer import normalize

        assert normalize("") == ""

    def test_no_change_already_normalized(self):
        from llm_benchmark.domain.scorer import normalize

        assert normalize("céfazoline") == "céfazoline"


# ---------------------------------------------------------------------------
# OpenScorer
# ---------------------------------------------------------------------------


class TestOpenScorer:
    """Tests for OpenScorer."""

    @pytest.fixture
    def scorer(self):
        from llm_benchmark.domain.scorer import OpenScorer

        return OpenScorer()

    def test_single_molecule_case_insensitive_correct(self, scorer):
        """'Céfazoline' expected, 'céfazoline' actual → correct."""
        question = make_open_question("Céfazoline")
        result = scorer.score(question, "céfazoline")
        assert result.is_correct is True

    def test_single_molecule_wrong_answer(self, scorer):
        """'Céfazoline' expected, 'Amoxicilline' actual → incorrect."""
        question = make_open_question("Céfazoline")
        result = scorer.score(question, "Amoxicilline")
        assert result.is_correct is False

    def test_multi_molecule_both_present_correct(self, scorer):
        """'Clindamycine + Gentamicine' expected, both present in actual → correct."""
        question = make_open_question("Clindamycine + Gentamicine")
        result = scorer.score(question, "Clindamycine + Gentamicine")
        assert result.is_correct is True

    def test_multi_molecule_one_missing_incorrect(self, scorer):
        """'Clindamycine + Gentamicine' expected, one missing → incorrect."""
        question = make_open_question("Clindamycine + Gentamicine")
        result = scorer.score(question, "Clindamycine")
        assert result.is_correct is False

    def test_non_expected_non_in_actual_correct(self, scorer):
        """'Non' expected, 'non' in actual → correct."""
        question = make_open_question("Non")
        result = scorer.score(question, "non")
        assert result.is_correct is True

    def test_non_expected_pas_d_in_actual_correct(self, scorer):
        """'Non' expected, 'pas d'antibioprophylaxie' in actual → correct."""
        question = make_open_question("Non")
        result = scorer.score(question, "pas d'antibioprophylaxie")
        assert result.is_correct is True

    def test_non_expected_molecule_in_actual_incorrect(self, scorer):
        """'Non' expected, 'Céfazoline' in actual → incorrect."""
        question = make_open_question("Non")
        result = scorer.score(question, "Céfazoline")
        assert result.is_correct is False

    def test_hors_perimetre_case_insensitive_correct(self, scorer):
        """'Hors périmètre' expected, 'hors périmètre' in actual → correct."""
        question = make_open_question("Hors périmètre")
        result = scorer.score(question, "hors périmètre")
        assert result.is_correct is True

    def test_mixed_case_in_actual_correct(self, scorer):
        """Mixed case in actual → correct (case-insensitive matching)."""
        question = make_open_question("Céfazoline")
        result = scorer.score(question, "La réponse est CÉFAZOLINE pour ce patient.")
        assert result.is_correct is True

    def test_returns_score_result(self, scorer):
        """score() returns a ScoreResult instance."""
        from llm_benchmark.domain.entities import ScoreResult

        question = make_open_question("Céfazoline")
        result = scorer.score(question, "céfazoline")
        assert isinstance(result, ScoreResult)


# ---------------------------------------------------------------------------
# QCMScorer
# ---------------------------------------------------------------------------


class TestQCMScorer:
    """Tests for QCMScorer."""

    @pytest.fixture
    def scorer(self):
        from llm_benchmark.domain.scorer import QCMScorer

        return QCMScorer()

    def test_letter_alone_correct(self, scorer):
        """'B' expected, 'B' actual → correct."""
        question = make_mcq_question("B")
        result = scorer.score(question, "B")
        assert result.is_correct is True

    def test_letter_in_sentence_correct(self, scorer):
        """'B' expected, 'La réponse est B.' actual → correct."""
        question = make_mcq_question("B")
        result = scorer.score(question, "La réponse est B.")
        assert result.is_correct is True

    def test_wrong_letter_incorrect(self, scorer):
        """'B' expected, 'A' actual → incorrect."""
        question = make_mcq_question("B")
        result = scorer.score(question, "A")
        assert result.is_correct is False

    def test_no_letter_found_incorrect(self, scorer):
        """'B' expected, 'je ne sais pas' actual → incorrect."""
        question = make_mcq_question("B")
        result = scorer.score(question, "je ne sais pas")
        assert result.is_correct is False

    def test_returns_score_result(self, scorer):
        """score() returns a ScoreResult instance."""
        from llm_benchmark.domain.entities import ScoreResult

        question = make_mcq_question("A")
        result = scorer.score(question, "A")
        assert isinstance(result, ScoreResult)

    def test_case_insensitive_letter_extraction(self, scorer):
        """Letter extraction is case-insensitive: 'b' matches 'B'."""
        question = make_mcq_question("B")
        result = scorer.score(question, "b")
        assert result.is_correct is True


# ---------------------------------------------------------------------------
# SourcingScorer
# ---------------------------------------------------------------------------


class TestSourcingScorer:
    """Tests for SourcingScorer."""

    @pytest.fixture
    def scorer(self):
        from llm_benchmark.domain.scorer import SourcingScorer

        return SourcingScorer()

    def test_source_present_detected(self, scorer):
        """Response contains a source reference → present=True."""
        question = make_open_question("Céfazoline")
        result = scorer.score(
            question, "Selon les recommandations SFAR 2024, la réponse est Céfazoline."
        )
        assert result.is_sourcing_present is True
        assert result.is_sourcing_correct is False

    def test_no_source_reference_in_response(self, scorer):
        """Response has no source reference → present=False, correct=False."""
        question = make_open_question("Céfazoline")
        result = scorer.score(question, "Céfazoline")
        assert result.is_sourcing_present is False
        assert result.is_sourcing_correct is False

    def test_returns_score_result(self, scorer):
        """score() returns a ScoreResult instance."""
        from llm_benchmark.domain.entities import ScoreResult

        question = make_open_question("Céfazoline")
        result = scorer.score(question, "Céfazoline")
        assert isinstance(result, ScoreResult)


# ---------------------------------------------------------------------------
# ScorerRegistry
# ---------------------------------------------------------------------------


class TestScorerRegistry:
    """Tests for ScorerRegistry."""

    @pytest.fixture
    def registry(self):
        from llm_benchmark.domain.scorer import ScorerRegistry

        return ScorerRegistry()

    def test_score_open_question_delegates_to_open_scorer(self, registry):
        """score(open_question, actual) delegates to OpenScorer and returns ScoreResult."""
        from llm_benchmark.domain.entities import ScoreResult

        question = make_open_question("Céfazoline")
        result = registry.score(question, "céfazoline")
        assert isinstance(result, ScoreResult)
        assert result.is_correct is True

    def test_score_mcq_question_delegates_to_qcm_scorer(self, registry):
        """score(mcq_question, actual) delegates to QCMScorer and returns ScoreResult."""
        from llm_benchmark.domain.entities import ScoreResult

        question = make_mcq_question("B")
        result = registry.score(question, "B")
        assert isinstance(result, ScoreResult)
        assert result.is_correct is True

    def test_score_open_incorrect(self, registry):
        """Registry correctly propagates incorrect result for open question."""
        question = make_open_question("Céfazoline")
        result = registry.score(question, "Amoxicilline")
        assert result.is_correct is False

    def test_score_mcq_incorrect(self, registry):
        """Registry correctly propagates incorrect result for MCQ question."""
        question = make_mcq_question("B")
        result = registry.score(question, "A")
        assert result.is_correct is False

    def test_score_includes_sourcing_fields(self, registry):
        """ScoreResult from registry includes sourcing fields."""
        question = make_open_question("Céfazoline")
        result = registry.score(question, "Selon SFAR 2024, Céfazoline.")
        assert hasattr(result, "is_sourcing_present")
        assert hasattr(result, "is_sourcing_correct")
