"""Property-based tests for the dataset loader.

**Validates: Requirements 1.3**
"""

import json
import tempfile
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

# All required fields for a question
REQUIRED_QUESTION_FIELDS = ["id", "type", "question", "réponse", "source"]

# A strategy for a non-empty, non-whitespace-only string
non_empty_text = st.text(min_size=1).filter(lambda s: s.strip())

valid_question_strategy = st.fixed_dictionaries(
    {
        "id": non_empty_text,
        "type": st.just("open"),
        "question": non_empty_text,
        "réponse": non_empty_text,
        "source": non_empty_text,
    }
)

valid_dataset_strategy = st.fixed_dictionaries(
    {
        "id": non_empty_text,
        "version": non_empty_text,
        "source": non_empty_text,
        "scope": non_empty_text,
        "questions": st.lists(valid_question_strategy, min_size=1, max_size=5),
    }
)


def strategy_question_with_missing_field():
    """Generate a question dict with at least one required field removed."""

    @st.composite
    def _build(draw):
        question = draw(valid_question_strategy)
        # Pick at least one field to remove
        fields_to_remove = draw(
            st.lists(
                st.sampled_from(REQUIRED_QUESTION_FIELDS),
                min_size=1,
                max_size=len(REQUIRED_QUESTION_FIELDS),
                unique=True,
            )
        )
        for field in fields_to_remove:
            question.pop(field, None)
        return question

    return _build()


# ---------------------------------------------------------------------------
# Property 4: Exhaustive rejection
# ---------------------------------------------------------------------------


@given(
    dataset=valid_dataset_strategy,
    invalid_questions=st.lists(strategy_question_with_missing_field(), min_size=1, max_size=3),
)
@settings(max_examples=100)
def test_property_exhaustive_rejection(dataset, invalid_questions):
    """Property 4: Exhaustive rejection.

    For any JSON where at least one question is missing a required field,
    ``load_dataset`` raises ``DatasetValidationError`` and the error list
    is non-empty.

    **Validates: Requirements 1.3**
    """
    from llm_benchmark.domain.dataset_loader import load_dataset
    from llm_benchmark.domain.exceptions import DatasetValidationError

    # Replace the questions list with at least one invalid question
    dataset["questions"] = invalid_questions

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as tmp_file:
        json.dump(dataset, tmp_file, ensure_ascii=False)
        tmp_path = Path(tmp_file.name)

    try:
        with pytest.raises(DatasetValidationError) as exc_info:
            load_dataset(tmp_path)
        assert len(exc_info.value.errors) > 0, (
            "DatasetValidationError must contain at least one error message"
        )
    finally:
        tmp_path.unlink(missing_ok=True)
