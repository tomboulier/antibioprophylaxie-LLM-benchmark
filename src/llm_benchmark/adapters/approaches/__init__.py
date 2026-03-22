"""Approach adapters package — provides APPROACH_REGISTRY."""

from llm_benchmark.adapters.approaches.long_context import LongContextApproach
from llm_benchmark.adapters.approaches.simple_prompt import SimplePromptApproach
from llm_benchmark.ports.approach import ApproachPort

APPROACH_REGISTRY: dict[str, type[ApproachPort]] = {
    "long-context": LongContextApproach,
    "simple-prompt": SimplePromptApproach,
}
