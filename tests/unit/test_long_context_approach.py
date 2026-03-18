"""Unit tests for LongContextApproach adapter."""

from pathlib import Path

import pytest

from llm_benchmark.adapters.approaches.long_context import LongContextApproach
from llm_benchmark.domain.entities import Question
from llm_benchmark.domain.value_objects import ApproachId, QuestionId, QuestionType

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_open_question(text: str = "What antibiotic?") -> Question:
    return Question(
        id=QuestionId("q1"),
        question_type=QuestionType.OPEN,
        question_text=text,
        expected_answer="amoxicillin",
    )


# ---------------------------------------------------------------------------
# approach_id
# ---------------------------------------------------------------------------


class TestLongContextApproachId:
    def test_approach_id_is_long_context(self, tmp_path: Path) -> None:
        source_file = tmp_path / "source.txt"
        source_file.write_text("SFAR guidelines content.")

        approach = LongContextApproach(source_path=source_file)

        assert approach.approach_id == ApproachId("long-context")


# ---------------------------------------------------------------------------
# prepare()
# ---------------------------------------------------------------------------


class TestLongContextApproachPrepare:
    def test_prepare_loads_source_content(self, tmp_path: Path) -> None:
        source_file = tmp_path / "source.txt"
        source_file.write_text("SFAR guidelines content.")

        approach = LongContextApproach(source_path=source_file)
        approach.prepare()

        assert approach.source_content == "SFAR guidelines content."

    def test_prepare_raises_when_source_file_missing(self, tmp_path: Path) -> None:
        missing_file = tmp_path / "nonexistent.txt"

        approach = LongContextApproach(source_path=missing_file)

        with pytest.raises(FileNotFoundError):
            approach.prepare()


# ---------------------------------------------------------------------------
# build_prompt()
# ---------------------------------------------------------------------------


class TestLongContextApproachBuildPrompt:
    def test_build_prompt_returns_non_empty_string(self, tmp_path: Path) -> None:
        source_file = tmp_path / "source.txt"
        source_file.write_text("SFAR guidelines content.")
        approach = LongContextApproach(source_path=source_file)
        approach.prepare()

        prompt = approach.build_prompt(_make_open_question())

        assert isinstance(prompt, str)
        assert prompt.strip()

    def test_build_prompt_contains_question_text(self, tmp_path: Path) -> None:
        source_file = tmp_path / "source.txt"
        source_file.write_text("SFAR guidelines content.")
        approach = LongContextApproach(source_path=source_file)
        approach.prepare()

        question = _make_open_question("Which antibiotic for cardiac surgery?")
        prompt = approach.build_prompt(question)

        assert "Which antibiotic for cardiac surgery?" in prompt

    def test_build_prompt_contains_source_content(self, tmp_path: Path) -> None:
        source_file = tmp_path / "source.txt"
        source_file.write_text("SFAR guidelines content.")
        approach = LongContextApproach(source_path=source_file)
        approach.prepare()

        prompt = approach.build_prompt(_make_open_question())

        assert "SFAR guidelines content." in prompt

    def test_build_prompt_raises_when_prepare_not_called(self, tmp_path: Path) -> None:
        source_file = tmp_path / "source.txt"
        source_file.write_text("content")
        approach = LongContextApproach(source_path=source_file)

        with pytest.raises(RuntimeError, match="prepare"):
            approach.build_prompt(_make_open_question())
