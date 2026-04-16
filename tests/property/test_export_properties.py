"""Property-based tests for export adapters."""

import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st

from llm_benchmark.adapters.exports.json_export import JsonExportAdapter
from llm_benchmark.domain.entities import RunResult, RunSummary
from llm_benchmark.domain.value_objects import (
    Accuracy,
    ApproachId,
    DatasetId,
    ModelId,
    RunId,
)

_TOP_LEVEL_KEYS = {
    "run_id",
    "timestamp",
    "dataset_id",
    "dataset_version",
    "approach_id",
    "model_id",
    "framework_version",
    "config",
    "summary",
    "results",
}

_nonempty_text = st.text(
    alphabet=st.characters(blacklist_categories=("Cs",), blacklist_characters="\x00"),
    min_size=1,
    max_size=30,
).filter(str.strip)


def _make_summary() -> RunSummary:
    return RunSummary(
        total=1,
        answered=1,
        correct=1,
        accuracy=Accuracy(1.0),
        sourcing_rate=Accuracy(0.0),
        sourcing_correct_rate=Accuracy(0.0),
        total_cost=None,
        total_tokens=None,
        avg_latency=None,
        carbon_footprint=None,
        by_type={},
    )


@given(
    run_id=_nonempty_text,
    approach_id=_nonempty_text,
    model_id=_nonempty_text,
    dataset_id=_nonempty_text,
)
@settings(max_examples=30)
def test_property_json_schema_stable(
    run_id: str,
    approach_id: str,
    model_id: str,
    dataset_id: str,
) -> None:
    """For any valid RunResult, the exported JSON has exactly the required top-level keys.

    Validates: Requirements 7.4
    """
    run_result = RunResult(
        run_id=RunId(run_id),
        timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
        dataset_id=DatasetId(dataset_id),
        dataset_version="1.0",
        approach_id=ApproachId(approach_id),
        model_id=ModelId(model_id),
        framework_version="0.1.0",
        config={},
        summary=_make_summary(),
        results=[],
    )

    adapter = JsonExportAdapter()
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_path = adapter.export(run_result, Path(tmp_dir))
        content = json.loads(output_path.read_text())

    assert set(content.keys()) == _TOP_LEVEL_KEYS
