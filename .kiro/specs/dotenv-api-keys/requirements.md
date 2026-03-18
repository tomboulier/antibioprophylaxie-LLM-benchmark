# Requirements Document

## Introduction

This feature adds support for loading API keys from a `.env` file using `python-dotenv`.
Currently, the tool expects API keys (OpenAI, Anthropic, Mistral, etc.) to be set as
environment variables before invocation. There is no automatic loading mechanism, which
creates friction for local development. The feature wires up `python-dotenv` (already
declared as a dependency in `pyproject.toml`) at the CLI entry point, ships a
`.env.example` template, ensures `.env` is gitignored, and updates documentation to
explain the setup.

The domain layer is not affected — it has zero external dependencies and must remain so.

## Glossary

- **CLI**: The `llm-benchmark` command-line entry point defined in `pyproject.toml`,
  implemented in `src/llm_benchmark/cli/main.py`.
- **DotenvLoader**: The infrastructure component responsible for loading variables from a
  `.env` file into the process environment using `python-dotenv`.
- **EnvFile**: A `.env` file at the project root containing `KEY=value` pairs for API
  keys and other secrets. Never committed to version control.
- **EnvExampleFile**: A `.env.example` file at the project root containing placeholder
  values that documents required environment variables. Committed to version control.
- **API key**: A secret string required by an LLM provider (OpenAI, Anthropic, Mistral,
  etc.) to authenticate API calls made through LiteLLM.
- **LiteLLMAdapter**: The adapter in `src/llm_benchmark/adapters/llms/litellm_adapter.py`
  that calls LLM providers via LiteLLM. It reads API keys from environment variables at
  call time.

---

## Requirements

### Requirement 1: Load `.env` file at CLI startup

**User Story:** As a developer, I want the CLI to automatically load a `.env` file at
startup, so that I do not have to manually export API keys in my shell before running
benchmarks.

#### Acceptance Criteria

1. WHEN the `llm-benchmark` CLI is invoked, THE DotenvLoader SHALL load environment
   variables from a `.env` file located in the current working directory before any
   LLM API call is made.
2. WHEN no `.env` file is present in the current working directory, THE DotenvLoader
   SHALL proceed without error and leave the environment unchanged.
3. WHEN a variable is already set in the process environment, THE DotenvLoader SHALL
   preserve the existing value and not override it with the value from the `.env` file.
4. WHEN the `.env` file is malformed (e.g. contains a syntax error), THE DotenvLoader
   SHALL raise a descriptive error and exit with a non-zero status code before executing
   any benchmark logic.

---

### Requirement 2: Provide a `.env.example` template

**User Story:** As a developer onboarding to the project, I want a `.env.example` file
that lists all required API keys with placeholder values, so that I know exactly which
variables to set without reading provider documentation.

#### Acceptance Criteria

1. THE EnvExampleFile SHALL exist at the project root and be committed to version control.
2. THE EnvExampleFile SHALL contain one entry per supported LLM provider API key, using
   a placeholder value that clearly indicates the expected format (e.g.
   `OPENAI_API_KEY=your-openai-api-key-here`).
3. THE EnvExampleFile SHALL include entries for all providers declared in
   `config/models.yaml`: OpenAI, Anthropic, and Mistral.
4. THE EnvExampleFile SHALL include a comment block at the top explaining its purpose
   and instructing the developer to copy it to `.env` and fill in real values.

---

### Requirement 3: Ensure `.env` is excluded from version control

**User Story:** As a developer, I want the `.env` file to be gitignored, so that API
keys are never accidentally committed to the repository.

#### Acceptance Criteria

1. THE EnvFile SHALL be listed in `.gitignore` so that it is never tracked by Git.
2. THE EnvExampleFile SHALL NOT be listed in `.gitignore` so that it remains tracked
   by Git.

---

### Requirement 4: Update documentation to explain the setup

**User Story:** As a developer, I want the README to explain how to configure API keys
using a `.env` file, so that I can set up the project quickly without prior knowledge
of the tool.

#### Acceptance Criteria

1. THE README SHALL include a setup section that instructs the developer to copy
   `.env.example` to `.env` and fill in real API key values.
2. THE README SHALL replace the current `export VAR=value` shell instructions with the
   `.env` file approach as the primary setup method.
3. THE README SHALL note that manually exported environment variables take precedence
   over values in the `.env` file (non-override behaviour from Requirement 1.3).
