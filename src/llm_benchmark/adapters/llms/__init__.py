"""LLM adapters package — provides LLM_REGISTRY loaded from config/models.yaml."""

from __future__ import annotations

from pathlib import Path

import yaml

from llm_benchmark.adapters.llms.litellm_adapter import LiteLLMAdapter
from llm_benchmark.domain.value_objects import Cost

_MODELS_CONFIG_PATH = Path(__file__).parent.parent.parent.parent.parent / "config" / "models.yaml"


def _load_registry(
    config_path: Path,
    *,
    enabled_only: bool = False,
) -> dict[str, LiteLLMAdapter]:
    """Load the LLM registry from a YAML models config file.

    Parameters
    ----------
    config_path : Path
        Path to the models YAML file.
    enabled_only : bool
        When ``True``, only models with ``enabled: true`` are included.

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
        if enabled_only and not model_config.get("enabled", True):
            continue
        model_id = model_config["id"]
        # litellm_model is the string passed to litellm.completion(); it may
        # include a provider prefix (e.g. "mistral/mistral-small-latest").
        # Falls back to the user-facing id when not specified.
        litellm_model = model_config.get("litellm_model", model_id)
        currency = model_config.get("currency", "USD")
        registry[model_id] = LiteLLMAdapter(
            model=litellm_model,
            price_per_input_token=Cost(model_config["price_per_input_token"], currency),
            price_per_output_token=Cost(model_config["price_per_output_token"], currency),
            model_alias=model_id,
        )
    return registry


# Tous les modèles (pour --list-models, etc.)
LLM_REGISTRY: dict[str, LiteLLMAdapter] = _load_registry(_MODELS_CONFIG_PATH)

# Seulement les modèles activés (pour le pipeline automatisé)
ENABLED_REGISTRY: dict[str, LiteLLMAdapter] = _load_registry(
    _MODELS_CONFIG_PATH, enabled_only=True
)
