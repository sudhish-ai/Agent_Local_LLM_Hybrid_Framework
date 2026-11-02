# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF EvaluationService.
#
# Responsibilities:
# - Validate provider-neutral evaluation orchestration.
# - Validate evaluator support enforcement.
# - Validate EvaluationResult production.
# - Validate evaluator identity and version continuity.
# - Validate unsupported subject rejection.
# - Validate malformed evaluator output rejection.
#
# Must Not:
# - Test concrete evaluation algorithms in depth.
# - Perform retrieval, Evidence, or Context construction.
# - Generate model answers.
# - Implement optimization or self-learning.
# - Implement configuration promotion.
# - Depend on external RAG frameworks.

import pytest

from alhf.rag.context_packing.contracts.knowledge_context import (
    KnowledgeContext,
)
from alhf.rag.evaluation.contracts.evaluation_result import (
    EvaluationResult,
    EvaluationStatus,
)
from alhf.rag.evaluation.evaluation_service import (
    EvaluationService,
)
from alhf.rag.evaluation.interfaces.evaluator import (
    Evaluator,
)
from alhf.rag.evaluation.providers.deterministic_context_evaluator import (
    DeterministicContextEvaluator,
)


def _context(
    *,
    evidence_refs: tuple[str, ...] = ("evidence-001",),
    content: bytes = b"enterprise context",
) -> KnowledgeContext:
    return KnowledgeContext(
        context_id="context-001",
        knowledge_scope_ref="scope-001",
        evidence_refs=evidence_refs,
        content=content,
        media_type="text/plain",
        strategy_ref="deterministic-context-packer",
        strategy_version="1.0",
    )


def _service() -> EvaluationService:
    return EvaluationService(
        evaluator=DeterministicContextEvaluator(),
    )


def test_create_evaluation_service() -> None:
    assert isinstance(
        _service(),
        EvaluationService,
    )


def test_evaluate_returns_evaluation_result() -> None:
    result = _service().evaluate(
        subject=_context()
    )

    assert isinstance(
        result,
        EvaluationResult,
    )


def test_evaluate_preserves_subject_reference() -> None:
    result = _service().evaluate(
        subject=_context()
    )

    assert result.subject_ref == "context-001"


def test_non_empty_context_passes() -> None:
    result = _service().evaluate(
        subject=_context()
    )

    assert result.status == EvaluationStatus.PASS
    assert result.score == 1.0
    assert result.reason == (
        "Knowledge Context contains packed Evidence"
    )


def test_empty_context_is_inconclusive() -> None:
    result = _service().evaluate(
        subject=_context(
            evidence_refs=(),
            content=b"",
        )
    )

    assert result.status == EvaluationStatus.INCONCLUSIVE
    assert result.score == 0.0


def test_evaluate_preserves_evaluator_identity() -> None:
    result = _service().evaluate(
        subject=_context()
    )

    assert result.evaluator_ref == (
        "deterministic-context-evaluator"
    )
    assert result.evaluator_version == "1.0"


def test_repeated_evaluation_is_deterministic() -> None:
    service = _service()
    context = _context()

    first = service.evaluate(
        subject=context
    )
    second = service.evaluate(
        subject=context
    )

    assert first == second
    assert first.evaluation_id == second.evaluation_id


def test_invalid_evaluator_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match="evaluator must be an instance of Evaluator",
    ):
        EvaluationService(
            evaluator="invalid-evaluator"
        )


def test_unsupported_subject_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "configured evaluator does not support subject"
        ),
    ):
        _service().evaluate(
            subject="invalid-subject"
        )


class InvalidResultEvaluator(Evaluator):
    """Evaluator intentionally returning an invalid result."""

    @property
    def evaluator_ref(self) -> str:
        return "invalid-result-evaluator"

    @property
    def evaluator_version(self) -> str:
        return "1.0"

    def supports(
        self,
        subject: object,
    ) -> bool:
        return True

    def evaluate(
        self,
        *,
        subject: object,
    ):
        return "invalid-result"


def test_invalid_evaluation_result_is_rejected() -> None:
    service = EvaluationService(
        evaluator=InvalidResultEvaluator()
    )

    with pytest.raises(
        TypeError,
        match="evaluator must return EvaluationResult",
    ):
        service.evaluate(
            subject=_context()
        )


class WrongIdentityEvaluator(Evaluator):
    """Evaluator intentionally returning mismatched identity."""

    @property
    def evaluator_ref(self) -> str:
        return "expected-evaluator"

    @property
    def evaluator_version(self) -> str:
        return "1.0"

    def supports(
        self,
        subject: object,
    ) -> bool:
        return True

    def evaluate(
        self,
        *,
        subject: object,
    ) -> EvaluationResult:
        return EvaluationResult(
            evaluation_id="evaluation-001",
            subject_ref="context-001",
            evaluator_ref="wrong-evaluator",
            evaluator_version="1.0",
            status=EvaluationStatus.PASS,
            score=1.0,
            reason="test result",
        )


def test_mismatched_evaluator_reference_is_rejected() -> None:
    service = EvaluationService(
        evaluator=WrongIdentityEvaluator()
    )

    with pytest.raises(
        ValueError,
        match=(
            "EvaluationResult evaluator_ref must match evaluator"
        ),
    ):
        service.evaluate(
            subject=_context()
        )
