# Script Architecture Violation Bugfix Design

## Overview

`scripts/run_benchmark.py` bypasses the hexagonal architecture entirely: it imports provider
SDKs directly (`anthropic`, `openai`, `mistralai`), duplicates scoring logic, maintains a
hardcoded model registry, and writes a custom JSON schema — all of which already exist in
`src/llm_benchmark/`. The concrete runtime symptom is `cannot import name 'Mistral' from
'mistralai'` on SDK version mismatch, but the structural problem is broader.

The fix rewrites the script as a thin CLI entry point (~100 lines) that:
1. Parses arguments (same CLI surface as today)
2. Resolves models via `LLM_REGISTRY` from `config/models.yaml`
3. Loads the dataset via `DatasetLoader`
4. Wires a `SimplePromptApproach` (new, minimal adapter — no document injection)
5. Calls `BenchmarkEngine.run()`
6. Exports each `RunResult` via `JsonExportAdapter`
7. Prints a comparative summary

As a companion, this fix also produces:
- `docs/architecture.md` — human-readable hexagonal architecture reference
- `.kiro/steering/architecture.md` — agent-readable enforcement rules (auto-included in every session)

---

## Glossary

- **Bug_Condition (C)**: The script file imports any of `{anthropic, openai, mistralai}`,
  OR defines any of `{score_qcm, score_open, query_anthropic, query_openai, query_mistral,
  MODELS dict}`, OR does not delegate to `BenchmarkEngine`.
- **Property (P)**: The fixed script contains none of the above and calls
  `BenchmarkEngine.run()` with `LiteLLMAdapter` instances and exports via `JsonExportAdapter`.
- **Preservation**: The CLI surface (`--model`, `--list-models`, `--questions`, comparative
  summary, error messages) remains identical from the user's perspective.
- **BenchmarkEngine**: `src/llm_benchmark/domain/engine.py` — domain orchestrator that runs
  all (approach × LLM) combinations and returns `list[RunResult]`.
- **LiteLLMAdapter**: `src/llm_benchmark/adapters/llms/litellm_adapter.py` — universal LLM
  adapter backed by LiteLLM; handles every provider without direct SDK imports.
- **LLM_REGISTRY**: `src/llm_benchmark/adapters/llms/__init__.py` — `dict[str, LiteLLMAdapter]`
  loaded from `config/models.yaml` at import time.
- **JsonExportAdapter**: `src/llm_benchmark/adapters/exports/json_export.py` — writes a
  `RunResult` to `{run_id}.json` in the output directory.
- **DatasetLoader**: `src/llm_benchmark/domain/dataset_loader.py` — loads and validates a
  dataset JSON file into a `Dataset` entity.
- **SimplePromptApproach**: New adapter to be created at
  `src/llm_benchmark/adapters/approaches/simple_prompt.py` — passes the question text
  directly to the LLM without injecting a source document.
- **ApproachPort**: `src/llm_benchmark/ports/approach.py` — abstract interface every approach
  adapter must implement.

---

## Bug Details

### Bug Condition

The bug manifests whenever `scripts/run_benchmark.py` is imported or executed. The script
contains direct provider SDK imports at the module level and inside functions, duplicated
business logic, and a hardcoded model registry — none of which delegate to the hexagonal
architecture.

**Formal Specification:**

```
FUNCTION isBugCondition(script_source)
  INPUT: script_source — the source text of scripts/run_benchmark.py
  OUTPUT: boolean

  RETURN script_source contains any import of {anthropic, openai, mistralai}
      OR script_source defines any of {score_qcm, score_open,
                                        query_anthropic, query_openai, query_mistral}
      OR script_source defines a module-level MODELS dict
      OR script_source does NOT import BenchmarkEngine
      OR script_source does NOT import LiteLLMAdapter or LLM_REGISTRY
      OR script_source does NOT import JsonExportAdapter
END FUNCTION
```

### Examples

