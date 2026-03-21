"""Marimo notebook for exploring llm-benchmark results.

Run with: marimo run notebooks/explore_results.py
Edit with: marimo edit notebooks/explore_results.py
"""

import marimo

__generated_with = "0.9.0"
app = marimo.App(width="wide")


@app.cell
def _imports():
    import json
    from pathlib import Path

    import marimo as mo

    return Path, json, mo


@app.cell
def _file_picker(mo, Path):
    _results_dirs = [Path("research/results"), Path("outputs")]
    _json_files = []
    for _d in _results_dirs:
        if _d.exists():
            _json_files.extend(sorted(_d.glob("*.json")))

    _file_options = {str(p): str(p) for p in _json_files}
    if not _file_options:
        _file_options = {"(no results found)": ""}

    selected_files = mo.ui.multiselect(
        options=_file_options,
        label="Select result files to compare",
    )
    return (selected_files,)


@app.cell
def _display_file_picker(mo, selected_files):
    mo.vstack([
        mo.md("## LLM Benchmark — Results Explorer"),
        mo.md("Select one or more JSON result files to compare."),
        selected_files,
    ])
    return


@app.cell
def _load_results(json, selected_files):
    loaded_runs = []
    for _path in selected_files.value:
        if _path:
            with open(_path, encoding="utf-8") as _fh:
                loaded_runs.append(json.load(_fh))
    return (loaded_runs,)


@app.cell
def _summary_table(mo, loaded_runs):
    mo.stop(not loaded_runs, mo.md("_No results loaded. Select files above._"))

    _rows = []
    for _run in loaded_runs:
        _s = _run.get("summary", {})
        _rows.append({
            "run_id": _run.get("run_id", "")[:8] + "…",
            "approach": _run.get("approach_id", ""),
            "model": _run.get("model_id", ""),
            "dataset": _run.get("dataset_id", ""),
            "accuracy": f"{_s.get('accuracy', 0):.1%}",
            "correct": _s.get("correct", 0),
            "total": _s.get("total", 0),
            "cost ($)": f"{_s.get('total_cost') or 0:.4f}",
            "tokens": _s.get("total_tokens") or "—",
            "latency (s)": f"{_s.get('avg_latency_s') or 0:.2f}",
            "CO₂ (g)": f"{_s.get('carbon_g_co2e') or 0:.4f}",
        })

    mo.vstack([
        mo.md("## Comparative Summary"),
        mo.ui.table(_rows),
    ])
    return


@app.cell
def _by_type_breakdown(mo, loaded_runs):
    mo.stop(not loaded_runs)

    _breakdown_rows = []
    for _run in loaded_runs:
        _label = f"{_run.get('approach_id', '')} / {_run.get('model_id', '')}"
        for _qtype, _stats in _run.get("summary", {}).get("by_type", {}).items():
            _breakdown_rows.append({
                "run": _label,
                "type": _qtype,
                "total": _stats.get("total", 0),
                "correct": _stats.get("correct", 0),
                "accuracy": f"{_stats.get('accuracy', 0):.1%}",
            })

    mo.stop(not _breakdown_rows)
    mo.vstack([
        mo.md("## Breakdown by Question Type"),
        mo.ui.table(_breakdown_rows),
    ])
    return


@app.cell
def _question_detail(mo, loaded_runs):
    mo.stop(not loaded_runs)

    _run_options = {
        f"{_r.get('approach_id')} / {_r.get('model_id')} ({_r.get('run_id', '')[:8]})": _i
        for _i, _r in enumerate(loaded_runs)
    }
    selected_run_index = mo.ui.dropdown(
        options=_run_options,
        label="Select run for question detail",
    )
    mo.vstack([
        mo.md("## Per-Question Detail"),
        selected_run_index,
    ])
    return (selected_run_index,)


@app.cell
def _question_table(mo, loaded_runs, selected_run_index):
    mo.stop(not loaded_runs or selected_run_index.value is None)

    _run = loaded_runs[selected_run_index.value]
    _rows = []
    for _result in _run.get("results", []):
        _rows.append({
            "id": _result.get("question_id", ""),
            "type": _result.get("question_type", ""),
            "expected": _result.get("expected_answer", "")[:60],
            "actual": (_result.get("actual_answer") or _result.get("error") or "")[:60],
            "correct": "✓" if _result.get("is_correct") else "✗",
            "sourcing": "✓" if _result.get("is_sourcing_present") else "✗",
        })

    mo.ui.table(_rows)
    return


@app.cell
def _csv_export(mo, loaded_runs, Path):
    mo.stop(not loaded_runs)

    export_button = mo.ui.button(label="Export comparison CSV")
    mo.vstack([
        mo.md("## Export"),
        export_button,
    ])
    return (export_button,)


@app.cell
def _do_csv_export(mo, loaded_runs, export_button, Path):
    mo.stop(not loaded_runs or not export_button.value)

    from datetime import datetime, timezone

    from llm_benchmark.adapters.exports.csv_export import CsvExportAdapter
    from llm_benchmark.domain.entities import RunResult, RunSummary
    from llm_benchmark.domain.value_objects import (
        Accuracy,
        ApproachId,
        DatasetId,
        ModelId,
        RunId,
    )

    _run_results = []
    for _run_data in loaded_runs:
        _sd = _run_data.get("summary", {})
        _run_results.append(RunResult(
            run_id=RunId(_run_data.get("run_id", "unknown")),
            timestamp=datetime.now(tz=timezone.utc),
            dataset_id=DatasetId(_run_data.get("dataset_id", "unknown")),
            dataset_version=_run_data.get("dataset_version", ""),
            approach_id=ApproachId(_run_data.get("approach_id", "unknown")),
            model_id=ModelId(_run_data.get("model_id", "unknown")),
            framework_version=_run_data.get("framework_version", ""),
            config=_run_data.get("config", {}),
            summary=RunSummary(
                total=_sd.get("total", 0),
                correct=_sd.get("correct", 0),
                accuracy=Accuracy(_sd.get("accuracy", 0.0)),
                sourcing_rate=Accuracy(_sd.get("sourcing_rate", 0.0)),
                sourcing_correct_rate=Accuracy(_sd.get("sourcing_correct_rate", 0.0)),
                total_cost=None,
                total_tokens=_sd.get("total_tokens"),
                avg_latency=None,
                carbon_footprint=None,
                by_type=_sd.get("by_type", {}),
            ),
            results=[],
        ))

    _output_path = CsvExportAdapter().export(_run_results, Path("outputs"))
    mo.md(f"CSV exported to `{_output_path}`")
    return
