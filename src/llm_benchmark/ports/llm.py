"""LLMPort — abstract interface for large language model adapters."""

from abc import ABC, abstractmethod

from llm_benchmark.domain.entities import LLMRequest, LLMResponse
from llm_benchmark.domain.value_objects import Cost, ModelId


class LLMPort(ABC):
    """Contract that every LLM adapter must fulfil.

    An LLM adapter wraps a specific provider (Anthropic, OpenAI, Mistral,
    etc.) and exposes a uniform interface for sending requests and
    declaring pricing information.
    """

    @property
    @abstractmethod
    def model_id(self) -> ModelId:
        """Identifier of the underlying model (e.g. ``ModelId('gpt-4o')``).

        Returns
        -------
        ModelId
            The model identifier.
        """

    @property
    @abstractmethod
    def price_per_input_token(self) -> Cost:
        """Cost charged per input (prompt) token.

        Returns
        -------
        Cost
            Price per input token in the declared currency.
        """

    @property
    @abstractmethod
    def price_per_output_token(self) -> Cost:
        """Cost charged per output (completion) token.

        Returns
        -------
        Cost
            Price per output token in the declared currency.
        """

    @abstractmethod
    def complete(self, request: LLMRequest) -> LLMResponse:
        """Send a prompt to the model and return the response with metrics.

        Parameters
        ----------
        request : LLMRequest
            The prompt and generation parameters.

        Returns
        -------
        LLMResponse
            The generated text along with token counts and latency.
        """
