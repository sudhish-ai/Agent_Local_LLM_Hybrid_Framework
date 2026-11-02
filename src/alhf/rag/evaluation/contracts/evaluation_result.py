# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the provider-neutral evaluation result produced by the ALHF
# Knowledge Foundation evaluation layer.
#
# Problem Solved:
# Knowledge-pipeline behavior must be evaluated through explicit,
# reproducible artifacts instead of implicit pass/fail assumptions.
#
# Responsibilities:
# - Identify one evaluation result.
# - Identify the evaluated subject.
# - Preserve evaluator identity and version.
# - Record explicit evaluation status.
# - Record a normalized evaluation score.
# - Preserve a human-readable evaluation reason.
# - Provide immutable evaluation semantics.
#
# Must Not:
# - Perform retrieval or representation generation.
# - Construct Evidence or Context.
# - Generate model answers.
# - Modify the evaluated artifact.
# - Implement adaptive optimization or self-learning.
# - Promote configuration or strategy changes.
# - Depend on external RAG or orchestration frameworks.
#
# Architectural Position:
# - Stable output boundary for Knowledge Foundation evaluation.
# - Provides reproducible quality signals for V1 validation.
# - Separates measurement from future optimization intelligence.
#
# Reuse Value:
# - Retrieval evaluation.
# - Evidence evaluation.
# - Context evaluation.
# - End-to-end RAG evaluation.
# - Future regression and quality-gate evaluation.
#
# Future Extensibility:
# - Offline and online evaluators can share this result contract.
# - Multiple evaluation dimensions can evolve through new evaluators.
# - Knowledge Intelligence can consume evaluations without owning them.
# - Promotion and self-learning decisions remain separate capabilities.

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum


class EvaluationStatus(str, Enum):
    """Outcome of one governed evaluation."""

    PASS = "PASS"
    FAIL = "FAIL"
    INCONCLUSIVE = "INCONCLUSIVE"


@dataclass(frozen=True, slots=True)
class EvaluationResult:
    """Immutable result of one Knowledge Foundation evaluation."""

    evaluation_id: str
    subject_ref: str
    evaluator_ref: str
    evaluator_version: str
    status: EvaluationStatus
    score: float
    reason: str

    def __post_init__(self) -> None:
        fields = (
            "evaluation_id",
            "subject_ref",
            "evaluator_ref",
            "evaluator_version",
            "reason",
        )

        for field_name in fields:
            normalized = self._required_text(
                value=getattr(
                    self,
                    field_name,
                ),
                field_name=field_name,
            )

            object.__setattr__(
                self,
                field_name,
                normalized,
            )

        if not isinstance(
            self.status,
            EvaluationStatus,
        ):
            raise TypeError(
                "status must be an instance of EvaluationStatus"
            )

        if isinstance(
            self.score,
            bool,
        ) or not isinstance(
            self.score,
            (int, float),
        ):
            raise TypeError(
                "score must be a number"
            )

        score = float(
            self.score
        )

        if not math.isfinite(
            score
        ):
            raise ValueError(
                "score must be finite"
            )

        if score < 0.0 or score > 1.0:
            raise ValueError(
                "score must be between 0.0 and 1.0"
            )

        object.__setattr__(
            self,
            "score",
            score,
        )

    @staticmethod
    def _required_text(
        *,
        value: str,
        field_name: str,
    ) -> str:
        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                f"{field_name} must be a string"
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                f"{field_name} cannot be empty"
            )

        return normalized
