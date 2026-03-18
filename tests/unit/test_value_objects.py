"""Unit tests for domain Value Objects."""

import dataclasses

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
    RunId,
    Source,
)

# ---------------------------------------------------------------------------
# Cost
# ---------------------------------------------------------------------------


def test_cost_zero_valid():
    c = Cost(0.0)
    assert c.amount == 0.0
    assert c.currency == "USD"


def test_cost_eur_valid():
    c = Cost(1.5, "EUR")
    assert c.amount == 1.5
    assert c.currency == "EUR"


def test_cost_negative_raises():
    with pytest.raises(ValueError):
        Cost(-0.1)


def test_cost_unsupported_currency_raises():
    with pytest.raises(ValueError):
        Cost(1.0, "GBP")


# ---------------------------------------------------------------------------
# Latency
# ---------------------------------------------------------------------------


def test_latency_zero_valid():
    assert Latency(0.0).seconds == 0.0


def test_latency_positive_valid():
    assert Latency(1.5).seconds == 1.5


def test_latency_negative_raises():
    with pytest.raises(ValueError):
        Latency(-0.1)


# ---------------------------------------------------------------------------
# CarbonFootprint
# ---------------------------------------------------------------------------


def test_carbon_zero_valid():
    assert CarbonFootprint(0.0).g_co2e == 0.0


def test_carbon_negative_raises():
    with pytest.raises(ValueError):
        CarbonFootprint(-1.0)


# ---------------------------------------------------------------------------
# Accuracy
# ---------------------------------------------------------------------------


def test_accuracy_zero_valid():
    assert Accuracy(0.0).value == 0.0


def test_accuracy_one_valid():
    assert Accuracy(1.0).value == 1.0


def test_accuracy_mid_valid():
    assert Accuracy(0.5).value == 0.5


def test_accuracy_negative_raises():
    with pytest.raises(ValueError):
        Accuracy(-0.1)


def test_accuracy_above_one_raises():
    with pytest.raises(ValueError):
        Accuracy(1.1)


def test_accuracy_as_percent():
    assert Accuracy(0.75).as_percent == 75.0


# ---------------------------------------------------------------------------
# String-based Value Objects (ModelId, ApproachId, DatasetId, RunId,
# QuestionId, DatasetVersion, Source)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "cls",
    [ModelId, ApproachId, DatasetId, RunId, QuestionId, DatasetVersion, Source],
)
def test_string_vo_valid(cls):
    obj = cls("some-value")
    assert obj.value == "some-value"


@pytest.mark.parametrize(
    "cls",
    [ModelId, ApproachId, DatasetId, RunId, QuestionId, DatasetVersion, Source],
)
def test_string_vo_empty_raises(cls):
    with pytest.raises(ValueError):
        cls("")


@pytest.mark.parametrize(
    "cls",
    [ModelId, ApproachId, DatasetId, RunId, QuestionId, DatasetVersion, Source],
)
def test_string_vo_whitespace_raises(cls):
    with pytest.raises(ValueError):
        cls("   ")


# ---------------------------------------------------------------------------
# MCQChoices
# ---------------------------------------------------------------------------


def test_mcq_choices_valid():
    m = MCQChoices({"A": "oui", "B": "non"})
    assert m.choices == {"A": "oui", "B": "non"}


def test_mcq_choices_empty_raises():
    with pytest.raises(ValueError):
        MCQChoices({})


def test_mcq_choices_invalid_key_single_raises():
    with pytest.raises(ValueError):
        MCQChoices({"E": "invalide"})


def test_mcq_choices_mixed_invalid_key_raises():
    with pytest.raises(ValueError):
        MCQChoices({"A": "ok", "Z": "bad"})


# ---------------------------------------------------------------------------
# Immuabilité
# ---------------------------------------------------------------------------


def test_cost_immutable():
    c = Cost(1.0)
    with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
        c.amount = 5.0  # type: ignore[misc]
