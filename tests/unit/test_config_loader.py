"""Unit tests for the YAML configuration loader."""

import textwrap
from pathlib import Path

import pytest

from llm_benchmark.config.loader import BenchmarkConfig, ConfigValidationError, load_config

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_yaml(tmp_path: Path, content: str) -> Path:
    """Write *content* to a YAML file in *tmp_path* and return its path."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(textwrap.dedent(content))
    return config_file


# ---------------------------------------------------------------------------
# Valid configuration
# ---------------------------------------------------------------------------


class TestLoadConfigValid:
    def test_returns_benchmark_config_instance(self, tmp_path: Path) -> None:
        config_file = _write_yaml(
            tmp_path,
            """
            dataset: datasets/sfar/benchmark.json
            approaches:
              - long-context
            llms:
              - gpt-4o
            """,
        )

        config = load_config(config_file)

        assert isinstance(config, BenchmarkConfig)

    def test_dataset_path_is_resolved(self, tmp_path: Path) -> None:
        config_file = _write_yaml(
            tmp_path,
            """
            dataset: datasets/sfar/benchmark.json
            approaches:
              - long-context
            llms:
              - gpt-4o
            """,
        )

        config = load_config(config_file)

        assert config.dataset_path == Path("datasets/sfar/benchmark.json")

    def test_approaches_list_is_loaded(self, tmp_path: Path) -> None:
        config_file = _write_yaml(
            tmp_path,
            """
            dataset: datasets/sfar/benchmark.json
            approaches:
              - long-context
              - rag-pdf
            llms:
              - gpt-4o
            """,
        )

        config = load_config(config_file)

        assert config.approaches == ["long-context", "rag-pdf"]

    def test_llms_list_is_loaded(self, tmp_path: Path) -> None:
        config_file = _write_yaml(
            tmp_path,
            """
            dataset: datasets/sfar/benchmark.json
            approaches:
              - long-context
            llms:
              - gpt-4o
              - claude-sonnet
            """,
        )

        config = load_config(config_file)

        assert config.llms == ["gpt-4o", "claude-sonnet"]

    def test_optional_output_dir_defaults_to_none(self, tmp_path: Path) -> None:
        config_file = _write_yaml(
            tmp_path,
            """
            dataset: datasets/sfar/benchmark.json
            approaches:
              - long-context
            llms:
              - gpt-4o
            """,
        )

        config = load_config(config_file)

        assert config.output_dir is None

    def test_optional_output_dir_is_loaded_when_present(self, tmp_path: Path) -> None:
        config_file = _write_yaml(
            tmp_path,
            """
            dataset: datasets/sfar/benchmark.json
            approaches:
              - long-context
            llms:
              - gpt-4o
            output_dir: results/
            """,
        )

        config = load_config(config_file)

        assert config.output_dir == Path("results/")

    def test_optional_question_ids_defaults_to_none(self, tmp_path: Path) -> None:
        config_file = _write_yaml(
            tmp_path,
            """
            dataset: datasets/sfar/benchmark.json
            approaches:
              - long-context
            llms:
              - gpt-4o
            """,
        )

        config = load_config(config_file)

        assert config.question_ids is None

    def test_optional_question_ids_is_loaded_when_present(self, tmp_path: Path) -> None:
        config_file = _write_yaml(
            tmp_path,
            """
            dataset: datasets/sfar/benchmark.json
            approaches:
              - long-context
            llms:
              - gpt-4o
            question_ids:
              - q1
              - q2
            """,
        )

        config = load_config(config_file)

        assert config.question_ids == ["q1", "q2"]


# ---------------------------------------------------------------------------
# Missing required fields
# ---------------------------------------------------------------------------


class TestLoadConfigMissingFields:
    def test_raises_when_dataset_missing(self, tmp_path: Path) -> None:
        config_file = _write_yaml(
            tmp_path,
            """
            approaches:
              - long-context
            llms:
              - gpt-4o
            """,
        )

        with pytest.raises(ConfigValidationError, match="dataset"):
            load_config(config_file)

    def test_raises_when_approaches_missing(self, tmp_path: Path) -> None:
        config_file = _write_yaml(
            tmp_path,
            """
            dataset: datasets/sfar/benchmark.json
            llms:
              - gpt-4o
            """,
        )

        with pytest.raises(ConfigValidationError, match="approaches"):
            load_config(config_file)

    def test_raises_when_llms_missing(self, tmp_path: Path) -> None:
        config_file = _write_yaml(
            tmp_path,
            """
            dataset: datasets/sfar/benchmark.json
            approaches:
              - long-context
            """,
        )

        with pytest.raises(ConfigValidationError, match="llms"):
            load_config(config_file)

    def test_raises_when_file_does_not_exist(self, tmp_path: Path) -> None:
        missing_path = tmp_path / "nonexistent.yaml"

        with pytest.raises(FileNotFoundError):
            load_config(missing_path)
