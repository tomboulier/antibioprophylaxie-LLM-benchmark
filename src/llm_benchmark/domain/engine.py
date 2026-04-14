"""BenchmarkEngine — orchestrates a full benchmark run.

Pure domain service with zero external dependencies. Iterates over every
(approach × LLM) combination, delegates prompt building, LLM calls,
scoring, and metric collection, then aggregates results into RunResult.
"""

from __future__ import annotations

import sys
import uuid
from datetime import datetime
from typing import Any

from llm_benchmark.domain.entities import (
    Dataset,
    QuestionResult,
    RunResult,
    RunSummary,
)
from llm_benchmark.domain.metrics import MetricsCollector
from llm_benchmark.domain.scorer import ScorerRegistry
from llm_benchmark.domain.value_objects import (
    Accuracy,
    Latency,
    QuestionId,
    RunId,
)
from llm_benchmark.ports.approach import ApproachPort
from llm_benchmark.ports.llm import LLMPort

_FRAMEWORK_VERSION = "0.1.0"


class BenchmarkEngine:
    """Orchestrate benchmark runs across (approach × LLM) combinations.

    Parameters
    ----------
    scorer_registry : ScorerRegistry or None, optional
        Registry used to score answers. A default instance is created when
        ``None`` is passed.
    metrics_collector : MetricsCollector or None, optional
        Collector used to compute per-question costs. A default instance
        (without carbon tracking) is created when ``None`` is passed.
    """

    def __init__(
        self,
        scorer_registry: ScorerRegistry | None = None,
        metrics_collector: MetricsCollector | None = None,
    ) -> None:
        self._scorer = scorer_registry or ScorerRegistry()
        self._metrics = metrics_collector or MetricsCollector()

    def run(
        self,
        dataset: Dataset,
        approaches: list[ApproachPort],
        llms: list[LLMPort],
        question_ids: list[QuestionId] | None = None,
    ) -> list[RunResult]:
        """Execute the benchmark for every (approach × LLM) pair.

        Parameters
        ----------
        dataset : Dataset
            The dataset of questions to evaluate.
        approaches : list[ApproachPort]
            Approach adapters to benchmark.
        llms : list[LLMPort]
            LLM adapters to benchmark.
        question_ids : list[QuestionId] or None, optional
            When provided, only the listed questions are evaluated.
            When ``None``, all questions in the dataset are used.

        Returns
        -------
        list[RunResult]
            One ``RunResult`` per (approach × LLM) combination.
        """
        questions = self._filter_questions(dataset, question_ids)
        results: list[RunResult] = []

        for approach in approaches:
            approach.prepare()
            for llm in llms:
                run_result = self._run_single(dataset, questions, approach, llm)
                results.append(run_result)

        return results

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _filter_questions(
        self,
        dataset: Dataset,
        question_ids: list[QuestionId] | None,
    ) -> list:
        if question_ids is None:
            return dataset.questions
        requested = {qid.value for qid in question_ids}
        return [question for question in dataset.questions if question.id.value in requested]

    def _run_single(
        self,
        dataset: Dataset,
        questions: list,
        approach: ApproachPort,
        llm: LLMPort,
    ) -> RunResult:
        run_id = RunId(str(uuid.uuid4()))
        timestamp = datetime.now().astimezone()
        question_results: list[QuestionResult] = []

        print(f"\n  ▶ {llm.model_id.value}")
        total = len(questions)
        correct = 0
        errors = 0
        for i, question in enumerate(questions, 1):
            question_result = self._evaluate_question(
                question, approach, llm, dataset.system_prompt
            )
            question_results.append(question_result)
            if question_result.score and question_result.score.is_correct:
                correct += 1
            if question_result.error:
                errors += 1
            bar_len = 20
            filled = int(bar_len * i / total)
            bar = "█" * filled + "░" * (bar_len - filled)
            err_part = f" {errors} err" if errors else ""
            sys.stdout.write(
                f"\r  {bar} {i}/{total}  {correct} ok{err_part}"
            )
            sys.stdout.flush()
        sys.stdout.write("\n")

        summary = self._build_summary(question_results)

        return RunResult(
            run_id=run_id,
            timestamp=timestamp,
            dataset_id=dataset.id,
            dataset_version=dataset.version.value,
            approach_id=approach.approach_id,
            model_id=llm.model_id,
            framework_version=_FRAMEWORK_VERSION,
            config={},
            summary=summary,
            results=question_results,
        )

    def _evaluate_question(
        self,
        question,
        approach: ApproachPort,
        llm: LLMPort,
        system_prompt: str = "",
    ) -> QuestionResult:
        from llm_benchmark.domain.entities import LLMRequest

        try:
            prompt = approach.build_prompt(question)
            request = LLMRequest(system_prompt=system_prompt, user_prompt=prompt)
            response = llm.complete(request)
            score = self._scorer.score(question, response.text)
            cost = self._metrics.compute_cost(llm, response)
            return QuestionResult(
                question_id=question.id,
                question_type=question.question_type,
                expected_answer=question.expected_answer,
                actual_answer=response.text,
                score=score,
                latency=response.latency,
                input_tokens=response.input_tokens,
                output_tokens=response.output_tokens,
                cost=cost,
                error=None,
            )
        except Exception as exc:  # noqa: BLE001
            return QuestionResult(
                question_id=question.id,
                question_type=question.question_type,
                expected_answer=question.expected_answer,
                actual_answer=None,
                score=None,
                error=str(exc),
            )

    def _build_summary(self, question_results: list[QuestionResult]) -> RunSummary:
        total = len(question_results)
        scored = [result for result in question_results if result.score is not None]
        correct = sum(1 for result in scored if result.score.is_correct)
        sourcing_present = sum(1 for result in scored if result.score.is_sourcing_present)
        sourcing_correct = sum(1 for result in scored if result.score.is_sourcing_correct)

        accuracy = Accuracy(correct / total if total > 0 else 0.0)
        sourcing_rate = Accuracy(sourcing_present / total if total > 0 else 0.0)
        sourcing_correct_rate = Accuracy(sourcing_correct / total if total > 0 else 0.0)

        total_tokens = self._sum_tokens(question_results)
        total_cost = self._sum_costs(question_results)
        avg_latency = self._average_latency(question_results)
        by_type = self._breakdown_by_type(question_results)

        return RunSummary(
            total=total,
            correct=correct,
            accuracy=accuracy,
            sourcing_rate=sourcing_rate,
            sourcing_correct_rate=sourcing_correct_rate,
            total_cost=total_cost,
            total_tokens=total_tokens,
            avg_latency=avg_latency,
            carbon_footprint=None,
            by_type=by_type,
        )

    def _sum_tokens(self, question_results: list[QuestionResult]) -> int | None:
        token_counts = [
            (result.input_tokens or 0) + (result.output_tokens or 0)
            for result in question_results
            if result.input_tokens is not None or result.output_tokens is not None
        ]
        return sum(token_counts) if token_counts else None

    def _sum_costs(self, question_results: list[QuestionResult]):
        costs = [result.cost for result in question_results if result.cost is not None]
        if not costs:
            return None
        from llm_benchmark.domain.value_objects import Cost

        total = sum(cost.amount for cost in costs)
        currency = costs[0].currency
        return Cost(amount=total, currency=currency)

    def _average_latency(self, question_results: list[QuestionResult]):
        latencies = [
            result.latency.seconds for result in question_results if result.latency is not None
        ]
        if not latencies:
            return None
        return Latency(sum(latencies) / len(latencies))

    def _breakdown_by_type(
        self, question_results: list[QuestionResult]
    ) -> dict[str, dict[str, Any]]:
        breakdown: dict[str, dict[str, Any]] = {}
        for result in question_results:
            type_key = result.question_type.value
            if type_key not in breakdown:
                breakdown[type_key] = {"total": 0, "correct": 0}
            breakdown[type_key]["total"] += 1
            if result.score is not None and result.score.is_correct:
                breakdown[type_key]["correct"] += 1
        for type_key, stats in breakdown.items():
            total = stats["total"]
            stats["accuracy"] = stats["correct"] / total if total > 0 else 0.0
        return breakdown
