---
inclusion: always
---

# Coding Standards

Always refer to `CONTRIBUTING.md` at the root of the repository before writing any code.

Key rules to apply at all times:

- All code, variable names, comments, and docstrings are written in **English**
- Use intention-revealing names — no abbreviations, no single-letter variables
- One function = one responsibility; keep functions short and pure where possible
- KISS / YAGNI: write only what the current requirement needs, no speculative code
- Docstrings on all public symbols in **NumPy format**
- All tooling (ruff, pytest, coverage) is configured in `pyproject.toml` — never use standalone config files
- Run `uv run ruff check --fix src/ tests/ && uv run ruff format src/ tests/` before considering any task done
- TDD: tests before implementation
- Conventional Commits for every git commit (feat, fix, test, refactor, chore, docs, ci)
- Commit early and often — one logical change per commit, never batch unrelated changes
- The domain layer (`src/llm_benchmark/domain/`) must have zero external dependencies
