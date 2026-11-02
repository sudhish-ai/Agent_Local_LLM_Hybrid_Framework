# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the universal evaluation boundary used by the ALHF Knowledge
# Foundation evaluation layer.
#
# Problem Solved:
# Knowledge Foundation artifacts require reproducible evaluation without
# coupling orchestration to groundedness, completeness, citation,
# retrieval-quality, no-answer, or future evaluation implementations.
#
# Responsibilities:
# - Accept one provider-neutral evaluation subject.
# - Produce one governed EvaluationResult.
# - Expose stable evaluator identity and version.
# - Declare whether the evaluator supports a subject.
# - Keep evaluation implementations independently replaceable.
#
# Must Not:
# - Modify the evaluated subject.
# - Perform retrieval, indexing, or representation generation.
# - Construct Evidence or Context.
# - Generate model answers.
# - Implement optimization or self-learning.
# - Promote configuration or strategy changes.
# - Depend on external RAG or orchestration frameworks.
#
# Architectural Position:
# - Stable execution boundary for Knowledge Foundation evaluation.
# - Separates measurement from optimization and learning.
# - Supports multiple independent evaluation dimensions.
#
# Reuse Value:
# - Retrieval evaluation.
# - Groundedness evaluation.
# - Completeness evaluation.
# - Citation evaluation.
# - No-answer evaluation.
# - End-to-end Knowledge Foundation evaluation.
#
# Future Extensibility:
# - Offline and online evaluators can implement this boundary.
# - Multiple evaluators can assess the same subject independently.
# - Evaluation Intelligence can consume results above this boundary.
# - Governed promotion decisions remain separate from evaluation.

from __future__ import annotations

from abc import ABC, abstractmethod

from alhf.rag.evaluation.contracts.evaluation_result import (
    EvaluationResult,
)


class Evaluator(ABC):
    """Universal provider-neutral evaluation boundary."""

    @property
    @abstractmethod
    def evaluator_ref(self) -> str:
        """Return the stable logical evaluator identifier."""

        raise NotImplementedError

    @property
    @abstractmethod
    def evaluator_version(self) -> str:
        """Return the stable evaluator behavior version."""

        raise NotImplementedError

    @abstractmethod
    def supports(
        self,
        subject: object,
    ) -> bool:
        """Return whether this evaluator supports the subject."""

        raise NotImplementedError

    @abstractmethod
    def evaluate(
        self,
        *,
        subject: object,
    ) -> EvaluationResult:
        """
        Evaluate one supported subject.

        Implementations own a single evaluation dimension while
        returning the common provider-neutral EvaluationResult.
        """

        raise NotImplementedError
