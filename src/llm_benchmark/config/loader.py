"""YAML configuration loader for llm-benchmark."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


class ConfigValidationError(Exception):
    """Raised when a required configuration field is missing or invalid.

    Parameters
    ----------
    message : str
        Human-readable description of the validation failure.
    """


@dataclass
class BenchmarkConfig:
    """Validated benchmark configuration loaded from a YAML file.

    Parameters
    ----------
    dataset_path : Path
        Path to the dataset JSON file.
    approaches : list[str]
        List of approach identifiers to benchmark.
    llms : list[str]
        List of LLM model identifiers to benchmark.
    output_dir : Path or None
        Directory where results will be written. Defaults to ``None``.
    question_ids : list[str] or None
        Subset of question IDs to evaluate. ``None`` means all questions.
    """

    dataset_path: Path
    approaches: list[str]
    llms: list[str]
    output_dir: Path | None = None
    question_ids: list[str] | None = None


def load_config(path: Path) -> BenchmarkConfig:
    """Load and validate a benchmark configuration from a YAML file.

    Parameters
    ----------
    path : Path
        Path to the YAML configuration file.

    Returns
    -------
    BenchmarkConfig
        Validated configuration object.

    Raises
    ------
    FileNotFoundError
        If *path* does not exist.
    ConfigValidationError
        If any required field (``dataset``, ``approaches``, ``llms``) is absent.
    """
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    with path.open(encoding="utf-8") as file_handle:
        raw = yaml.safe_load(file_handle) or {}

    _validate_required_fields(raw)

    output_dir_raw = raw.get("output_dir")
    question_ids_raw = raw.get("question_ids")

    return BenchmarkConfig(
        dataset_path=Path(raw["dataset"]),
        approaches=raw["approaches"],
        llms=raw["llms"],
        output_dir=Path(output_dir_raw) if output_dir_raw else None,
        question_ids=question_ids_raw if question_ids_raw else None,
    )


def _validate_required_fields(raw: dict) -> None:
    """Raise ConfigValidationError for each missing required field.

    Parameters
    ----------
    raw : dict
        Parsed YAML content.

    Raises
    ------
    ConfigValidationError
        If ``dataset``, ``approaches``, or ``llms`` is absent.
    """
    required = ["dataset", "approaches", "llms"]
    missing = [field for field in required if field not in raw]
    if missing:
        raise ConfigValidationError(
            f"Missing required configuration field(s): {', '.join(missing)}"
        )
