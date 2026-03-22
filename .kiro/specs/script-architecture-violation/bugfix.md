# Bugfix Requirements Document

## Introduction

`scripts/run_benchmark.py` is a standalone script that completely bypasses the hexagonal
architecture defined in `src/llm_benchmark/`. It reimplements core logic that already exists
in the architecture — model registry, scoring, LLM calls, and result export — using direct
provider SDK imports (`anthropic`, `openai`, `mistralai`). This causes concrete runtime bugs
(e.g. `cannot import name 'Mistral' from 'mistralai'` due to SDK version drift) and makes
the script impossible to maintain in sync with the domain layer.

The fix replaces the script body with a thin CLI entry point that delegates entirely to
`BenchmarkEngine`, `LiteLLMAdapter` (via the model registry in `config/models.yaml`), and
`JsonExportAdapter` — never importing provider SDKs directly.

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN `scripts/run_benchmark.py` is executed with any `--model` argument THEN the system
    imports provider SDKs directly (`anthropic`, `openai`, `mistralai`) instead of going
    through `LiteLLMAdapter`, causing `ImportError` / `cannot import name 'Mistral' from
    'mistralai'` on SDK version mismatch.

1.2 WHEN a model is requested THEN the system resolves it from a hardcoded `MODELS` dict
    inside the script instead of reading `config/models.yaml` via the config loader, causing
    the script to be out of sync with the authoritative model registry.

1.3 WHEN a question is scored THEN the system executes inline `score_qcm` / `score_open`
    functions instead of delegating to `ScorerRegistry` from `domain/scorer.py`, duplicating
    scoring logic and diverging from domain behaviour over time.

1.4 WHEN results are persisted THEN the system writes a custom JSON structure directly to
    `research/results/` instead of using `JsonExportAdapter`, producing a schema that differs
    from the one the rest of the architecture expects.

1.5 WHEN the script is run THEN the system bypasses `BenchmarkEngine` entirely, meaning
    domain-level orchestration (metrics collection, latency tracking, cost computation,
    `RunResult` / `RunSummary` entities) is never exercised.

### Expected Behavior (Correct)

2.1 WHEN `scripts/run_benchmark.py` is executed with any `--model` argument THEN the system
    SHALL route all LLM calls through `LiteLLMAdapter`, which handles every provider via
    LiteLLM without importing provider SDKs directly.

2.2 WHEN a model is requested THEN the system SHALL resolve it by loading `config/models.yaml`
    through the existing config loader and instantiating a `LiteLLMAdapter` with the pricing
    declared there.

2.3 WHEN a question is scored THEN the system SHALL delegate scoring to `BenchmarkEngine`,
    which internally uses `ScorerRegistry`, so that scoring logic lives exclusively in the
    domain layer.

2.4 WHEN results are persisted THEN the system SHALL use `JsonExportAdapter` to write a
    `RunResult` to the output directory, producing a schema consistent with the rest of the
    architecture.

2.5 WHEN the script is run THEN the system SHALL act as a thin CLI entry point that only
    parses arguments, wires adapters, calls `BenchmarkEngine.run()`, and exports results —
    containing no business logic of its own.

### Unchanged Behavior (Regression Prevention)

3.1 WHEN `--list-models` is passed THEN the system SHALL CONTINUE TO print the list of
    available models and exit without running the benchmark.

3.2 WHEN `--model` / `-m` is passed one or more times THEN the system SHALL CONTINUE TO
    run the benchmark for each specified model and save one result file per model.

3.3 WHEN `--questions` / `-q` is passed with a comma-separated list of question IDs THEN
    the system SHALL CONTINUE TO filter the benchmark to only those questions.

3.4 WHEN multiple models are specified THEN the system SHALL CONTINUE TO print a
    comparative summary table after all runs complete.

3.5 WHEN an unknown model name is passed THEN the system SHALL CONTINUE TO exit with a
    clear error message before running any benchmark.

3.6 WHEN the benchmark dataset file is missing THEN the system SHALL CONTINUE TO exit with
    a clear error message pointing to the conversion script.

---

## Bug Condition (Pseudocode)

```pascal
FUNCTION isBugCondition(entryPoint)
  INPUT: entryPoint — the script file being executed
  OUTPUT: boolean

  RETURN entryPoint imports any of {anthropic, openai, mistralai}
      OR entryPoint defines any of {score_qcm, score_open, query_anthropic,
                                     query_openai, query_mistral, MODELS dict}
      OR entryPoint does NOT delegate to BenchmarkEngine
      OR entryPoint does NOT use LiteLLMAdapter
      OR entryPoint does NOT use JsonExportAdapter
END FUNCTION
```

```pascal
// Property: Fix Checking
FOR ALL entryPoint WHERE isBugCondition(entryPoint) DO
  result ← execute(entryPoint)
  ASSERT no direct provider SDK import exists in entryPoint
  ASSERT BenchmarkEngine.run() is called
  ASSERT LiteLLMAdapter is used for every LLM call
  ASSERT JsonExportAdapter is used for every result export
END FOR

// Property: Preservation Checking
FOR ALL entryPoint WHERE NOT isBugCondition(entryPoint) DO
  ASSERT F(entryPoint) = F'(entryPoint)   // CLI surface unchanged
END FOR
```
