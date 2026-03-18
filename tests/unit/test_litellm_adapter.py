"""Unit tests for LiteLLMAdapter (all LLM calls are mocked)."""

from unittest.mock import MagicMock, patch

import pytest

from llm_benchmark.adapters.llms.litellm_adapter import LiteLLMAdapter
from llm_benchmark.domain.entities import LLMRequest, LLMResponse
from llm_benchmark.domain.value_objects import Cost, Latency, ModelId

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_adapter(
    model: str = "gpt-4o",
    price_in: float = 0.000001,
    price_out: float = 0.000002,
) -> LiteLLMAdapter:
    return LiteLLMAdapter(
        model=model,
        price_per_input_token=Cost(price_in),
        price_per_output_token=Cost(price_out),
    )


def _make_litellm_response(
    content: str = "answer",
    prompt_tokens: int = 100,
    completion_tokens: int = 50,
) -> MagicMock:
    """Build a mock that mimics the litellm completion response shape."""
    response = MagicMock()
    response.choices[0].message.content = content
    response.usage.prompt_tokens = prompt_tokens
    response.usage.completion_tokens = completion_tokens
    response.model_dump.return_value = {"mock": True}
    return response


# ---------------------------------------------------------------------------
# Properties
# ---------------------------------------------------------------------------


class TestLiteLLMAdapterProperties:
    def test_model_id_matches_constructor_argument(self) -> None:
        adapter = _make_adapter(model="claude-sonnet")
        assert adapter.model_id == ModelId("claude-sonnet")

    def test_price_per_input_token_matches_constructor_argument(self) -> None:
        adapter = _make_adapter(price_in=0.000005)
        assert adapter.price_per_input_token == Cost(0.000005)

    def test_price_per_output_token_matches_constructor_argument(self) -> None:
        adapter = _make_adapter(price_out=0.000015)
        assert adapter.price_per_output_token == Cost(0.000015)


# ---------------------------------------------------------------------------
# complete()
# ---------------------------------------------------------------------------


class TestLiteLLMAdapterComplete:
    def test_returns_llm_response(self) -> None:
        adapter = _make_adapter()
        request = LLMRequest(system_prompt="You are a doctor.", user_prompt="What antibiotic?")

        with patch("llm_benchmark.adapters.llms.litellm_adapter.litellm") as mock_litellm:
            mock_litellm.completion.return_value = _make_litellm_response()
            response = adapter.complete(request)

        assert isinstance(response, LLMResponse)

    def test_response_text_matches_litellm_content(self) -> None:
        adapter = _make_adapter()
        request = LLMRequest(system_prompt="sys", user_prompt="user")

        with patch("llm_benchmark.adapters.llms.litellm_adapter.litellm") as mock_litellm:
            mock_litellm.completion.return_value = _make_litellm_response(content="amoxicillin")
            response = adapter.complete(request)

        assert response.text == "amoxicillin"

    def test_response_input_tokens_matches_usage(self) -> None:
        adapter = _make_adapter()
        request = LLMRequest(system_prompt="sys", user_prompt="user")

        with patch("llm_benchmark.adapters.llms.litellm_adapter.litellm") as mock_litellm:
            mock_litellm.completion.return_value = _make_litellm_response(prompt_tokens=123)
            response = adapter.complete(request)

        assert response.input_tokens == 123

    def test_response_output_tokens_matches_usage(self) -> None:
        adapter = _make_adapter()
        request = LLMRequest(system_prompt="sys", user_prompt="user")

        with patch("llm_benchmark.adapters.llms.litellm_adapter.litellm") as mock_litellm:
            mock_litellm.completion.return_value = _make_litellm_response(completion_tokens=77)
            response = adapter.complete(request)

        assert response.output_tokens == 77

    def test_response_latency_is_positive(self) -> None:
        adapter = _make_adapter()
        request = LLMRequest(system_prompt="sys", user_prompt="user")

        with patch("llm_benchmark.adapters.llms.litellm_adapter.litellm") as mock_litellm:
            mock_litellm.completion.return_value = _make_litellm_response()
            response = adapter.complete(request)

        assert isinstance(response.latency, Latency)
        assert response.latency.seconds >= 0

    def test_complete_passes_correct_model_to_litellm(self) -> None:
        adapter = _make_adapter(model="mistral-large")
        request = LLMRequest(system_prompt="sys", user_prompt="user")

        with patch("llm_benchmark.adapters.llms.litellm_adapter.litellm") as mock_litellm:
            mock_litellm.completion.return_value = _make_litellm_response()
            adapter.complete(request)

        call_kwargs = mock_litellm.completion.call_args
        assert call_kwargs.kwargs["model"] == "mistral-large"

    def test_complete_passes_max_tokens_to_litellm(self) -> None:
        adapter = _make_adapter()
        request = LLMRequest(system_prompt="sys", user_prompt="user", max_tokens=512)

        with patch("llm_benchmark.adapters.llms.litellm_adapter.litellm") as mock_litellm:
            mock_litellm.completion.return_value = _make_litellm_response()
            adapter.complete(request)

        call_kwargs = mock_litellm.completion.call_args
        assert call_kwargs.kwargs["max_tokens"] == 512

    def test_litellm_exception_propagates(self) -> None:
        adapter = _make_adapter()
        request = LLMRequest(system_prompt="sys", user_prompt="user")

        with patch("llm_benchmark.adapters.llms.litellm_adapter.litellm") as mock_litellm:
            mock_litellm.completion.side_effect = RuntimeError("API error")

            with pytest.raises(RuntimeError, match="API error"):
                adapter.complete(request)
