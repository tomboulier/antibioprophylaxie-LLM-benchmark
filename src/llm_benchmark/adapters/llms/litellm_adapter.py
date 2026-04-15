"""LiteLLM adapter — universal LLM backend via the LiteLLM library."""

from __future__ import annotations

import time

import litellm
from litellm.exceptions import RateLimitError

from llm_benchmark.domain.entities import LLMRequest, LLMResponse
from llm_benchmark.domain.value_objects import Cost, Latency, ModelId
from llm_benchmark.ports.llm import LLMPort

_MAX_RETRIES = 5
_INITIAL_BACKOFF_S = 1.0


class LiteLLMAdapter(LLMPort):
    """Universal LLM adapter backed by LiteLLM.

    Supports 100+ providers (Anthropic, OpenAI, Mistral, etc.) through a
    single interface. Pricing is declared at construction time and used by
    ``MetricsCollector`` to estimate per-question costs.

    Rate-limit errors (HTTP 429) are retried up to ``_MAX_RETRIES`` times
    with exponential backoff.

    Parameters
    ----------
    model : str
        LiteLLM model string passed to ``litellm.completion()``
        (e.g. ``"mistral/mistral-small-latest"``).
    price_per_input_token : Cost
        Cost charged per input (prompt) token.
    price_per_output_token : Cost
        Cost charged per output (completion) token.
    model_alias : str | None
        User-facing model identifier (e.g. ``"mistral-small-latest"``).
        When ``None``, defaults to ``model``.
    """

    def __init__(
        self,
        model: str,
        price_per_input_token: Cost,
        price_per_output_token: Cost,
        model_alias: str | None = None,
    ) -> None:
        self._litellm_model = model
        self._model_id = ModelId(model_alias if model_alias is not None else model)
        self._price_in = price_per_input_token
        self._price_out = price_per_output_token

    @property
    def model_id(self) -> ModelId:
        """Identifier of the underlying model.

        Returns
        -------
        ModelId
            The model identifier.
        """
        return self._model_id

    @property
    def price_per_input_token(self) -> Cost:
        """Cost charged per input token.

        Returns
        -------
        Cost
            Price per input token.
        """
        return self._price_in

    @property
    def price_per_output_token(self) -> Cost:
        """Cost charged per output token.

        Returns
        -------
        Cost
            Price per output token.
        """
        return self._price_out

    def complete(self, request: LLMRequest) -> LLMResponse:
        """Send a prompt to the model and return the response with metrics.

        Retries automatically on rate-limit errors (HTTP 429) with
        exponential backoff (1s, 2s, 4s, 8s, 16s).

        Parameters
        ----------
        request : LLMRequest
            The prompt and generation parameters.

        Returns
        -------
        LLMResponse
            Generated text with token counts and latency.

        Raises
        ------
        Exception
            Any exception raised by LiteLLM is propagated to the caller
            after all retry attempts are exhausted.
        """
        backoff = _INITIAL_BACKOFF_S
        last_exc: Exception | None = None

        for attempt in range(_MAX_RETRIES):
            try:
                start_time = time.perf_counter()
                raw_response = litellm.completion(
                    model=self._litellm_model,
                    messages=[
                        {"role": "system", "content": request.system_prompt},
                        {"role": "user", "content": request.user_prompt},
                    ],
                    max_tokens=request.max_tokens,
                )
                latency = Latency(time.perf_counter() - start_time)

                return LLMResponse(
                    text=raw_response.choices[0].message.content,
                    input_tokens=raw_response.usage.prompt_tokens,
                    output_tokens=raw_response.usage.completion_tokens,
                    latency=latency,
                    raw=raw_response.model_dump(),
                )
            except RateLimitError as exc:
                last_exc = exc
                if attempt < _MAX_RETRIES - 1:
                    time.sleep(backoff)
                    backoff *= 2

        raise last_exc  # type: ignore[misc]
