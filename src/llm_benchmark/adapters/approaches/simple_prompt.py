"""Simple-prompt approach adapter — passes the question directly to the LLM."""

from __future__ import annotations

from llm_benchmark.domain.entities import Question
from llm_benchmark.domain.value_objects import ApproachId, QuestionType
from llm_benchmark.ports.approach import ApproachPort


class SimplePromptApproach(ApproachPort):
    """Minimal approach that sends the question text directly to the LLM.

    No source document is injected. For MCQ questions the answer choices
    are appended in a lettered list below the question text.
    """

    @property
    def approach_id(self) -> ApproachId:
        """Unique identifier for this approach.

        Returns
        -------
        ApproachId
            Always ``ApproachId("simple-prompt")``.
        """
        return ApproachId("simple-prompt")

    def prepare(self) -> None:
        """No-op — this approach requires no resource initialisation.

        Returns
        -------
        None
        """

    def build_prompt(self, question: Question) -> str:
        """Build the prompt for a given question.

        For open questions the prompt is the question text verbatim.
        For MCQ questions the answer choices are appended as a lettered list.

        Parameters
        ----------
        question : Question
            The question to build a prompt for.

        Returns
        -------
        str
            The prompt string ready to send to the LLM.
        """
        if question.question_type == QuestionType.OPEN:
            return question.question_text

        # MCQ: append formatted choices
        choices_lines = "\n".join(
            f"{key}. {value}" for key, value in question.choices.choices.items()
        )
        return f"{question.question_text}\n{choices_lines}"
