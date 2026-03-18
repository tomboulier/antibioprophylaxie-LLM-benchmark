"""Property-based tests for domain scorers.

**Validates: Requirements 4.1, 4.2**
"""

from hypothesis import given, settings
from hypothesis import strategies as st

from llm_benchmark.domain.value_objects import (
    MCQChoices,
    QuestionId,
    QuestionType,
)

# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

text_strategy = st.text(min_size=0, max_size=200)

molecule_strategy = st.text(
    alphabet=st.characters(
        whitelist_categories=("Lu", "Ll"), whitelist_characters=" éèêëàâùûüîïôçæœ"
    ),
    min_size=3,
    max_size=30,
).filter(lambda s: s.strip())

valid_letter_strategy = st.sampled_from(["A", "B", "C", "D"])


def make_open_question(expected_answer: str):
    """Build a minimal open Question for property testing."""
    from llm_benchmark.domain.entities import Question

    return Question(
        id=QuestionId("q-prop"),
        question_type=QuestionType.OPEN,
        question_text="Which antibiotic?",
        expected_answer=expected_answer,
    )


def make_mcq_question(expected_answer: str):
    """Build a minimal MCQ Question for property testing."""
    from llm_benchmark.domain.entities import Question

    return Question(
        id=QuestionId("q-prop"),
        question_type=QuestionType.MCQ,
        question_text="Which antibiotic?",
        expected_answer=expected_answer,
        choices=MCQChoices({"A": "opt A", "B": "opt B", "C": "opt C", "D": "opt D"}),
    )


# ---------------------------------------------------------------------------
# Property 5: Determinism
# Validates: Requirements 4.1, 4.2
# ---------------------------------------------------------------------------


@given(expected=molecule_strategy, actual=text_strategy)
@settings(max_examples=100)
def test_property_open_scorer_determinism(expected: str, actual: str) -> None:
    """Property 5: Determinism — OpenScorer returns identical ScoreResult on repeated calls.

    For any (expected, actual) string pair, calling scorer.score twice returns
    identical ScoreResult objects.

    **Validates: Requirements 4.1, 4.2**
    """
    from llm_benchmark.domain.scorer import OpenScorer

    scorer = OpenScorer()
    question = make_open_question(expected)

    result_1 = scorer.score(question, actual)
    result_2 = scorer.score(question, actual)

    assert result_1.is_correct == result_2.is_correct
    assert result_1.is_sourcing_present == result_2.is_sourcing_present
    assert result_1.is_sourcing_correct == result_2.is_sourcing_correct


@given(expected=valid_letter_strategy, actual=text_strategy)
@settings(max_examples=100)
def test_property_qcm_scorer_determinism(expected: str, actual: str) -> None:
    """Property 5: Determinism — QCMScorer returns identical ScoreResult on repeated calls.

    For any (expected, actual) string pair, calling scorer.score twice returns
    identical ScoreResult objects.

    **Validates: Requirements 4.1, 4.2**
    """
    from llm_benchmark.domain.scorer import QCMScorer

    scorer = QCMScorer()
    question = make_mcq_question(expected)

    result_1 = scorer.score(question, actual)
    result_2 = scorer.score(question, actual)

    assert result_1.is_correct == result_2.is_correct
    assert result_1.is_sourcing_present == result_2.is_sourcing_present
    assert result_1.is_sourcing_correct == result_2.is_sourcing_correct


# ---------------------------------------------------------------------------
# Property 6: Normalization idempotency
# Validates: Requirements 4.1
# ---------------------------------------------------------------------------


@given(text_strategy)
@settings(max_examples=200)
def test_property_normalize_idempotency(text: str) -> None:
    """Property 6: Normalization idempotency — normalize(normalize(s)) == normalize(s).

    Applying normalize twice produces the same result as applying it once.

    **Validates: Requirements 4.1**
    """
    from llm_benchmark.domain.scorer import normalize

    once = normalize(text)
    twice = normalize(once)

    assert once == twice, f"normalize not idempotent for {text!r}: {once!r} != {twice!r}"


# ---------------------------------------------------------------------------
# Property 7: QCM correctness
# Validates: Requirements 4.2
# ---------------------------------------------------------------------------


@given(
    expected=valid_letter_strategy,
    actual_letter=st.one_of(st.none(), valid_letter_strategy),
    prefix=text_strategy,
    suffix=text_strategy,
)
@settings(max_examples=100)
def test_property_qcm_correctness(
    expected: str,
    actual_letter: str | None,
    prefix: str,
    suffix: str,
) -> None:
    """Property 7: QCM correctness — QCMScorer returns is_correct=True iff extracted letter matches expected.

    QCMScorer returns is_correct=True if and only if the extracted letter
    matches the expected letter exactly.

    **Validates: Requirements 4.2**
    """
    import re

    from llm_benchmark.domain.scorer import QCMScorer

    scorer = QCMScorer()
    question = make_mcq_question(expected)

    if actual_letter is not None:
        # Build an actual string that contains the letter as a word boundary
        # Strip any A-D letters from prefix/suffix to avoid ambiguity
        clean_prefix = re.sub(r"\b[A-Da-d]\b", "", prefix).strip()
        clean_suffix = re.sub(r"\b[A-Da-d]\b", "", suffix).strip()
        actual = f"{clean_prefix} {actual_letter} {clean_suffix}".strip()
    else:
        # Build an actual string with no A-D letter
        actual = re.sub(r"\b[A-Da-d]\b", "", prefix + suffix)

    result = scorer.score(question, actual)

    if actual_letter is not None:
        # Re-extract what the scorer would find to verify our expectation
        match = re.search(r"\b([A-D])\b", actual.upper())
        extracted = match.group(1) if match else None
        expected_correct = extracted == expected.upper()
        assert result.is_correct == expected_correct, (
            f"expected={expected!r}, actual={actual!r}, "
            f"extracted={extracted!r}, result.is_correct={result.is_correct}"
        )
    else:
        # No letter in actual → should be incorrect
        assert result.is_correct is False, (
            f"expected={expected!r}, actual={actual!r} (no letter), "
            f"result.is_correct should be False"
        )
