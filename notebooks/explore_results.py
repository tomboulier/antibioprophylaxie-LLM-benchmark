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
    results_dirs = [Path("research/results"), Path("outputs")]
    json_files = []
    for results_dir in results_dirs:
        if results_dir.exists():
            json_files.extend(sorted(results_dir.glob("*.json")))

    file_options = {str(path): str(path) for path in json_files}

    if not file_options:
        file_options = {"(no results found)": ""}

    selected_files = mo.ui.multiselect(
        options=file_options,
        label="Select result files to compare",
    )
    return file_options, json_files, results_dirs, selected_files


@app.cell
def _display_file_picker(mo, selected_files):
    mo.vstack(
        [
            mo.md("## LLM Benchmark — Results Explorer"),
            mo.md("Select one or more JSON result files to compare."),
            selected_files,
        ]
    )
    return


@app.cell
def _load_results(json, selected_files):
    loaded_runs = []
    for file_path in selected_files.value:
        if file_path:
            with open(file_path, encoding="utf-8") as file_handle:
                loaded_runs.append(json.load(file_handle))
    return (loaded_runs,)


@app.cell
def _summary_table(mo, loaded_runs):
    if not loaded_runs:
        mo.md("_No results loaded. Select files above._")
        return

    rows = []
    for run in loaded_runs:
        summary = run.get("summary", {})
        rows.append(
            {
                "run_id": run.get("run_id", "")[:8] + "…",
                "approach": run.get("approach_id", ""),
                "model": run.get("model_id", ""),
                "dataset": run.get("dataset_id", ""),
                "accuracy": f"{summary.get('accuracy', 0):.1%}",
                "correct": summary.get("correct", 0),
                "total": summary.get("total", 0),
                "cost ($)": f"{summary.get('total_cost') or 0:.4f}",
                "tokens": summary.get("total_tokens") or "—",
                "latency (s)": f"{summary.get('avg_latency_s') or 0:.2f}",
                "CO₂ (g)": f"{summary.get('carbon_g_co2e') or 0:.4f}",
            }
        )

    mo.vstack(
        [
            mo.md("## Comparative Summary"),
            mo.ui.table(rows),
        ]
    )
    return (rows,)


@app.cell
def _by_type_breakdown(mo, loaded_runs):
    if not loaded_runs:
        return

    breakdown_rows = []
    for run in loaded_runs:
        run_label = f"{run.get('approach_id', '')} / {run.get('model_id', '')}"
        by_type = run.get("summary", {}).get("by_type", {})
        for question_type, stats in by_type.items():
            breakdown_rows.append(
                {
                    "run": run_label,
                    "type": question_type,
                    "total": stats.get("total", 0),
                    "correct": stats.get("correct", 0),
                    "accuracy": f"{stats.get('accuracy', 0):.1%}",
                }
            )

    if breakdown_rows:
        mo.vstack(
            [
                mo.md("## Breakdown by Question Type"),
                mo.ui.table(breakdown_rows),
            ]
        )
    return (breakdown_rows,)


@app.cell
def _question_detail(mo, loaded_runs):
    if not loaded_runs:
        return

    run_options = {
        f"{run.get('approach_id')} / {run.get('model_id')} ({run.get('run_id', '')[:8]})": index
        for index, run in enumerate(loaded_runs)
    }

    selected_run_index = mo.ui.dropdown(
        options=run_options,
        label="Select run for question detail",
    )
    mo.vstack(
        [
            mo.md("## Per-Question Detail"),
            selected_run_index,
        ]
    )
    return (run_options, selected_run_index)


@app.cell
def _question_table(mo, loaded_runs, selected_run_index):
    if not loaded_runs or selected_run_index.value is None:
        return

    run = loaded_runs[selected_run_index.value]
    question_rows = []
    for result in run.get("results", []):
        question_rows.append(
            {
                "id": result.get("question_id", ""),
                "type": result.get("question_type", ""),
                "expected": result.get("expected_answer", "")[:60],
                "actual": (result.get("actual_answer") or result.get("error") or "")[:60],
                "correct": "✓" if result.get("is_correct") else "✗",
                "sourcing": "✓" if result.get("is_sourcing_present") else "✗",
            }
        )

    mo.ui.table(question_rows)
    return (question_rows,)


@app.cell
def _csv_export(mo, loaded_runs, Path):
    if not loaded_runs:
        return

    export_button = mo.ui.button(label="Export comparison CSV")

    mo.vstack(
        [
            mo.md("## Export"),
            export_button,
        ]
    )
    return (export_button,)


@app.cell
def _do_csv_export(mo, loaded_runs, export_button, Path):
    if not loaded_runs or not export_button.value:
        return

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

    # Reconstruct minimal RunResult objects for the CSV adapter
    run_results = []
    for run_data in loaded_runs:
        summary_data = run_data.get("summary", {})
        summary = RunSummary(
            total=summary_data.get("total", 0),
            correct=summary_data.get("correct", 0),
            accuracy=Accuracy(summary_data.get("accuracy", 0.0)),
            sourcing_rate=Accuracy(summary_data.get("sourcing_rate", 0.0)),
            sourcing_correct_rate=Accuracy(summary_data.get("sourcing_correct_rate", 0.0)),
            total_cost=None,
            total_tokens=summary_data.get("total_tokens"),
            avg_latency=None,
            carbon_footprint=None,
            by_type=summary_data.get("by_type", {}),
        )
        run_results.append(
            RunResult(
                run_id=RunId(run_data.get("run_id", "unknown")),
                timestamp=datetime.now(tz=timezone.utc),
                dataset_id=DatasetId(run_data.get("dataset_id", "unknown")),
                dataset_version=run_data.get("dataset_version", ""),
                approach_id=ApproachId(run_data.get("approach_id", "unknown")),
                model_id=ModelId(run_data.get("model_id", "unknown")),
                framework_version=run_data.get("framework_version", ""),
                config=run_data.get("config", {}),
                summary=summary,
                results=[],
            )
        )

    output_dir = Path("outputs")
    adapter = CsvExportAdapter()
    output_path = adapter.export(run_results, output_dir)
    mo.md(f"CSV exported to `{output_path}`")
    return
