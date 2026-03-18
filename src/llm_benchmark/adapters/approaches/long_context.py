"""Long-context approach adapter — baseline that injects the full source document."""

from __future__ import annotations

from pathlib import Path

from llm_benchmark.domain.entities import Question
from llm_benchmark.domain.value_objects import ApproachId
from llm_benchmark.ports.approach import ApproachPort


class LongContextApproach(ApproachPort):
    """Baseline approach that provides the full source document as context.

    The entire source text is included in every prompt, giving the LLM
    direct access to the reference material without retrieval.

    Parameters
    ----------
    source_path : Path
        Path to the plain-text source document (e.g. SFAR guidelines).
    """

    def __init__(self, source_path: Path) -> None:
        self._source_path = source_path
        self._source_content: str | None = None

    @property
    def approach_id(self) -> ApproachId:
        """Unique identifier for this approach.

        Returns
        -------
        ApproachId
            Always ``ApproachId("long-context")``.
        """
        return ApproachId("long-context")

    @property
    def source_content(self) -> str | None:
        """The loaded source document text, or ``None`` before ``prepare`` is called.

        Returns
        -------
        str or None
            Source document content.
        """
        return self._source_content

    def prepare(self) -> None:
        """Load the source document into memory.

        Raises
        ------
        FileNotFoundError
            If ``source_path`` does not exist.
        """
        if not self._source_path.exists():
            raise FileNotFoundError(f"Source file not found: {self._source_path}")
        self._source_content = self._source_path.read_text(encoding="utf-8")

    def build_prompt(self, question: Question) -> str:
        """Build a prompt that embeds the full source document and the question.

        Parameters
        ----------
        question : Question
            The question to answer.

        Returns
        -------
        str
            Prompt string ready to send to the LLM.

        Raises
        ------
        RuntimeError
            If ``prepare`` has not been called yet.
        """
        if self._source_content is None:
            raise RuntimeError(
                "Source content is not loaded. Call prepare() before build_prompt()."
            )
        return (
            f"Using the following reference document, answer the question.\n\n"
            f"--- REFERENCE DOCUMENT ---\n{self._source_content}\n"
            f"--- END OF DOCUMENT ---\n\n"
            f"Question: {question.question_text}"
        )
