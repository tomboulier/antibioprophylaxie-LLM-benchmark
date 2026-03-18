"""Unit tests for dotenv loading behaviour in the CLI entry point.

These tests are written TDD-style: they describe the behaviour that will be
implemented in Task 2 (wiring ``load_dotenv`` into ``main()``).  All tests
are expected to fail until that implementation is in place.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_env_file(directory: Path, content: str) -> Path:
    """Write a ``.env`` file with the given content inside *directory*.

    Parameters
    ----------
    directory : Path
        Directory in which the ``.env`` file is created.
    content : str
        Raw text content to write into the file.

    Returns
    -------
    Path
        Absolute path to the created ``.env`` file.
    """
    env_file = directory / ".env"
    env_file.write_text(content, encoding="utf-8")
    return env_file


# ---------------------------------------------------------------------------
# Test: .env present → load_dotenv called before any handler runs
# ---------------------------------------------------------------------------


class TestDotenvPresentLoadsVariables:
    """load_dotenv is called when a .env file exists in the working directory."""

    def test_load_dotenv_is_called_when_env_file_exists(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """main() calls load_dotenv(override=False) before dispatching commands.

        Parameters
        ----------
        tmp_path : Path
            Pytest-provided temporary directory.
        monkeypatch : pytest.MonkeyPatch
            Pytest fixture for safe environment and attribute patching.
        """
        _write_env_file(tmp_path, "SOME_API_KEY=test-value\n")
        monkeypatch.chdir(tmp_path)

        with patch("dotenv.load_dotenv") as mock_load_dotenv:
            with pytest.raises(SystemExit):
                from llm_benchmark.cli.main import main

                main([])  # no subcommand → exits 1, but load_dotenv must be called first

        mock_load_dotenv.assert_called_once()

    def test_load_dotenv_called_with_override_false(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """main() passes override=False to load_dotenv to preserve existing env vars.

        Parameters
        ----------
        tmp_path : Path
            Pytest-provided temporary directory.
        monkeypatch : pytest.MonkeyPatch
            Pytest fixture for safe environment and attribute patching.
        """
        _write_env_file(tmp_path, "SOME_API_KEY=test-value\n")
        monkeypatch.chdir(tmp_path)

        with patch("dotenv.load_dotenv") as mock_load_dotenv:
            with pytest.raises(SystemExit):
                from llm_benchmark.cli.main import main

                main([])

        _call_kwargs = mock_load_dotenv.call_args
        assert _call_kwargs is not None
        # override=False must be passed either as keyword or positional arg
        assert _call_kwargs.kwargs.get("override") is False or (
            len(_call_kwargs.args) >= 2 and _call_kwargs.args[1] is False
        )


# ---------------------------------------------------------------------------
# Test: no .env file → no error, environment unchanged
# ---------------------------------------------------------------------------


class TestNoDotenvFileNoError:
    """main() proceeds without error when no .env file is present."""

    def test_no_error_when_env_file_absent(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """main() does not raise when .env is missing; exits normally for no-command.

        Parameters
        ----------
        tmp_path : Path
            Pytest-provided temporary directory (no .env file created here).
        monkeypatch : pytest.MonkeyPatch
            Pytest fixture for safe environment and attribute patching.
        """
        monkeypatch.chdir(tmp_path)
        assert not (tmp_path / ".env").exists()

        with patch("dotenv.load_dotenv"):
            # No subcommand → SystemExit(1), but no other exception should propagate
            with pytest.raises(SystemExit) as exc_info:
                from llm_benchmark.cli.main import main

                main([])

        # Only a SystemExit from the missing subcommand is acceptable — not an IOError
        assert exc_info.value.code is not None

    def test_environment_unchanged_when_env_file_absent(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Environment variables are not modified when no .env file is present.

        Parameters
        ----------
        tmp_path : Path
            Pytest-provided temporary directory (no .env file created here).
        monkeypatch : pytest.MonkeyPatch
            Pytest fixture for safe environment and attribute patching.
        """
        monkeypatch.chdir(tmp_path)
        sentinel_key = "DOTENV_TEST_SENTINEL_ABSENT"
        monkeypatch.delenv(sentinel_key, raising=False)

        with patch("dotenv.load_dotenv"):
            with pytest.raises(SystemExit):
                from llm_benchmark.cli.main import main

                main([])

        import os

        assert sentinel_key not in os.environ


# ---------------------------------------------------------------------------
# Test: variable already set → existing value preserved (no override)
# ---------------------------------------------------------------------------


class TestPreExistingVariableNotOverridden:
    """Pre-existing environment variables are not overwritten by .env values."""

    def test_existing_env_var_preserved_after_load(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A variable already in the environment keeps its value after main() runs.

        Parameters
        ----------
        tmp_path : Path
            Pytest-provided temporary directory.
        monkeypatch : pytest.MonkeyPatch
            Pytest fixture for safe environment and attribute patching.
        """
        import os

        key = "DOTENV_TEST_PREEXISTING_KEY"
        original_value = "original-secret"
        dotenv_value = "dotenv-override-attempt"

        monkeypatch.setenv(key, original_value)
        _write_env_file(tmp_path, f"{key}={dotenv_value}\n")
        monkeypatch.chdir(tmp_path)

        # Let the real load_dotenv run (override=False is the behaviour under test)
        with pytest.raises(SystemExit):
            from llm_benchmark.cli.main import main

            main([])

        assert os.environ[key] == original_value


# ---------------------------------------------------------------------------
# Test: malformed .env file → descriptive error, non-zero exit
# ---------------------------------------------------------------------------


class TestMalformedDotenvFileExitsWithError:
    """A malformed .env file causes main() to print a descriptive error and exit(1).

    python-dotenv 1.2.x raises a ``ValueError`` (e.g. ``UnicodeDecodeError``) when it
    cannot parse the file.  The CLI must catch that and exit with a non-zero code.
    """

    def test_malformed_env_file_exits_nonzero(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """main() exits with a non-zero code when the .env file is malformed.

        Parameters
        ----------
        tmp_path : Path
            Pytest-provided temporary directory.
        monkeypatch : pytest.MonkeyPatch
            Pytest fixture for safe environment and attribute patching.
        """
        _write_env_file(tmp_path, "THIS IS NOT VALID DOTENV ===\x00\xff\n")
        monkeypatch.chdir(tmp_path)

        with patch("dotenv.load_dotenv", side_effect=ValueError("parse error")):
            with pytest.raises(SystemExit) as exc_info:
                from llm_benchmark.cli.main import main

                main(["list", "models"])

        assert exc_info.value.code != 0

    def test_malformed_env_file_prints_descriptive_message_to_stderr(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
    ) -> None:
        """main() writes a human-readable error message to stderr on malformed .env.

        Parameters
        ----------
        tmp_path : Path
            Pytest-provided temporary directory.
        monkeypatch : pytest.MonkeyPatch
            Pytest fixture for safe environment and attribute patching.
        capsys : pytest.CaptureFixture
            Pytest fixture for capturing stdout/stderr output.
        """
        _write_env_file(tmp_path, "THIS IS NOT VALID DOTENV ===\x00\xff\n")
        monkeypatch.chdir(tmp_path)

        with patch("dotenv.load_dotenv", side_effect=ValueError("parse error")):
            with pytest.raises(SystemExit):
                from llm_benchmark.cli.main import main

                main(["list", "models"])

        stderr_output = capsys.readouterr().err
        assert stderr_output.strip(), "Expected a descriptive error message on stderr"
        # The message should mention .env so the user knows what went wrong
        assert ".env" in stderr_output
