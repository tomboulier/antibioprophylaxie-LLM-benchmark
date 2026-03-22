"""ApproachPort — abstract interface for knowledge-access approaches."""

from abc import ABC, abstractmethod

from llm_benchmark.domain.entities import Question
from llm_benchmark.domain.value_objects import ApproachId


class ApproachPort(ABC):
    """Contract that every knowledge-access approach adapter must fulfil.

    An approach is responsible for building the prompt sent to the LLM
    and for preparing any required resources (indexes, connections, etc.).
    """

    @property
    def system_prompt(self) -> str:
        """System-level instructions sent to the LLM before the user prompt.

        Override in subclasses to provide format or role instructions.
        Defaults to an empty string (no system prompt).

        Returns
        -------
        str
            The system prompt string.
        """
        return ""

    @property
    @abstractmethod
    def approach_id(self) -> ApproachId:
        """Unique identifier for this approach (e.g. ``ApproachId('rag-pdf')``).

        Returns
        -------
        ApproachId
            The approach identifier.
        """

    @abstractmethod
    def build_prompt(self, question: Question) -> str:
        """Build the user prompt to send to the LLM for a given question.

        Parameters
        ----------
        question : Question
            The question to answer.

        Returns
        -------
        str
            The prompt string to pass to the LLM.
        """

    @abstractmethod
    def prepare(self) -> None:
        """Initialise any resources required by this approach.

        This may include loading indexes, establishing connections, or
        reading source documents into memory. Called once before a run.
        """