- **Pressing `--model mistral-large`**: triggers `from mistralai import Mistral` →
  `ImportError: cannot import name 'Mistral' from 'mistralai'` (SDK version mismatch).
  Expected: routes through `LiteLLMAdapter` which uses LiteLLM's unified interface.
- **Scoring a QCM answer**: calls inline `score_qcm()` in the script →
  diverges from `ScorerRegistry` logic over time.
  Expected: `BenchmarkEngine` delegates to `ScorerRegistry` internally.
- **Saving results**: writes `research/results/<model>_<ts>.json` with a custom schema →
  incompatible with `JsonExportAdapter`'s schema.
  Expected: `JsonExportAdapter.export(run_result, output_dir)` writes `{run_id}.json`.
- **Adding a new model to `config/models.yaml`**: script stays unaware because it reads
  its own hardcoded `MODELS` dict.
  Expected: `LLM_REGISTRY` is the single source of truth.

---

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**

- `--list-models` prints available model IDs and exits 0 (requirement 3.1)
- `--model`/`-m` (repeatable) runs the benchmark for each specified model (requirement 3.2)
- `--questions`/`-q` with comma-separated IDs filters the run to those questions (requirement 3.3)
- Multiple `--model` flags produce a comparative summary table after all runs (requirement 3.4)
- An unknown model name exits with a clear error before running anything (requirement 3.5)
- A missing dataset file exits with a clear error pointing to the conversion script (requirement 3.6)

**Scope:**

All inputs that do NOT involve direct provider SDK calls are unaffected by this fix. The
argument-parsing surface, output directory convention (`research/results/`), and
human-readable progress printing are preserved.

---

## Hypothesized Root Cause

1. **Script written before the architecture existed**: `run_benchmark.py` predates
   `BenchmarkEngine`, `LiteLLMAdapter`, and `JsonExportAdapter`. It was never updated to
   delegate to them.

2. **No architectural guard**: nothing prevents a script from importing provider SDKs
   directly. The absence of a steering document or linting rule means the violation went
   undetected.

3. **SDK version drift**: `mistralai` changed its public API between the version pinned in
   `pyproject.toml` and the one the script was written against, surfacing the latent bug as
   a concrete `ImportError`.

4. **Missing `SimplePromptApproach`**: the existing `LongContextApproach` requires a source
   document path. The script's original behaviour (send the question directly, no document
   injection) has no corresponding adapter, so there was no obvious migration path.

---

## Correctness Properties

Property 1: Bug Condition — No Direct Provider SDK Imports

_For any_ version of `scripts/run_benchmark.py` where `isBugCondition` returns true (i.e.
the script imports provider SDKs directly or duplicates domain logic), the fixed script
SHALL contain none of `{import anthropic, import openai, from mistralai}`, SHALL NOT define
`score_qcm`, `score_open`, `query_anthropic`, `query_openai`, `query_mistral`, or a
module-level `MODELS` dict, and SHALL import and call `BenchmarkEngine`, `LLM_REGISTRY`,
and `JsonExportAdapter`.

**Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**

Property 2: Preservation — CLI Surface Unchanged

_For any_ invocation of the script where `isBugCondition` does NOT hold (i.e. the script is
already architecture-compliant), the fixed script SHALL produce the same observable CLI
behaviour as the original: same flags accepted, same exit codes, same result file location
convention, same comparative summary format.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6**

---

## Fix Implementation

### Part 1 — New adapter: `SimplePromptApproach`

**File**: `src/llm_benchmark/adapters/approaches/simple_prompt.py`

The current script sends questions directly to the LLM without injecting a source document.
`LongContextApproach` requires a source file path, so a new minimal adapter is needed.

