# Hexagonal Architecture Enforcement

This file is auto-included in every Kiro agent session. Follow these rules without exception.

Full reference: `docs/architecture.md`

---

## Dependency Rules (strict)

| Layer | May import | Must NEVER import |
|---|---|---|
| `domain/` | stdlib only | any third-party lib, `ports/`, `adapters/`, `cli/`, `scripts/` |
| `ports/` | `domain/` | `adapters/`, `cli/`, `scripts/` |
| `adapters/` | `ports/`, `domain/`, third-party libs | `cli/`, `scripts/` |
| `cli/` | `adapters/`, `ports/`, `domain/` | `scripts/` |
| `scripts/` | `adapters/`, `ports/`, `domain/` | provider SDKs directly |

---

## Forbidden Patterns — Never Do These

### Direct provider SDK imports in scripts or CLI

```python
# FORBIDDEN in scripts/ or cli/
import anthropic
import openai
from mistralai import Mistral
```

Use `LiteLLMAdapter` via `LLM_REGISTRY` instead:

```python
from llm_benchmark.adapters.llms import LLM_REGISTRY
adapter = LLM_REGISTRY["gpt-4o"]
```

### Inline scoring logic outside the domain

```python
# FORBIDDEN anywhere outside domain/scorer.py
def score_qcm(expected, actual): ...
def score_open(expected, actual): ...
```

Delegate to `BenchmarkEngine`, which uses `ScorerRegistry` internally.

### Hardcoded model registries

```python
# FORBIDDEN — duplicates config/models.yaml
MODELS = {"gpt-4o": ("openai", "gpt-4o"), ...}
```

Use `LLM_REGISTRY` from `src/llm_benchmark/adapters/llms/__init__.py`.

### Custom JSON result schemas

```python
# FORBIDDEN — diverges from RunResult schema
path.write_text(json.dumps({"model_name": ..., "results": [...]}))
```

Use `JsonExportAdapter().export(run_result, output_dir)`.

### Raw dataset parsing outside DatasetLoader

```python
# FORBIDDEN — bypasses validation
data = json.loads(Path("research/benchmark.json").read_text())
questions = data["questions"]
```

Use `load_dataset(path)` from `src/llm_benchmark/domain/dataset_loader`.

---

## Scripts Must Be Thin Entry Points

A script in `scripts/` is allowed to do exactly five things:

1. Parse CLI arguments
2. Resolve adapters from registries (`LLM_REGISTRY`, `APPROACH_REGISTRY`)
3. Call `BenchmarkEngine.run()`
4. Export results via `JsonExportAdapter`
5. Print human-readable progress/summary

If you find yourself writing business logic in a script, move it to the domain layer.
