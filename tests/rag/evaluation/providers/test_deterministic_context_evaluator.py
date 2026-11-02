# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF DeterministicContextEvaluator.
#
# Responsibilities:
# - Validate stable evaluator identity and version.
# - Validate KnowledgeContext compatibility.
# - Validate deterministic PASS evaluation.
# - Validate empty Context as INCONCLUSIVE.
# - Validate evaluation subject identity.
# - Validate deterministic evaluation identity.
# - Validate unsupported subject rejection.
#
# Must Not:
# - Claim semantic correctness or groundedness.
# - Measure retrieval precision or recall.
# - Evaluate citation correctness or completeness.
# - Generate answers or invoke an LLM.
# - Implement optimization or self-learning.
# - Depend on external RAG frameworks.

import pytest

from alhf.rag.context_packing.contracts.knowledge_context import (
    KnowledgeContext,
)
from alhf.rag.evaluation.contracts.evaluation_result import (
    EvaluationResult,
    EvaluationStatus,
)
from alhf.rag.evaluation.providers.deterministic_context_evaluator import (
    DeterministicContextEvaluator,
)


def _context(
    *,
    context_id: str = "context-001",
    evidence_refs: tuple[str, ...] = ("evidence-001",),
    content: bytes = b"enterprise context",
) -> KnowledgeContext:
    return KnowledgeContext(
        context_id=context_id,
        knowledge_scope_ref="scope-001",
        evidence_refs=evidence_refs,
        content=content,
        media_type="text/plain",
        strategy_ref="deterministic-context-packer",
        strategy_version="1.0",
    )


def _evaluator() -> DeterministicContextEvaluator:
    return DeterministicContextEvaluator()


def test_evaluator_exposes_stable_identity() -> None:
    evaluator = _evaluator()

    assert evaluator.evaluator_ref == (
        "deterministic-context-evaluator"
    )
    assert evaluator.evaluator_version == "1.0"


def test_evaluator_supports_knowledge_context() -> None:
    assert _evaluator().supports(
        _context()
    ) is True


def test_evaluator_rejects_unknown_subject() -> None:
    assert _evaluator().supports(
        "invalid-context"
    ) is False


def test_non_empty_context_passes() -> None:
    result = _evaluator().evaluate(
        subject=_context()
    )

    assert isinstance(
        result,
        EvaluationResult,
    )
    assert result.status == EvaluationStatus.PASS
    assert result.score == 1.0
    assert result.reason == (
        "Knowledge Context contains packed Evidence"
    )


def test_evaluation_preserves_context_reference() -> None:
    result = _evaluator().evaluate(
        subject=_context(
            context_id="context-123",
        )
    )

    assert result.subject_ref == "context-123"


def test_evaluation_preserves_evaluator_identity() -> None:
    evaluator = _evaluator()

    result = evaluator.evaluate(
        subject=_context()
    )

    assert result.evaluator_ref == evaluator.evaluator_ref
    assert result.evaluator_version == evaluator.evaluator_version


def test_empty_context_is_inconclusive() -> None:
    result = _evaluator().evaluate(
        subject=_context(
            evidence_refs=(),
            content=b"",
        )
    )

    assert result.status == EvaluationStatus.INCONCLUSIVE
    assert result.score == 0.0
    assert result.reason == (
        "Knowledge Context contains no packed Evidence"
    )


def test_content_without_evidence_is_inconclusive() -> None:
    result = _evaluator().evaluate(
        subject=_context(
            evidence_refs=(),
            content=b"context without Evidence",
        )
    )

    assert result.status == EvaluationStatus.INCONCLUSIVE
    assert result.score == 0.0


def test_evidence_reference_without_content_is_inconclusive() -> None:
    result = _evaluator().evaluate(
        subject=_context(
            evidence_refs=("evidence-001",),
            content=b"",
        )
    )

    assert result.status == EvaluationStatus.INCONCLUSIVE
    assert result.score == 0.0


def test_evaluation_identity_is_deterministic() -> None:
    evaluator = _evaluator()
    context = _context()

    first = evaluator.evaluate(
        subject=context
    )
    second = evaluator.evaluate(
        subject=context
    )

    assert first.evaluation_id == second.evaluation_id
    assert first.evaluation_id.startswith(
        "evaluation:"
    )


def test_different_context_changes_evaluation_identity() -> None:
    evaluator = _evaluator()

    first = evaluator.evaluate(
        subject=_context(
            context_id="context-001",
        )
    )
    second = evaluator.evaluate(
        subject=_context(
            context_id="context-002",
        )
    )

    assert first.evaluation_id != second.evaluation_id


def test_invalid_subject_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "subject must be an instance of KnowledgeContext"
        ),
    ):
        _evaluator().evaluate(
            subject="invalid-context"
        )
