"""Unit tests for the CLI entry point."""

import argparse

import pytest

from llm_benchmark.cli.main import build_parser, main

# ---------------------------------------------------------------------------
# list subcommand
# ---------------------------------------------------------------------------


class TestListSubcommands:
    def test_list_models_prints_model_ids(self, capsys) -> None:
        main(["list", "models"])
        output = capsys.readouterr().out
        assert output.strip()

    def test_list_models_shows_enabled_marker(self, capsys) -> None:
        main(["list", "models"])
        output = capsys.readouterr().out
        assert "*" in output

    def test_list_unknown_resource_exits_nonzero(self) -> None:
        with pytest.raises(SystemExit) as exc_info:
            main(["list", "unknown"])
        assert exc_info.value.code != 0


# ---------------------------------------------------------------------------
# Parser structure
# ---------------------------------------------------------------------------


class TestParserStructure:
    def test_parser_returns_argument_parser(self) -> None:
        parser = build_parser()
        assert isinstance(parser, argparse.ArgumentParser)

    def test_run_subcommand_accepts_multiple_models(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["run", "-m", "gpt-4o", "-m", "claude-sonnet-4-5"])
        assert args.models == ["gpt-4o", "claude-sonnet-4-5"]

    def test_run_subcommand_accepts_question_filter(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["run", "-q", "Q01,Q05"])
        assert args.questions == "Q01,Q05"

    def test_no_command_exits_nonzero(self) -> None:
        with pytest.raises(SystemExit) as exc_info:
            main([])
        assert exc_info.value.code != 0
