# Contributing Guide

## Code Style

This project follows [Clean Code](https://www.oreilly.com/library/view/clean-code-a/9780136083238/) principles (Robert C. Martin), [KISS](https://en.wikipedia.org/wiki/KISS_principle), and [YAGNI](https://en.wikipedia.org/wiki/You_aren%27t_gonna_need_it).

### Language

All code, comments, docstrings, variable names, and commit messages are written in **English**.
User-facing CLI output and documentation may be in French (target audience).

### Naming

- Use **intention-revealing names**: `load_dataset` not `ld`, `question_id` not `qid`.
- Avoid abbreviations unless universally understood (`llm`, `csv`, `url`).
- Functions and variables: `snake_case`. Classes: `PascalCase`. Constants: `UPPER_SNAKE_CASE`.
- Boolean variables and functions: prefix with `is_`, `has_`, `can_` (`is_valid`, `has_source`).

### Functions

- One function = one responsibility (Single Responsibility Principle).
- Keep functions short. If it needs a comment to explain *what* it does, rename it.
- Prefer pure functions (no side effects) in the domain layer.
- Maximum one level of abstraction per function.

### KISS / YAGNI

- Write only the code needed to satisfy the current requirement.
- No speculative abstractions. No "we might need this later".
- Prefer the simplest solution that passes the tests.

### Docstrings

All public functions, classes, and methods must have a docstring in **NumPy format**:

```python
def score(self, question: Question, actual: str) -> ScoreResult:
    """Evaluate a model response against the expected answer.

    Parameters
    ----------
    question : Question
        The question containing the expected answer and type.
    actual : str
        The raw response text from the LLM.

    Returns
    -------
    ScoreResult
        Binary correctness result with optional sourcing evaluation.
    """
```

Private helpers (`_prefixed`) may use a single-line docstring.

## Tooling

All dev tooling is managed via `pyproject.toml`. Never install tools globally or outside the project venv.

```bash
# Install all dev dependencies
uv sync --extra dev

# Lint
uv run ruff check src/ tests/

# Fix auto-fixable lint issues
uv run ruff check --fix src/ tests/

# Format
uv run ruff format src/ tests/

# Run tests with coverage
uv run pytest tests/unit tests/property -v --cov=src/llm_benchmark --cov-report=term-missing
```

Ruff and pytest are configured in `pyproject.toml` under `[tool.ruff]` and `[tool.pytest.ini_options]`.
Do not use standalone config files (`.flake8`, `setup.cfg`, `pytest.ini`, etc.) — `pyproject.toml` is the single source of truth.

## Testing

- **TDD**: write tests before implementation.
- Unit tests in `tests/unit/`, property-based tests in `tests/property/`.
- Uses [Hypothesis](https://hypothesis.readthedocs.io/) for property-based testing.
- Coverage target: ≥ 80% on `src/llm_benchmark/domain/`.

## Git Commits

**Commit early, commit often.** Each commit should represent one coherent, self-contained change.
Do not batch unrelated changes into a single commit.

Use [Conventional Commits](https://www.conventionalcommits.org/) format for every commit message:

```
<type>: <short imperative description>
```

Types:

| Type       | When to use                                      |
|------------|--------------------------------------------------|
| `feat`     | New feature or behaviour                         |
| `fix`      | Bug fix                                          |
| `test`     | Adding or updating tests                         |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `chore`    | Dependency updates, config, tooling              |
| `docs`     | Documentation only                               |
| `ci`       | CI/CD pipeline changes                           |

Examples:

```
feat: add QCM scorer with A-D letter extraction
fix: reject negative cost values in Cost value object
test: add property tests for Accuracy invariants
refactor: extract normalize() to shared text utils
chore: add hypothesis and ruff to dev dependencies in pyproject.toml
docs: document ApproachPort contract in numpydoc format
```

**Good commit granularity examples:**
- One commit per new Value Object + its tests
- One commit for a new port interface
- One commit for a new adapter + its unit tests
- One commit for a pyproject.toml dependency update

**Never** commit broken code. Run `uv run ruff check` and `uv run pytest` before committing.

## Architecture

See `design.md` in the spec for the hexagonal architecture overview.
The domain layer (`src/llm_benchmark/domain/`) must have **zero external dependencies**.
