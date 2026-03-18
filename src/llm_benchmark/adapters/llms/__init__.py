"""LLM adapters package — provides LLM_REGISTRY loaded from config/models.yaml."""

from __future__ import annotations

from pathlib import Path

import yaml

from llm_benchmark.adapters.llms.litellm_adapter import LiteLLMAdapter
from llm_benchmark.domain.value_objects import Cost

_MODELS_CONFIG_PATH = Path(__file__).parent.parent.parent.parent.parent / "config" / "models.yaml"


def _load_registry(config_path: Path) -> dict[str, LiteLLMAdapter]:
    """Load the LLM registry from a YAML models config file.

    Parameters
    ----------
    config_path : Path
        Path to the models YAML file.

    Returns
    -------
    dict[str, LiteLLMAdapter]
        Mapping from model ID string to a configured ``LiteLLMAdapter``.
    """
    if not config_path.exists():
        return {}

    with config_path.open(encoding="utf-8") as file_handle:
        raw = yaml.safe_load(file_handle) or {}

    registry: dict[str, LiteLLMAdapter] = {}
    for model_config in raw.get("models", []):
        model_id = model_config["id"]
        currency = model_config.get("currency", "USD")
        registry[model_id] = LiteLLMAdapter(
            model=model_id,
            price_per_input_token=Cost(model_config["price_per_input_token"], currency),
            price_per_output_token=Cost(model_config["price_per_output_token"], currency),
        )
    return registry


LLM_REGISTRY: dict[str, LiteLLMAdapter] = _load_registry(_MODELS_CONFIG_PATH)