**Behaviour**:
- `approach_id` → `ApproachId("simple-prompt")`
- `prepare()` → no-op
- `build_prompt(question)` → returns `question.question_text` for open questions;
  appends formatted choices for MCQ questions (matching the script's current `format_question` logic)

**Register** in `src/llm_benchmark/adapters/approaches/__init__.py`:
```python
APPROACH_REGISTRY["simple-prompt"] = SimplePromptApproach
```

### Part 2 — Rewrite `scripts/run_benchmark.py`

**File**: `scripts/run_benchmark.py`

**Specific Changes**:

1. **Remove all provider SDK imports**: delete `import anthropic`, `import openai`,
   `from mistralai import Mistral` and all functions that use them
   (`query_anthropic`, `query_openai`, `query_mistral`, `PROVIDERS` dict).

2. **Remove duplicated domain logic**: delete `score_qcm`, `score_open`, `normalize`,
   `format_question`, `run_model`, `_group_stats`, `save_results`, and the hardcoded
   `MODELS` dict.

3. **Model resolution via `LLM_REGISTRY`**: replace `MODELS` dict with a lookup into
   `LLM_REGISTRY` from `src/llm_benchmark/adapters/llms`. The `--list-models` flag
   iterates `sorted(LLM_REGISTRY.keys())`.

4. **Dataset loading via `DatasetLoader`**: replace the raw `json.loads(BENCHMARK_PATH...)`
   call with `load_dataset(DATASET_PATH)` from `src/llm_benchmark/domain/dataset_loader`.
   The default dataset path points to `datasets/sfar_antibioprophylaxie/benchmark.json`.

5. **Approach wiring**: instantiate `SimplePromptApproach()` (no arguments needed).

6. **Engine call**: `engine = BenchmarkEngine(); results = engine.run(dataset, [approach],
   llm_adapters, question_ids)` where `llm_adapters` is the list of `LiteLLMAdapter`
   instances resolved from `LLM_REGISTRY`.

7. **Export via `JsonExportAdapter`**: for each `RunResult`, call
   `JsonExportAdapter().export(result, output_dir)` and print the returned path.

8. **Comparative summary**: reimplement `print_comparison` using `RunResult.summary`
   fields (`summary.correct`, `summary.total`, `summary.accuracy.value`,
   `summary.by_type`) — same table format as today.

9. **Question ID filtering**: convert the comma-separated `--questions` string to
   `list[QuestionId]` and pass to `engine.run(... question_ids=...)`.

**Resulting structure of the fixed script** (pseudocode):

```
parse_args()
if --list-models: print sorted(LLM_REGISTRY.keys()); exit 0
validate models against LLM_REGISTRY
dataset = load_dataset(DATASET_PATH)
filter questions if --questions given
approach = SimplePromptApproach()
llm_adapters = [LLM_REGISTRY[name] for name in args.models]
engine = BenchmarkEngine()
results = engine.run(dataset, [approach], llm_adapters, question_ids)
for result in results:
    path = JsonExportAdapter().export(result, OUTPUT_DIR)
    print(f"Results saved: {path}")
print_comparison(results)   # only when len(results) > 1
```

### Part 3 — Architecture documentation

**File**: `docs/architecture.md`

Human-readable reference covering:
- Hexagonal architecture diagram (Mermaid)
- Layer descriptions and dependency rules
- Correct vs incorrect import patterns with code examples

**File**: `.kiro/steering/architecture.md`

Agent-readable enforcement rules, auto-included in every Kiro session. Contains:
- The dependency rule table (what each layer may import)
- Explicit forbidden patterns with examples
- Pointer to `docs/architecture.md` for full context

---

## Testing Strategy

### Validation Approach

Two-phase: first run static property tests against the **unfixed** script to confirm the
bug condition holds, then verify the fix satisfies both correctness properties.

### Exploratory Bug Condition Checking

**Goal**: Confirm `isBugCondition` returns true for the current script before touching any
code. Surface the exact imports and definitions that violate the architecture.

**Test Plan**: Parse `scripts/run_benchmark.py` with Python's `ast` module and assert the
presence of forbidden imports and function definitions. Run on the **unfixed** script to
observe failures that confirm the root cause.

**Test Cases**:

1. **Direct SDK import test**: assert `import anthropic` / `import openai` /
   `from mistralai import ...` are present in the AST (will PASS on unfixed code,
   confirming the bug).
2. **Duplicated scorer test**: assert `score_qcm` and `score_open` are defined in the
   script (will PASS on unfixed code, confirming duplication).
3. **Missing BenchmarkEngine test**: assert `BenchmarkEngine` is NOT imported in the script
   (will PASS on unfixed code, confirming bypass).
4. **Missing LLM_REGISTRY test**: assert `LLM_REGISTRY` is NOT imported (will PASS on
   unfixed code).

**Expected Counterexamples**:
- The unfixed script contains `import anthropic`, `import openai`, `from mistralai import Mistral`
- The unfixed script defines `score_qcm`, `score_open`, `query_anthropic`, `query_openai`, `query_mistral`
- The unfixed script does not import `BenchmarkEngine` or `LLM_REGISTRY`

### Fix Checking

**Goal**: Verify that after the fix, `isBugCondition` returns false for the script.

**Pseudocode:**
```
FOR ALL script_source WHERE isBugCondition(script_source) DO
  fixed_source := apply_fix(script_source)
  ASSERT NOT isBugCondition(fixed_source)
  ASSERT fixed_source imports BenchmarkEngine
  ASSERT fixed_source imports LLM_REGISTRY
  ASSERT fixed_source imports JsonExportAdapter
END FOR
```

### Preservation Checking

**Goal**: Verify that the CLI surface is unchanged — same flags, same exit codes, same
output directory convention.

**Pseudocode:**
```
FOR ALL invocation WHERE NOT isBugCondition(script_source) DO
  ASSERT parse_args(invocation) produces same Namespace as original
  ASSERT output path convention is research/results/<model_id>_<timestamp>.json
END FOR
```

**Testing Approach**: Property-based testing with Hypothesis is used for the static
structural checks (generate variations of import lists and verify the predicate). Unit
tests with mocked `BenchmarkEngine` cover the CLI surface preservation.

**Test Cases**:

1. **`--list-models` preservation**: mock `LLM_REGISTRY`, invoke with `--list-models`,
   assert prints model IDs and exits 0.
2. **Unknown model preservation**: invoke with `--model unknown-xyz`, assert exits with
   error before calling `BenchmarkEngine`.
3. **`--questions` filtering preservation**: mock `BenchmarkEngine.run`, invoke with
   `--questions Q01,Q03`, assert `question_ids` passed correctly.
4. **Comparative summary preservation**: mock two `RunResult` objects, assert
   `print_comparison` output contains both model IDs and accuracy values.

### Unit Tests

- `SimplePromptApproach.build_prompt` returns `question_text` for open questions
- `SimplePromptApproach.build_prompt` appends formatted choices for MCQ questions
- `SimplePromptApproach.prepare()` is a no-op (no exception raised)
- `SimplePromptApproach.approach_id` returns `ApproachId("simple-prompt")`
- Script `main()` calls `BenchmarkEngine.run()` with correct arguments (mocked engine)
- Script `main()` calls `JsonExportAdapter.export()` for each result (mocked adapter)

### Property-Based Tests

- **Property 1 (static)**: for the fixed `scripts/run_benchmark.py` source, assert
  `isBugCondition` returns false — no forbidden imports, no duplicated functions,
  `BenchmarkEngine` and `LLM_REGISTRY` are imported.
- **Property 2 (static)**: for the fixed script source, assert `BenchmarkEngine` is
  referenced in the AST (the script delegates to the engine).
- These are deterministic static checks expressed as Hypothesis tests for PBT traceability,
  even though the input space is a single fixed file.

### Integration Tests

- Full run with a mocked `LiteLLMAdapter` (returns a fixed `LLMResponse`) against the
  real `sfar_antibioprophylaxie` dataset — verifies end-to-end wiring without live API calls.
- `--list-models` integration: real `LLM_REGISTRY` loaded, output contains known model IDs
  from `config/models.yaml`.
