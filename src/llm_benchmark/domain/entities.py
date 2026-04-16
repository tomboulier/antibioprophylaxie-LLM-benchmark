"""Domain entities for llm-benchmark.

Mutable dataclasses representing the core domain objects.
Unlike value objects, entities have identity and may change over time.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from llm_benchmark.domain.value_objects import (
    Accuracy,
    ApproachId,
    CarbonFootprint,
    Cost,
    DatasetId,
    DatasetVersion,
    Latency,
    MCQChoices,
    ModelId,
    QuestionId,
    QuestionType,
    RunId,
    Source,
)


@dataclass
class Question:
    """A single evaluation question, either open-ended or multiple-choice.

    Parameters
    ----------
    id : QuestionId
        Unique identifier for this question within a dataset.
    question_type : QuestionType
        Whether the question is open-ended or MCQ.
    question_text : str
        The text of the question posed to the LLM.
    expected_answer : str
        The reference answer used for scoring.
    choices : MCQChoices or None, optional
        Answer choices (A–D). Required when question_type is MCQ.

    Raises
    ------
    ValueError
        If question_type is MCQ and choices is None.
    """

    id: QuestionId
    question_type: QuestionType
    question_text: str
    expected_answer: str
    choices: MCQChoices | None = None

    def __post_init__(self) -> None:
        if self.question_type == QuestionType.MCQ and self.choices is None:
            raise ValueError(
                f"Question {self.id.value!r} is of type MCQ but choices is None. "
                "Provide MCQChoices when question_type is MCQ."
            )


@dataclass
class Dataset:
    """A versioned collection of evaluation questions.

    Parameters
    ----------
    id : DatasetId
        Unique identifier for this dataset.
    version : DatasetVersion
        Version string for reproducibility tracking.
    source : Source
        Origin of the dataset (e.g. a medical society reference).
    scope : str
        Human-readable description of the dataset's domain.
    questions : list[Question]
        The questions contained in this dataset.
    system_prompt : str, optional
        Instructions sent to the LLM as the system message for every question
        in this dataset (e.g. format constraints). Defaults to empty string.
    """

    id: DatasetId
    version: DatasetVersion
    source: Source
    scope: str
    questions: list[Question]
    system_prompt: str = ""


@dataclass
class LLMRequest:
    """A request to send to a large language model.

    Parameters
    ----------
    system_prompt : str
        Instructions that define the model's role and behaviour.
    user_prompt : str
        The actual question or task for the model.
    max_tokens : int, optional
        Maximum number of tokens in the completion. Defaults to 300.
    """

    system_prompt: str
    user_prompt: str
    max_tokens: int = 300


@dataclass
class LLMResponse:
    """A response received from a large language model.

    Parameters
    ----------
    text : str
        The generated text content.
    input_tokens : int or None, optional
        Number of tokens in the prompt, if reported by the model.
    output_tokens : int or None, optional
        Number of tokens in the completion, if reported by the model.
    latency : Latency or None, optional
        Round-trip latency for the API call.
    raw : dict[str, Any], optional
        Raw response payload from the provider for debugging.
    """

    text: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    latency: Latency | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class ScoreResult:
    """The result of evaluating a single LLM answer.

    Parameters
    ----------
    is_correct : bool
        Whether the answer matches the expected answer.
    is_sourcing_present : bool, optional
        Whether the answer contains an explicit source reference.
    is_sourcing_correct : bool, optional
        Whether the cited source matches the expected source.
    details : dict[str, Any], optional
        Additional scorer-specific metadata.
    """

    is_correct: bool
    is_sourcing_present: bool = False
    is_sourcing_correct: bool = False
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class QuestionResult:
    """The full result for a single question within a run.

    Parameters
    ----------
    question_id : QuestionId
        Reference to the evaluated question.
    question_type : QuestionType
        Type of the evaluated question.
    expected_answer : str
        The reference answer.
    actual_answer : str or None
        The answer produced by the LLM, or None if an error occurred.
    score : ScoreResult or None
        Evaluation outcome, or None if scoring was not possible.
    latency : Latency or None, optional
        Time taken for the LLM call.
    input_tokens : int or None, optional
        Prompt token count.
    output_tokens : int or None, optional
        Completion token count.
    cost : Cost or None, optional
        Estimated monetary cost for this question.
    error : str or None, optional
        Error message if the LLM call failed.
    """

    question_id: QuestionId
    question_type: QuestionType
    expected_answer: str
    actual_answer: str | None
    score: ScoreResult | None
    latency: Latency | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost: Cost | None = None
    error: str | None = None


@dataclass
class RunSummary:
    """Aggregated statistics for a benchmark run.

    Parameters
    ----------
    total : int
        Total number of questions evaluated.
    answered : int
        Number of questions that received an answer (total minus errors).
    correct : int
        Number of correctly answered questions.
    accuracy : Accuracy
        Overall accuracy (correct / answered).
    sourcing_rate : Accuracy
        Fraction of answers that contain a source reference.
    sourcing_correct_rate : Accuracy
        Fraction of answers whose source reference is correct.
    total_cost : Cost or None
        Total estimated cost for the run, if available.
    total_tokens : int or None
        Total token count (input + output), if available.
    avg_latency : Latency or None
        Average per-question latency, if available.
    carbon_footprint : CarbonFootprint or None
        Estimated CO2 equivalent for the run, if available.
    by_type : dict[str, dict[str, Any]]
        Per-question-type breakdown (e.g. ``{"open": {"total": 18, ...}}``).
    """

    total: int
    answered: int
    correct: int
    accuracy: Accuracy
    sourcing_rate: Accuracy
    sourcing_correct_rate: Accuracy
    total_cost: Cost | None
    total_tokens: int | None
    avg_latency: Latency | None
    carbon_footprint: CarbonFootprint | None
    by_type: dict[str, dict[str, Any]]


@dataclass
class RunResult:
    """The complete result of a single benchmark run.

    Parameters
    ----------
    run_id : RunId
        Unique identifier for this run (UUID4).
    timestamp : datetime
        UTC timestamp when the run was started.
    dataset_id : DatasetId
        Identifier of the dataset used.
    dataset_version : str
        Version string of the dataset used.
    approach_id : ApproachId
        Identifier of the approach used.
    model_id : ModelId
        Identifier of the LLM used.
    framework_version : str
        Version of llm-benchmark that produced this result.
    config : dict[str, Any]
        Full configuration parameters for reproducibility.
    summary : RunSummary
        Aggregated statistics for the run.
    results : list[QuestionResult]
        Per-question results.
    """

    run_id: RunId
    timestamp: datetime
    dataset_id: DatasetId
    dataset_version: str
    approach_id: ApproachId
    model_id: ModelId
    framework_version: str
    config: dict[str, Any]
    summary: RunSummary
    results: list[QuestionResult]
