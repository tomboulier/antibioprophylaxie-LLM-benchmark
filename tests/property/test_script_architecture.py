"""Property tests for architecture compliance.

Validate that the CLI and use case layers do NOT contain forbidden
patterns (direct provider SDK imports, duplicated domain functions)
and DO delegate to the domain layer (BenchmarkEngine, LLM_REGISTRY).
"""

from __future__ import annotations

import ast
from pathlib import Path

# ---------------------------------------------------------------------------
# Sources to validate
# ---------------------------------------------------------------------------

CLI_SOURCE: str = Path("src/llm_benchmark/cli/main.py").read_text(encoding="utf-8")
USECASE_SOURCE: str = Path("src/llm_benchmark/usecases/run_experiment.py").read_text(
    encoding="utf-8"
)

_FORBIDDEN_PROVIDER_MODULES: frozenset[str] = frozenset({"anthropic", "openai", "mistralai"})

_FORBIDDEN_FUNCTION_NAMES: frozenset[str] = frozenset(
    {"score_qcm", "score_open", "query_anthropic", "query_openai", "query_mistral"}
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _find_forbidden_imports(source: str) -> list[str]:
    found = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in _FORBIDDEN_PROVIDER_MODULES:
                    found.append(f"import {alias.name}")
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module.split(".")[0] in _FORBIDDEN_PROVIDER_MODULES:
                names = ", ".join(a.name for a in node.names)
                found.append(f"from {module} import {names}")
    return found


def _find_forbidden_functions(source: str) -> list[str]:
    return [
        node.name
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.FunctionDef) and node.name in _FORBIDDEN_FUNCTION_NAMES
    ]


def _imports_name(source: str, name: str) -> bool:
    return any(
        isinstance(node, ast.ImportFrom) and any(a.name == name for a in node.names)
        for node in ast.walk(ast.parse(source))
    )


# ---------------------------------------------------------------------------
# Tests — CLI
# ---------------------------------------------------------------------------


def test_cli_has_no_direct_provider_imports() -> None:
    """La CLI ne doit pas importer directement les SDKs provider."""
    found = _find_forbidden_imports(CLI_SOURCE)
    assert not found, f"CLI contient des imports provider interdits : {found}"


def test_cli_does_not_define_domain_functions() -> None:
    """La CLI ne doit pas dupliquer de fonctions du domaine."""
    found = _find_forbidden_functions(CLI_SOURCE)
    assert not found, f"CLI définit des fonctions domaine dupliquées : {found}"


# ---------------------------------------------------------------------------
# Tests — Use case
# ---------------------------------------------------------------------------


def test_usecase_has_no_direct_provider_imports() -> None:
    """Le use case ne doit pas importer directement les SDKs provider."""
    found = _find_forbidden_imports(USECASE_SOURCE)
    assert not found, f"Use case contient des imports provider interdits : {found}"


def test_usecase_does_not_define_domain_functions() -> None:
    """Le use case ne doit pas dupliquer de fonctions du domaine."""
    found = _find_forbidden_functions(USECASE_SOURCE)
    assert not found, f"Use case définit des fonctions domaine dupliquées : {found}"


def test_usecase_imports_benchmark_engine() -> None:
    """Le use case doit déléguer à BenchmarkEngine."""
    assert _imports_name(USECASE_SOURCE, "BenchmarkEngine"), (
        "Le use case n'importe pas BenchmarkEngine."
    )


def test_usecase_imports_llm_registry() -> None:
    """Le use case doit utiliser le registry de modèles."""
    has_enabled = _imports_name(USECASE_SOURCE, "ENABLED_REGISTRY")
    has_full = _imports_name(USECASE_SOURCE, "LLM_REGISTRY")
    assert has_enabled or has_full, "Le use case n'importe aucun registry de modèles."
