# Script Architecture Violation — Task List

## Tasks

- [x] 1. Write exploratory property tests (unfixed code — expected to fail after fix)
  - [x] 1.1 Create `tests/property/test_script_architecture.py` with `isBugCondition` helper that parses `scripts/run_benchmark.py` via `ast` and checks for forbidden imports and definitions
  - [x] 1.2 Write `test_script_has_no_direct_provider_imports` — asserts no `import anthropic`, `import openai`, `from mistralai` in the AST (fails on unfixed code, passes after fix)
  - [x] 1.3 Write `test_script_does_not_define_duplicated_domain_functions` — asserts `score_qcm`, `score_open`, `query_anthropic`, `query_openai`, `query_mistral` are not defined (fails on unfixed code, passes after fix)
  - [x] 1.4 Write `test_script_imports_benchmark_engine` — asserts `BenchmarkEngine` is imported (fails on unfixed code, passes after fix)
  - [x] 1.5 Write `test_script_imports_llm_registry` — asserts `LLM_REGISTRY` is imported (fails on unfixed code, passes after fix)

- [x] 2. Create `SimplePromptApproach` adapter
  - [x] 2.1 Create `src/llm_benchmark/adapters/approaches/simple_prompt.py` implementing `ApproachPort`: `approach_id` returns `ApproachId("simple-prompt")`, `prepare()` is a no-op, `build_prompt` returns `question.question_text` for open questions and appends formatted choices for MCQ
  - [x] 2.2 Register `SimplePromptApproach` in `src/llm_benchmark/adapters/approaches/__init__.py`
  - [x] 2.3 Write unit tests in `tests/unit/adapters/approaches/test_simple_prompt.py` covering `approach_id`, `prepare`, `build_prompt` for open and MCQ question types

- [x] 3. Rewrite `scripts/run_benchmark.py` as a thin CLI entry point
  - [x] 3.1 Remove all direct provider SDK imports and functions (`query_anthropic`, `query_openai`, `query_mistral`, `PROVIDERS`, `MODELS` dict, `score_qcm`, `score_open`, `normalize`, `format_question`, `run_model`, `_group_stats`, `save_results`)
  - [x] 3.2 Implement `--list-models` using `sorted(LLM_REGISTRY.keys())`
  - [x] 3.3 Implement model validation against `LLM_REGISTRY` with clear error on unknown model
  - [x] 3.4 Implement dataset loading via `load_dataset(DATASET_PATH)` with clear error when file is missing
  - [x] 3.5 Implement `--questions` filtering by converting comma-separated IDs to `list[QuestionId]`
  - [x] 3.6 Wire `SimplePromptApproach`, `LLM_REGISTRY` adapters, `BenchmarkEngine`, and `JsonExportAdapter` — call `engine.run()` and export each `RunResult` to `research/results/`
  - [x] 3.7 Implement `print_comparison` using `RunResult.summary` fields (same table format as original)

- [x] 4. Write unit tests for the rewritten script
  - [x] 4.1 Create `tests/unit/scripts/test_run_benchmark.py` with mocked `BenchmarkEngine` and `JsonExportAdapter`
  - [x] 4.2 Test `--list-models` prints model IDs from a mocked `LLM_REGISTRY` and exits 0
  - [x] 4.3 Test unknown model name exits with error before calling `BenchmarkEngine`
  - [x] 4.4 Test missing dataset file exits with error
  - [x] 4.5 Test `--questions Q01,Q03` passes correct `question_ids` to `engine.run()`
  - [x] 4.6 Test multiple models produce a comparative summary (mock two `RunResult` objects)

- [x] 5. Verify property tests pass on the fixed script
  - [x] 5.1 Run `tests/property/test_script_architecture.py` — all four property tests must pass
  - [x] 5.2 Run full test suite `uv run pytest tests/unit tests/property -v --cov=src/llm_benchmark --cov-report=term-missing` and confirm no regressions

- [x] 6. Write architecture documentation
  - [x] 6.1 Confirm `docs/architecture.md` exists with Mermaid diagram, layer descriptions, dependency rules, and correct vs incorrect code examples
  - [x] 6.2 Confirm `.kiro/steering/architecture.md` exists with dependency rule table, forbidden patterns, and the five-things rule for scripts
