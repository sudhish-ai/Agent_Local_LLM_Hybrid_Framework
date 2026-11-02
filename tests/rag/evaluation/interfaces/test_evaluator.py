# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF Evaluator interface.
#
# Responsibilities:
# - Validate the abstract evaluation boundary.
# - Validate evaluator identity and version contracts.
# - Validate subject support declaration.
# - Validate provider-neutral EvaluationResult production.
# - Validate evaluation status and score preservation.
#
# Must Not:
# - Test concrete production evaluation dimensions.
# - Perform retrieval or Evidence construction.
# - Construct Context or generate answers.
# - Implement optimization or self-learning.
# - Implement configuration promotion.
# - Depend on external RAG frameworks.

import pytest

from alhf.rag.evaluation.contracts.evaluation_result import (
    EvaluationResult,
    EvaluationStatus,
)
from alhf.rag.evaluation.interfaces.evaluator import (
    Evaluator,
)


class StubEvaluator(Evaluator):
    """Minimal concrete evaluator for interface testing."""

    @property
    def evaluator_ref(self) -> str:
        return "stub-evaluator"

    @property
    def evaluator_version(self) -> str:
        return "1.0"

    def supports(
        self,
        subject: object,
    ) -> bool:
        return isinstance(
            subject,
            str,
        )

    def evaluate(
        self,
        *,
        subject: object,
    ) -> EvaluationResult:
        if not self.supports(
            subject
        ):
            raise ValueError(
                "StubEvaluator requires a string subject"
            )

        return EvaluationResult(
            evaluation_id="evaluation-001",
            subject_ref=subject,
            evaluator_ref=self.evaluator_ref,
            evaluator_version=self.evaluator_version,
            status=EvaluationStatus.PASS,
            score=1.0,
            reason="supported subject",
        )


class MissingEvaluateEvaluator(Evaluator):
    """Invalid evaluator intentionally missing evaluate behavior."""

    @property
    def evaluator_ref(self) -> str:
        return "missing-evaluate"

    @property
    def evaluator_version(self) -> str:
        return "1.0"

    def supports(
        self,
        subject: object,
    ) -> bool:
        return True


def _evaluator() -> StubEvaluator:
    return StubEvaluator()


def test_evaluator_is_abstract() -> None:
    with pytest.raises(TypeError):
        Evaluator()


def test_missing_evaluate_prevents_instantiation() -> None:
    with pytest.raises(TypeError):
        MissingEvaluateEvaluator()


def test_concrete_evaluator_can_be_instantiated() -> None:
    assert isinstance(
        _evaluator(),
        Evaluator,
    )


def test_evaluator_exposes_stable_reference() -> None:
    assert _evaluator().evaluator_ref == "stub-evaluator"


def test_evaluator_exposes_stable_version() -> None:
    assert _evaluator().evaluator_version == "1.0"


def test_evaluator_supports_expected_subject() -> None:
    assert _evaluator().supports(
        "context-001"
    ) is True


def test_evaluator_rejects_unsupported_subject() -> None:
    assert _evaluator().supports(
        123
    ) is False


def test_evaluate_returns_evaluation_result() -> None:
    result = _evaluator().evaluate(
        subject="context-001"
    )

    assert isinstance(
        result,
        EvaluationResult,
    )


def test_evaluate_preserves_subject_reference() -> None:
    result = _evaluator().evaluate(
        subject="context-001"
    )

    assert result.subject_ref == "context-001"


def test_evaluate_preserves_evaluator_identity() -> None:
    evaluator = _evaluator()

    result = evaluator.evaluate(
        subject="context-001"
    )

    assert result.evaluator_ref == evaluator.evaluator_ref
    assert result.evaluator_version == evaluator.evaluator_version


def test_evaluate_preserves_status_and_score() -> None:
    result = _evaluator().evaluate(
        subject="context-001"
    )

    assert result.status == EvaluationStatus.PASS
    assert result.score == 1.0
    assert result.reason == "supported subject"


def test_unsupported_subject_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="StubEvaluator requires a string subject",
    ):
        _evaluator().evaluate(
            subject=123
        )
