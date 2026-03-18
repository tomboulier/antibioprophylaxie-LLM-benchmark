"""Unit tests for MetricsCollector."""

from unittest.mock import MagicMock

from llm_benchmark.domain.entities import LLMResponse
from llm_benchmark.domain.metrics import MetricsCollector
from llm_benchmark.domain.value_objects import (
    CarbonFootprint,
    Cost,
    Latency,
    ModelId,
)

# ---------------------------------------------------------------------------
# Helpers / stubs
# ---------------------------------------------------------------------------


def _make_llm_port(price_in: float = 0.000001, price_out: float = 0.000002) -> MagicMock:
    """Return a minimal LLMPort stub with configurable token prices."""
    port = MagicMock()
    port.model_id = ModelId("test-model")
    port.price_per_input_token = Cost(price_in)
    port.price_per_output_token = Cost(price_out)
    return port


def _make_response(input_tokens: int | None, output_tokens: int | None) -> LLMResponse:
    """Return an LLMResponse with the given token counts."""
    return LLMResponse(
        text="answer",
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        latency=Latency(0.5),
    )


# ---------------------------------------------------------------------------
# compute_cost
# ---------------------------------------------------------------------------


class TestComputeCost:
    """Tests for MetricsCollector.compute_cost."""

    def test_returns_cost_with_known_prices_and_tokens(self) -> None:
        collector = MetricsCollector()
        llm = _make_llm_port(price_in=0.000001, price_out=0.000002)
        response = _make_response(input_tokens=1000, output_tokens=500)

        cost = collector.compute_cost(llm, response)

        assert cost is not None
        # 1000 * 0.000001 + 500 * 0.000002 = 0.001 + 0.001 = 0.002
        assert abs(cost.amount - 0.002) < 1e-9
        assert cost.currency == "USD"

    def test_returns_none_when_input_tokens_is_none(self) -> None:
        collector = MetricsCollector()
        llm = _make_llm_port()
        response = _make_response(input_tokens=None, output_tokens=500)

        assert collector.compute_cost(llm, response) is None

    def test_returns_none_when_output_tokens_is_none(self) -> None:
        collector = MetricsCollector()
        llm = _make_llm_port()
        response = _make_response(input_tokens=1000, output_tokens=None)

        assert collector.compute_cost(llm, response) is None

    def test_returns_none_when_both_tokens_are_none(self) -> None:
        collector = MetricsCollector()
        llm = _make_llm_port()
        response = _make_response(input_tokens=None, output_tokens=None)

        assert collector.compute_cost(llm, response) is None

    def test_zero_tokens_returns_zero_cost(self) -> None:
        collector = MetricsCollector()
        llm = _make_llm_port(price_in=0.001, price_out=0.002)
        response = _make_response(input_tokens=0, output_tokens=0)

        cost = collector.compute_cost(llm, response)

        assert cost is not None
        assert cost.amount == 0.0

    def test_currency_matches_llm_port_currency(self) -> None:
        collector = MetricsCollector()
        llm = _make_llm_port()
        llm.price_per_input_token = Cost(0.000001, "EUR")
        llm.price_per_output_token = Cost(0.000002, "EUR")
        response = _make_response(input_tokens=100, output_tokens=50)

        cost = collector.compute_cost(llm, response)

        assert cost is not None
        assert cost.currency == "EUR"


# ---------------------------------------------------------------------------
# carbon_tracker injection
# ---------------------------------------------------------------------------


class TestCarbonTrackerInjection:
    """Tests for MetricsCollector with an injected CarbonTrackerPort."""

    def test_stop_run_returns_none_when_no_tracker_injected(self) -> None:
        collector = MetricsCollector()
        assert collector.stop_run() is None

    def test_start_and_stop_run_delegates_to_tracker(self) -> None:
        mock_tracker = MagicMock()
        mock_tracker.stop.return_value = CarbonFootprint(5.0)

        collector = MetricsCollector(carbon_tracker=mock_tracker)
        collector.start_run()
        result = collector.stop_run()

        mock_tracker.start.assert_called_once()
        mock_tracker.stop.assert_called_once()
        assert result == CarbonFootprint(5.0)

    def test_stop_run_returns_none_when_tracker_not_started(self) -> None:
        mock_tracker = MagicMock()
        mock_tracker.stop.return_value = CarbonFootprint(1.0)

        collector = MetricsCollector(carbon_tracker=mock_tracker)
        # stop_run without start_run
        result = collector.stop_run()

        mock_tracker.stop.assert_not_called()
        assert result is None

    def test_stop_run_returns_none_when_tracker_raises(self) -> None:
        mock_tracker = MagicMock()
        mock_tracker.stop.side_effect = RuntimeError("tracker error")

        collector = MetricsCollector(carbon_tracker=mock_tracker)
        collector.start_run()
        result = collector.stop_run()

        assert result is None
