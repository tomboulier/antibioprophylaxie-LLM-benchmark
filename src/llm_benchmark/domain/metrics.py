"""Domain metrics collector.

Pure domain service — zero external dependencies.
Carbon tracking is delegated to an optional ``CarbonTrackerPort`` adapter
injected at construction time.
"""

from __future__ import annotations

from llm_benchmark.domain.entities import LLMResponse
from llm_benchmark.domain.value_objects import CarbonFootprint, Cost
from llm_benchmark.ports.carbon_tracker import CarbonTrackerPort
from llm_benchmark.ports.llm import LLMPort


class MetricsCollector:
    """Collect operational metrics for a benchmark run.

    Computes monetary cost from token counts and LLM pricing, and
    optionally tracks carbon emissions via an injected adapter.

    Parameters
    ----------
    carbon_tracker : CarbonTrackerPort or None, optional
        Adapter responsible for measuring CO2 emissions. When ``None``,
        carbon tracking is disabled and ``stop_run`` always returns ``None``.
    """

    def __init__(self, carbon_tracker: CarbonTrackerPort | None = None) -> None:
        self._carbon_tracker = carbon_tracker
        self._run_started = False

    def start_run(self) -> None:
        """Signal the start of a benchmark run.

        Activates the carbon tracker if one was provided.

        Returns
        -------
        None
        """
        if self._carbon_tracker is not None:
            self._carbon_tracker.start()
        self._run_started = True

    def stop_run(self) -> CarbonFootprint | None:
        """Signal the end of a benchmark run and return carbon footprint.

        Returns ``None`` if no tracker was provided, if ``start_run`` was
        never called, or if the tracker raises an exception.

        Returns
        -------
        CarbonFootprint or None
            Measured carbon footprint, or ``None`` when unavailable.
        """
        if not self._run_started or self._carbon_tracker is None:
            return None
        try:
            return self._carbon_tracker.stop()
        except Exception:  # noqa: BLE001
            return None

    def compute_cost(self, llm: LLMPort, response: LLMResponse) -> Cost | None:
        """Estimate the monetary cost of a single LLM response.

        Returns ``None`` when token counts are unavailable (the LLM did not
        report them), so callers must handle the optional gracefully.

        Parameters
        ----------
        llm : LLMPort
            The LLM adapter that produced the response, carrying pricing info.
        response : LLMResponse
            The response whose token counts are used for cost calculation.

        Returns
        -------
        Cost or None
            Estimated cost, or ``None`` if token counts are missing.
        """
        if response.input_tokens is None or response.output_tokens is None:
            return None

        input_cost = llm.price_per_input_token.amount * response.input_tokens
        output_cost = llm.price_per_output_token.amount * response.output_tokens
        total = input_cost + output_cost
        currency = llm.price_per_input_token.currency
        return Cost(amount=total, currency=currency)
