"""Unit tests for the CLI entry point."""

import pytest

from llm_benchmark.cli.main import build_parser, main

# ---------------------------------------------------------------------------
# list subcommands (no network, no files needed)
# ---------------------------------------------------------------------------


class TestListSubcommands:
    def test_list_models_exits_zero(self, capsys) -> None:
        with pytest.raises(SystemExit) as exc_info:
            main(["list", "models"])
        assert exc_info.value.code == 0

    def test_list_models_prints_model_ids(self, capsys) -> None:
        with pytest.raises(SystemExit):
            main(["list", "models"])
        output = capsys.readouterr().out
        assert output.strip()  # at least one line printed

    def test_list_approaches_exits_zero(self, capsys) -> None:
        with pytest.raises(SystemExit) as exc_info:
            main(["list", "approaches"])
        assert exc_info.value.code == 0

    def test_list_approaches_prints_approach_ids(self, capsys) -> None:
        with pytest.raises(SystemExit):
            main(["list", "approaches"])
        output = capsys.readouterr().out
        assert "long-context" in output


# ---------------------------------------------------------------------------
# run subcommand — argument validation
# ---------------------------------------------------------------------------


class TestRunSubcommandValidation:
    def test_run_without_dataset_exits_nonzero(self, capsys) -> None:
        with pytest.raises(SystemExit) as exc_info:
            main(["run", "--approach", "long-context", "--model", "gpt-4o"])
        assert exc_info.value.code != 0

    def test_run_without_approach_exits_nonzero(self, capsys) -> None:
        with pytest.raises(SystemExit) as exc_info:
            main(["run", "--dataset", "data.json", "--model", "gpt-4o"])
        assert exc_info.value.code != 0

    def test_run_without_model_exits_nonzero(self, capsys) -> None:
        with pytest.raises(SystemExit) as exc_info:
            main(["run", "--dataset", "data.json", "--approach", "long-context"])
        assert exc_info.value.code != 0


# ---------------------------------------------------------------------------
# compare subcommand — argument validation
# ---------------------------------------------------------------------------


class TestCompareSubcommandValidation:
    def test_compare_without_runs_exits_nonzero(self, capsys) -> None:
        with pytest.raises(SystemExit) as exc_info:
            main(["compare"])
        assert exc_info.value.code != 0


# ---------------------------------------------------------------------------
# Parser structure
# ---------------------------------------------------------------------------


class TestParserStructure:
    def test_parser_returns_argument_parser(self) -> None:
        import argparse

        parser = build_parser()
        assert isinstance(parser, argparse.ArgumentParser)

    def test_run_subcommand_accepts_multiple_approaches(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "run",
                "--dataset",
                "data.json",
                "--approach",
                "long-context",
                "--approach",
                "rag-pdf",
                "--model",
                "gpt-4o",
            ]
        )
        assert args.approach == ["long-context", "rag-pdf"]

    def test_run_subcommand_accepts_multiple_models(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "run",
                "--dataset",
                "data.json",
                "--approach",
                "long-context",
                "--model",
                "gpt-4o",
                "--model",
                "claude-sonnet",
            ]
        )
        assert args.model == ["gpt-4o", "claude-sonnet"]

    def test_run_subcommand_accepts_question_filter(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "run",
                "--dataset",
                "data.json",
                "--approach",
                "long-context",
                "--model",
                "gpt-4o",
                "--questions",
                "q1",
                "q2",
            ]
        )
        assert args.questions == ["q1", "q2"]

    def test_run_subcommand_accepts_output_dir(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "run",
                "--dataset",
                "data.json",
                "--approach",
                "long-context",
                "--model",
                "gpt-4o",
                "--output-dir",
                "results/",
            ]
        )
        assert args.output_dir == "results/"
