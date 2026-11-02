# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides provider-neutral evaluation orchestration for ALHF RAG V1.
#
# Problem Solved:
# Knowledge Foundation artifacts must be evaluated through configured
# evaluators without coupling common orchestration to individual quality
# dimensions or future evaluation technologies.
#
# Responsibilities:
# - Accept one evaluation subject.
# - Validate evaluator support for the subject.
# - Delegate evaluation to the configured Evaluator.
# - Validate provider-neutral EvaluationResult output.
# - Validate evaluator identity and version continuity.
#
# Must Not:
# - Implement evaluation algorithms.
# - Perform retrieval, indexing, or representation generation.
# - Construct Evidence or Context.
# - Generate model answers.
# - Implement optimization or self-learning.
# - Promote configuration or strategy changes.
# - Depend on external RAG or orchestration frameworks.
#
# Architectural Position:
# - Common orchestration boundary for Knowledge evaluation.
# - Separates evaluation execution from evaluation dimensions.
# - Keeps measurement independent from future optimization intelligence.
#
# Reuse Value:
# - V1 deterministic Context evaluation.
# - Retrieval, groundedness, completeness, and citation evaluation.
# - No-answer evaluation.
# - End-to-end Knowledge Foundation evaluation.
#
# Future Extensibility:
# - Multiple evaluation dimensions can compose above this service.
# - Offline and online evaluators can use the same boundary.
# - Knowledge Intelligence can consume EvaluationResult artifacts.
# - Governed learning and promotion remain separate capabilities.

from __future__ import annotations

from alhf.rag.evaluation.contracts.evaluation_result import (
    EvaluationResult,
)
from alhf.rag.evaluation.interfaces.evaluator import (
    Evaluator,
)


class EvaluationService:
    """Provider-neutral orchestration for Knowledge evaluation."""

    def __init__(
        self,
        *,
        evaluator: Evaluator,
    ) -> None:
        if not isinstance(
            evaluator,
            Evaluator,
        ):
            raise TypeError(
                "evaluator must be an instance of Evaluator"
            )

        self._evaluator = evaluator

    def evaluate(
        self,
        *,
        subject: object,
    ) -> EvaluationResult:
        """Evaluate one subject through the configured evaluator."""

        if not self._evaluator.supports(
            subject
        ):
            raise ValueError(
                "configured evaluator does not support subject"
            )

        result = self._evaluator.evaluate(
            subject=subject
        )

        if not isinstance(
            result,
            EvaluationResult,
        ):
            raise TypeError(
                "evaluator must return EvaluationResult"
            )

        if result.evaluator_ref != self._evaluator.evaluator_ref:
            raise ValueError(
                "EvaluationResult evaluator_ref must match evaluator"
            )

        if (
            result.evaluator_version
            != self._evaluator.evaluator_version
        ):
            raise ValueError(
                "EvaluationResult evaluator_version must match evaluator"
            )

        return result
