"""Tests de propriété (Hypothesis) pour les Value Objects du domaine.

Valide : Requirements 2.1, 2.2, 2.3, 4.6, 5.3
"""

import dataclasses

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

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
    RunId,
    Source,
)

# ---------------------------------------------------------------------------
# Propriété 1 : Immuabilité
# Valide : Requirements 2.1, 2.2, 2.3
# ---------------------------------------------------------------------------

_FROZEN_VOS = [
    (Cost, {"amount": 1.0, "currency": "USD"}),
    (Latency, {"seconds": 1.0}),
    (CarbonFootprint, {"g_co2e": 1.0}),
    (Accuracy, {"value": 0.5}),
    (ModelId, {"value": "gpt-4o"}),
    (ApproachId, {"value": "rag-pdf"}),
    (DatasetId, {"value": "sfar"}),
    (RunId, {"value": "run-1"}),
    (QuestionId, {"value": "Q01"}),
    (DatasetVersion, {"value": "1.0"}),
    (Source, {"value": "SFAR 2024"}),
    (MCQChoices, {"choices": {"A": "oui", "B": "non"}}),
]


@pytest.mark.parametrize("cls,kwargs", _FROZEN_VOS)
def test_immutability(cls, kwargs):
    """Tout Value Object frozen lève FrozenInstanceError à toute tentative de mutation.

    Valide : Requirements 2.1, 2.2, 2.3
    """
    obj = cls(**kwargs)
    field_name = next(iter(kwargs))
    with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
        object.__setattr__(obj, field_name, "mutated")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Propriété 2 : Invariants Cost
# Valide : Requirements 5.3
# ---------------------------------------------------------------------------


@given(
    st.floats(min_value=0, allow_nan=False, allow_infinity=False),
    st.sampled_from(["USD", "EUR"]),
)
def test_cost_valid(amount: float, currency: str) -> None:
    """Cost(amount, currency) est valide ssi amount >= 0 et currency in {"USD","EUR"}.

    Valide : Requirements 5.3
    """
    c = Cost(amount, currency)
    assert c.amount == amount
    assert c.currency == currency


@given(st.floats(max_value=-0.001, allow_nan=False, allow_infinity=False))
def test_cost_negative_invalid(amount: float) -> None:
    """Cost avec montant négatif lève ValueError.

    Valide : Requirements 5.3
    """
    with pytest.raises(ValueError):
        Cost(amount)


@given(
    st.floats(min_value=0, allow_nan=False, allow_infinity=False),
    st.text(min_size=1).filter(lambda s: s not in ("USD", "EUR")),
)
@settings(max_examples=50)
def test_cost_invalid_currency(amount: float, currency: str) -> None:
    """Cost avec devise non supportée lève ValueError.

    Valide : Requirements 5.3
    """
    with pytest.raises(ValueError):
        Cost(amount, currency)


# ---------------------------------------------------------------------------
# Propriété 3 : Invariants Accuracy
# Valide : Requirements 4.6
# ---------------------------------------------------------------------------


@given(st.floats(min_value=0.0, max_value=1.0, allow_nan=False))
def test_accuracy_valid_range(v: float) -> None:
    """Accuracy(v) est valide ssi 0.0 <= v <= 1.0 ; as_percent == v * 100.

    Valide : Requirements 4.6
    """
    a = Accuracy(v)
    assert abs(a.as_percent - v * 100) < 1e-9


@given(
    st.one_of(
        st.floats(max_value=-0.001, allow_nan=False, allow_infinity=False),
        st.floats(min_value=1.001, allow_nan=False, allow_infinity=False),
    )
)
def test_accuracy_out_of_range_invalid(v: float) -> None:
    """Accuracy hors [0, 1] lève ValueError.

    Valide : Requirements 4.6
    """
    with pytest.raises(ValueError):
        Accuracy(v)
