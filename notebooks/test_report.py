"""Marimo notebook — Test suite report for llm-benchmark.

Shows what was tested, what passed, and what the coverage looks like.
All tests use stubs/mocks — no real LLM calls were made.

Run with: marimo run notebooks/test_report.py
Edit with: marimo edit notebooks/test_report.py
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
def _load_report(Path, json):
    report_path = Path("docs/test_report.json")
    report = json.loads(report_path.read_text()) if report_path.exists() else {}
    tests = report.get("tests", [])
    coverage = report.get("coverage", {})
    return coverage, report, tests


@app.cell
def _header(mo, report):
    total = report.get("total", 0)
    passed = report.get("passed", 0)
    failed = report.get("failed", 0)

    status_color = "green" if failed == 0 else "red"
    status_label = "✅ All passing" if failed == 0 else f"❌ {failed} failing"

    mo.vstack(
        [
            mo.md("# llm-benchmark — Test Suite Report"),
            mo.md(
                "> **Note:** All tests use stubs and mocks. "
                "No real LLM API calls were made during testing. "
                "The benchmark engine, scorers, and adapters were validated "
                "against controlled inputs only."
            ),
            mo.hstack(
                [
                    mo.stat(label="Total tests", value=str(total)),
                    mo.stat(label="Passed", value=str(passed)),
                    mo.stat(label="Failed", value=str(failed)),
                    mo.stat(label="Status", value=status_label),
                ]
            ),
        ]
    )
    return failed, passed, status_color, status_label, total


@app.cell
def _by_module(mo, tests):
    from collections import defaultdict

    by_module = defaultdict(lambda: {"unit": 0, "property": 0, "passed": 0, "failed": 0})
    for test in tests:
        module = test["module"]
        kind = test["kind"]
        by_module[module][kind] += 1
        by_module[module][test["status"].lower()] += 1

    rows = [
        {
            "module": module,
            "unit tests": stats["unit"],
            "property tests": stats["property"],
            "passed": stats["passed"],
            "failed": stats["failed"],
        }
        for module, stats in sorted(by_module.items())
    ]

    mo.vstack(
        [
            mo.md("## Tests by module"),
            mo.ui.table(rows),
        ]
    )
    return by_module, rows


@app.cell
def _property_tests(mo, tests):
    property_tests = [t for t in tests if t["kind"] == "property"]

    descriptions = {
        "test_immutability": "Property 1 — All Value Objects are frozen (FrozenInstanceError on mutation)",
        "test_cost_valid": "Property 2a — Cost is valid iff amount ≥ 0 and currency ∈ {USD, EUR}",
        "test_cost_negative_invalid": "Property 2b — Negative Cost always raises ValueError",
        "test_cost_invalid_currency": "Property 2c — Unknown currency always raises ValueError",
        "test_accuracy_valid_range": "Property 3a — Accuracy is valid iff 0.0 ≤ value ≤ 1.0",
        "test_accuracy_out_of_range_invalid": "Property 3b — Out-of-range Accuracy always raises ValueError",
        "test_property_exhaustive_rejection": "Property 4 — Dataset loader rejects any JSON with a missing required field",
        "test_property_open_scorer_determinism": "Property 5a — OpenScorer is deterministic",
        "test_property_qcm_scorer_determinism": "Property 5b — QCMScorer is deterministic",
        "test_property_normalize_idempotency": "Property 6 — normalize(normalize(s)) == normalize(s) for all strings",
        "test_property_qcm_correctness": "Property 7 — QCMScorer returns correct=True iff extracted letter matches expected",
        "test_property_run_id_uniqueness": "Property 8 — Two successive engine.run() calls produce distinct RunIds",
        "test_property_summary_correct_lte_total": "Property 9a — summary.correct ≤ summary.total for any dataset",
        "test_property_summary_accuracy_equals_correct_over_total": "Property 9b — summary.accuracy == correct / total",
        "test_property_json_schema_stable": "Property 10 — JSON export always has exactly the 10 required top-level keys",
    }

    rows = []
    for test in property_tests:
        short_name = test["name"].split("::")[-1].split("[")[0]
        rows.append(
            {
                "property": descriptions.get(short_name, short_name),
                "status": "✅ pass" if test["status"] == "PASSED" else "❌ fail",
            }
        )

    mo.vstack(
        [
            mo.md("## Correctness properties verified"),
            mo.md(
                "These are the formal properties validated by [Hypothesis](https://hypothesis.readthedocs.io/). "
                "Each property was checked against hundreds of randomly generated inputs."
            ),
            mo.ui.table(rows),
        ]
    )
    return descriptions, property_tests, rows, short_name


@app.cell
def _coverage_table(mo, coverage):
    domain_rows = []
    adapter_rows = []
    other_rows = []

    for path, stats in sorted(coverage.items()):
        row = {
            "file": path.replace("src/llm_benchmark/", ""),
            "statements": stats["stmts"],
            "missed": stats["miss"],
            "coverage": f"{stats['cover']}%",
        }
        if "domain" in path:
            domain_rows.append(row)
        elif "adapters" in path or "ports" in path:
            adapter_rows.append(row)
        else:
            other_rows.append(row)

    domain_avg = sum(coverage[p]["cover"] for p in coverage if "domain" in p) // max(
        1, sum(1 for p in coverage if "domain" in p)
    )

    mo.vstack(
        [
            mo.md("## Coverage"),
            mo.md(
                f"Domain layer average: **{domain_avg}%** "
                f"(target: ≥ 80% — {'✅ met' if domain_avg >= 80 else '❌ not met'})"
            ),
            mo.md("### Domain layer"),
            mo.ui.table(domain_rows),
            mo.md("### Adapters & ports"),
            mo.ui.table(adapter_rows),
            mo.md("### Other"),
            mo.ui.table(other_rows),
        ]
    )
    return adapter_rows, domain_avg, domain_rows, other_rows, row


@app.cell
def _what_was_tested(mo):
    mo.vstack(
        [
            mo.md("## What was tested — and how"),
            mo.md("""
### Unit tests (stubs & mocks)

Every component was tested in isolation using `unittest.mock`:

| Component | What was verified |
|-----------|------------------|
| **Value Objects** | Invariants (negative values, empty strings, invalid keys), immutability |
| **Entities** | Construction, MCQ requires choices, field defaults |
| **Dataset loader** | Valid JSON loading, missing fields, unknown types |
| **Scorers** | Molecule matching, letter extraction, sourcing detection, registry dispatch |
| **MetricsCollector** | Cost calculation from token counts, carbon tracker delegation |
| **BenchmarkEngine** | approach×LLM combinations, error recovery, summary aggregation, filtering |
| **Export adapters** | JSON schema, CSV columns, file creation |
| **Config loader** | YAML parsing, missing field errors |
| **LiteLLMAdapter** | Mocked `litellm.completion`, token/latency extraction |
| **LongContextApproach** | File loading, prompt construction |
| **CLI** | Argument parsing, subcommand dispatch, exit codes |

### Property-based tests (Hypothesis)

10 formal correctness properties were verified against hundreds of random inputs.
The most interesting finding: `normalize()` was **not idempotent** on Unicode
whitespace characters like `\\x85` (NEL). Fixed by adding a final `.strip()` after `rstrip(".")`.

### No real LLM calls

All LLM interactions were replaced by `MagicMock` stubs returning controlled
`LLMResponse` objects. To run a real benchmark, use:

```bash
llm-benchmark run --dataset datasets/sfar_antibioprophylaxie/benchmark.json \\
  --approach long-context --model gpt-4o --output-dir outputs/
```
        """),
        ]
    )
    return
