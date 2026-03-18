# Implementation Plan: dotenv-api-keys

## Overview

Wire `python-dotenv` into the CLI entry point, ship a `.env.example` template, verify
`.gitignore` coverage, and update the README. TDD order: tests first, then implementation.

## Tasks

- [x] 1. Write unit tests for dotenv loading behaviour
  - Create `tests/unit/test_dotenv_loader.py`
  - Test: `.env` present → variables loaded into environment before any handler runs
  - Test: no `.env` file → no error, environment unchanged
  - Test: variable already set in environment → existing value preserved (no override)
  - Test: malformed `.env` file → descriptive error raised, non-zero exit
  - Use `unittest.mock.patch` / `tmp_path` fixtures; do not touch the real environment
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 2. Implement dotenv loading in the CLI entry point
  - [x] 2.1 Add `load_dotenv` call at the top of `main()` in `src/llm_benchmark/cli/main.py`
    - Call `dotenv.load_dotenv(override=False)` before argument parsing
    - On `dotenv.main.DotEnvException` (malformed file): print descriptive message to
      stderr and call `sys.exit(1)`
    - Import `python-dotenv` in the CLI module only — never in domain or ports layers
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

  - [x] 2.2 Write property test for non-override invariant
    - **Property 1: Pre-existing environment variables are never overwritten by `.env`**
    - **Validates: Requirements 1.3**
    - Generate arbitrary `KEY=value` pairs; set them in the environment; write a `.env`
      with different values; assert environment values are unchanged after `load_dotenv`

- [x] 3. Checkpoint — ensure all tests pass
  - Run `uv run pytest tests/unit/test_dotenv_loader.py` and confirm green
  - Ask the user if any questions arise before continuing.

- [x] 4. Create `.env.example` at the project root
  - Create `.env.example` with a comment block explaining purpose and copy instructions
  - Include entries for all providers in `config/models.yaml`:
    - `OPENAI_API_KEY=your-openai-api-key-here`
    - `ANTHROPIC_API_KEY=your-anthropic-api-key-here`
    - `MISTRAL_API_KEY=your-mistral-api-key-here`
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [x] 5. Verify `.gitignore` coverage
  - Confirm `.env` is listed in `.gitignore` (already present — add if somehow missing)
  - Confirm `.env.example` is NOT listed in `.gitignore`
  - No code change needed if both conditions already hold; document finding in commit message
  - _Requirements: 3.1, 3.2_

- [x] 6. Update README setup section
  - Replace the `export VAR=value` block in the Setup section with the `.env` workflow:
    1. `cp .env.example .env`
    2. Edit `.env` and fill in real API key values
  - Add a note that manually exported environment variables take precedence over `.env`
  - _Requirements: 4.1, 4.2, 4.3_

- [x] 7. Final checkpoint — ensure all tests pass
  - Run `uv run pytest` and confirm the full suite is green
  - Run `uv run ruff check --fix src/ tests/ && uv run ruff format src/ tests/`
  - Ask the user if any questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP
- TDD order is enforced: task 1 (tests) must be completed before task 2 (implementation)
- `python-dotenv` is already declared in `pyproject.toml` — no dependency changes needed
- `.gitignore` already contains `.env` and `.env.local` — task 5 is a verification step
- The domain layer must remain free of external dependencies; dotenv loading stays in `cli/`
