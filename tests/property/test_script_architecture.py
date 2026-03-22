"""Property tests for script architecture compliance.

These tests parse ``scripts/run_benchmark.py`` with Python's ``ast`` module and
assert that the script does NOT contain forbidden patterns (direct provider SDK
imports, duplicated domain functions) and DOES delegate to ``BenchmarkEngine``
and ``LLM_REGISTRY``.

On the **unfixed** script all four tests are expected to FAIL — failure confirms
the bug condition exists.  After the fix all four tests must PASS.

**Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**
"""

from __future__ import annotations

import ast
from pathlib import Path

# ---------------------------------------------------------------------------
# Module-level constant — read once at import time
# ---------------------------------------------------------------------------

SCRIPT_SOURCE: str = Path("scripts/run_benchmark.py").read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

_FORBIDDEN_PROVIDER_MODULES: frozenset[str] = frozenset({"anthropic", "openai", "mistralai"})

_FORBIDDEN_FUNCTION_NAMES: frozenset[str] = frozenset(
    {"score_qcm", "score_open", "query_anthropic", "query_openai", "query_mistral"}
)


def is_bug_condition(script_source: str) -> bool:
    """Return ``True`` when *script_source* exhibits the architecture violation.

    Walks the AST of *script_source* and returns ``True`` if any of the
    following forbidden patterns are found:

    * An ``import`` statement whose module name is in
      ``{anthropic, openai, mistralai}``.
    * A ``from … import`` statement whose module name is in
      ``{anthropic, openai, mistralai}``.
    * A ``def`` statement whose name is in
      ``{score_qcm, score_open, query_anthropic, query_openai, query_mistral}``.
    * No ``from … import`` statement that names ``BenchmarkEngine``.
    * No ``from … import`` statement that names ``LLM_REGISTRY``.

    Parameters
    ----------
    script_source : str
        Full source text of the script to analyse.

    Returns
    -------
    bool
        ``True`` if the script violates the architecture, ``False`` otherwise.
    """
    tree = ast.parse(script_source)

    has_forbidden_import = False
    has_forbidden_function = False
    imports_benchmark_engine = False
    imports_llm_registry = False

    for node in ast.walk(tree):
        # Direct imports: import anthropic / import openai
        if isinstance(node, ast.Import):
            for alias in node.names:
                root_module = alias.name.split(".")[0]
                if root_module in _FORBIDDEN_PROVIDER_MODULES:
                    has_forbidden_import = True

        # From-imports: from mistralai import Mistral / from anthropic import …
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            root_module = module.split(".")[0]
            if root_module in _FORBIDDEN_PROVIDER_MODULES:
                has_forbidden_import = True

            # Check for BenchmarkEngine and LLM_REGISTRY in any from-import
            for alias in node.names:
                if alias.name == "BenchmarkEngine":
                    imports_benchmark_engine = True
                if alias.name == "LLM_REGISTRY":
                    imports_llm_registry = True

        # Function definitions with forbidden names
        if isinstance(node, ast.FunctionDef) and node.name in _FORBIDDEN_FUNCTION_NAMES:
            has_forbidden_function = True

    return (
        has_forbidden_import
        or has_forbidden_function
        or not imports_benchmark_engine
        or not imports_llm_registry
    )


# ---------------------------------------------------------------------------
# Tests — all four FAIL on unfixed code (confirming the bug)
# ---------------------------------------------------------------------------


def test_script_has_no_direct_provider_imports() -> None:
    """Assert the script contains no direct provider SDK imports.

    Checks that ``import anthropic``, ``import openai``, and
    ``from mistralai import …`` are absent from the AST.

    **Validates: Requirements 2.1**

    Expected to FAIL on the unfixed script (bug confirmed).
    Expected to PASS after the fix.
    """
    tree = ast.parse(SCRIPT_SOURCE)

    forbidden_found: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root in _FORBIDDEN_PROVIDER_MODULES:
                    forbidden_found.append(f"import {alias.name}")

        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            root = module.split(".")[0]
            if root in _FORBIDDEN_PROVIDER_MODULES:
                names = ", ".join(a.name for a in node.names)
                forbidden_found.append(f"from {module} import {names}")

    assert not forbidden_found, (
        "Script contains forbidden direct provider SDK imports: " + ", ".join(forbidden_found)
    )


def test_script_does_not_define_duplicated_domain_functions() -> None:
    """Assert the script does not define duplicated domain functions.

    Checks that none of ``score_qcm``, ``score_open``, ``query_anthropic``,
    ``query_openai``, ``query_mistral`` are defined as top-level or nested
    functions.

    **Validates: Requirements 2.3**

    Expected to FAIL on the unfixed script (bug confirmed).
    Expected to PASS after the fix.
    """
    tree = ast.parse(SCRIPT_SOURCE)

    duplicated_found: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in _FORBIDDEN_FUNCTION_NAMES:
            duplicated_found.append(node.name)

    assert not duplicated_found, "Script defines duplicated domain functions: " + ", ".join(
        duplicated_found
    )


def test_script_imports_benchmark_engine() -> None:
    """Assert the script imports ``BenchmarkEngine`` from the domain layer.

    **Validates: Requirements 2.5**

    Expected to FAIL on the unfixed script (bug confirmed).
    Expected to PASS after the fix.
    """
    tree = ast.parse(SCRIPT_SOURCE)

    found = any(
        isinstance(node, ast.ImportFrom)
        and any(alias.name == "BenchmarkEngine" for alias in node.names)
        for node in ast.walk(tree)
    )

    assert found, "Script does not import BenchmarkEngine — it bypasses the domain engine entirely."


def test_script_imports_llm_registry() -> None:
    """Assert the script imports ``LLM_REGISTRY`` from the adapters layer.

    **Validates: Requirements 2.2**

    Expected to FAIL on the unfixed script (bug confirmed).
    Expected to PASS after the fix.
    """
    tree = ast.parse(SCRIPT_SOURCE)

    found = any(
        isinstance(node, ast.ImportFrom)
        and any(alias.name == "LLM_REGISTRY" for alias in node.names)
        for node in ast.walk(tree)
    )

    assert found, "Script does not import LLM_REGISTRY — it uses a hardcoded MODELS dict instead."
