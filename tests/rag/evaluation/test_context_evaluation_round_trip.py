# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Validates the ALHF V1 Evidence-to-Context-to-Evaluation round trip.
#
# Responsibilities:
# - Pack governed Evidence into KnowledgeContext.
# - Evaluate the resulting KnowledgeContext deterministically.
# - Preserve Context identity through evaluation.
# - Distinguish populated Context from empty/no-Evidence Context.
# - Validate deterministic evaluation across repeated executions.
#
# Must Not:
# - Claim semantic correctness or groundedness.
# - Measure retrieval precision or recall.
# - Evaluate citation correctness or completeness.
# - Generate answers or invoke an LLM.
# - Implement optimization or self-learning.

from alhf.rag.context_packing.context_packing_service import (
    ContextPackingService,
)
from alhf.rag.context_packing.providers.deterministic_context_packer import (
    DeterministicContextPacker,
)
from alhf.rag.evaluation.contracts.evaluation_result import (
    EvaluationStatus,
)
from alhf.rag.evaluation.evaluation_service import (
    EvaluationService,
)
from alhf.rag.evaluation.providers.deterministic_context_evaluator import (
    DeterministicContextEvaluator,
)
from alhf.rag.evidence.contracts.evidence_item import (
    EvidenceItem,
    EvidenceRelation,
)


def _evidence(
    *,
    evidence_id: str = "evidence-001",
    content: bytes = b"enterprise authentication policy",
    rank: int = 1,
) -> EvidenceItem:
    return EvidenceItem(
        evidence_id=evidence_id,
        representation_ref=f"representation-{rank:03d}",
        knowledge_unit_ref=f"unit-{rank:03d}",
        derivation_id="derivation-001",
        knowledge_scope_ref="scope-001",
        resource_ref="resource-001",
        revision_ref="revision-001",
        content=content,
        media_type="text/plain",
        relation=EvidenceRelation.CANDIDATE,
        retrieval_score=1.0,
        retrieval_rank=rank,
    )


def _packing_service() -> ContextPackingService:
    return ContextPackingService(
        packer=DeterministicContextPacker(),
    )


def _evaluation_service() -> EvaluationService:
    return EvaluationService(
        evaluator=DeterministicContextEvaluator(),
    )


def test_packed_context_reaches_evaluation() -> None:
    context = _packing_service().pack(
        evidence=iter((_evidence(),)),
        knowledge_scope_ref="scope-001",
        max_bytes=1000,
    )

    result = _evaluation_service().evaluate(
        subject=context
    )

    assert result.subject_ref == context.context_id
    assert result.status == EvaluationStatus.PASS
    assert result.score == 1.0


def test_evaluation_preserves_context_identity() -> None:
    context = _packing_service().pack(
        evidence=iter((_evidence(),)),
        knowledge_scope_ref="scope-001",
        max_bytes=1000,
    )

    result = _evaluation_service().evaluate(
        subject=context
    )

    assert result.subject_ref == context.context_id
    assert result.evaluator_ref == (
        "deterministic-context-evaluator"
    )
    assert result.evaluator_version == "1.0"


def test_multiple_evidence_items_produce_passing_context() -> None:
    context = _packing_service().pack(
        evidence=iter(
            (
                _evidence(),
                _evidence(
                    evidence_id="evidence-002",
                    content=b"enterprise travel policy",
                    rank=2,
                ),
            )
        ),
        knowledge_scope_ref="scope-001",
        max_bytes=1000,
    )

    result = _evaluation_service().evaluate(
        subject=context
    )

    assert context.evidence_count == 2
    assert result.status == EvaluationStatus.PASS


def test_empty_evidence_context_is_inconclusive() -> None:
    context = _packing_service().pack(
        evidence=iter(()),
        knowledge_scope_ref="scope-001",
        max_bytes=1000,
    )

    result = _evaluation_service().evaluate(
        subject=context
    )

    assert context.evidence_count == 0
    assert context.content == b""
    assert result.status == EvaluationStatus.INCONCLUSIVE
    assert result.score == 0.0


def test_oversized_first_evidence_is_inconclusive() -> None:
    context = _packing_service().pack(
        evidence=iter(
            (
                _evidence(
                    content=b"oversized",
                ),
            )
        ),
        knowledge_scope_ref="scope-001",
        max_bytes=3,
    )

    result = _evaluation_service().evaluate(
        subject=context
    )

    assert context.evidence_count == 0
    assert result.status == EvaluationStatus.INCONCLUSIVE


def test_context_evaluation_round_trip_is_deterministic() -> None:
    def run():
        context = _packing_service().pack(
            evidence=iter((_evidence(),)),
            knowledge_scope_ref="scope-001",
            max_bytes=1000,
        )

        return _evaluation_service().evaluate(
            subject=context
        )

    first = run()
    second = run()

    assert first == second
    assert first.evaluation_id == second.evaluation_id
