# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF KnowledgeQueryService.
#
# Responsibilities:
# - Validate the V1 Knowledge query orchestration boundary.
# - Validate KnowledgeRequest-driven retrieval.
# - Validate Evidence construction.
# - Validate bounded Context packing.
# - Validate Context evaluation.
# - Validate the deterministic no-match path.
# - Validate invalid orchestration inputs.
#
# Must Not:
# - Test ingestion or indexing.
# - Implement retrieval or Evidence algorithms.
# - Generate prompts or invoke models.
# - Test adaptive Knowledge Intelligence.
# - Implement self-learning or promotion.
# - Depend on external RAG frameworks.

import pytest

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
from alhf.rag.evidence.evidence_service import (
    EvidenceService,
)
from alhf.rag.evidence.providers.candidate_evidence_builder import (
    CandidateEvidenceBuilder,
)
from alhf.rag.indexing.providers.in_memory_index_provider import (
    InMemoryIndexProvider,
)
from alhf.rag.knowledge_request.contracts.knowledge_request import (
    KnowledgeRequest,
)
from alhf.rag.knowledge_request.knowledge_query_service import (
    KnowledgeQueryService,
)
from alhf.rag.representation.contracts.knowledge_representation import (
    KnowledgeRepresentation,
    RepresentationKind,
)
from alhf.rag.retrieval.providers.in_memory_lexical_retriever import (
    InMemoryLexicalRetriever,
)
from alhf.rag.retrieval.retrieval_service import (
    RetrievalService,
)


def _provider() -> InMemoryIndexProvider:
    provider = InMemoryIndexProvider()

    provider.upsert(
        KnowledgeRepresentation(
            representation_id="representation-001",
            knowledge_unit_ref="unit-001",
            derivation_id="derivation-001",
            knowledge_scope_ref="scope-001",
            resource_ref="resource-001",
            revision_ref="revision-001",
            kind=RepresentationKind.LEXICAL,
            payload=b"enterprise authentication policy",
            media_type="text/plain",
            strategy_ref="deterministic-text-representation",
            strategy_version="1.0",
        )
    )

    return provider


def _service() -> KnowledgeQueryService:
    provider = _provider()

    retrieval = RetrievalService(
        retriever=InMemoryLexicalRetriever(
            provider=provider,
        )
    )

    evidence = EvidenceService(
        builder=CandidateEvidenceBuilder(),
        resolve_representation=provider.get,
    )

    packing = ContextPackingService(
        packer=DeterministicContextPacker(),
    )

    evaluation = EvaluationService(
        evaluator=DeterministicContextEvaluator(),
    )

    return KnowledgeQueryService(
        retrieval_service=retrieval,
        evidence_service=evidence,
        context_packing_service=packing,
        evaluation_service=evaluation,
    )


def _request(
    *,
    query: str = "authentication",
    retrieval_limit: int = 5,
    max_context_bytes: int = 4096,
) -> KnowledgeRequest:
    return KnowledgeRequest(
        request_id="request-001",
        knowledge_scope_ref="scope-001",
        query=query,
        index_ref="knowledge-index",
        index_version="v1",
        retrieval_limit=retrieval_limit,
        max_context_bytes=max_context_bytes,
    )


def test_execute_returns_context_and_evaluation() -> None:
    context, evaluation = _service().execute(
        request=_request()
    )

    assert context.content == (
        b"enterprise authentication policy"
    )
    assert context.evidence_count == 1
    assert evaluation.subject_ref == context.context_id


def test_matching_request_passes_evaluation() -> None:
    _, evaluation = _service().execute(
        request=_request()
    )

    assert evaluation.status == EvaluationStatus.PASS
    assert evaluation.score == 1.0


def test_request_retrieval_limit_reaches_pipeline() -> None:
    context, _ = _service().execute(
        request=_request(
            retrieval_limit=1,
        )
    )

    assert context.evidence_count == 1


def test_request_context_limit_reaches_pipeline() -> None:
    context, evaluation = _service().execute(
        request=_request(
            max_context_bytes=3,
        )
    )

    assert context.content == b""
    assert context.evidence_count == 0
    assert evaluation.status == EvaluationStatus.INCONCLUSIVE


def test_no_match_produces_inconclusive_evaluation() -> None:
    context, evaluation = _service().execute(
        request=_request(
            query="nonexistent",
        )
    )

    assert context.content == b""
    assert context.evidence_refs == ()
    assert evaluation.status == EvaluationStatus.INCONCLUSIVE
    assert evaluation.score == 0.0


def test_execution_is_deterministic() -> None:
    request = _request()

    first = _service().execute(
        request=request
    )
    second = _service().execute(
        request=request
    )

    assert first == second


def test_invalid_request_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match="request must be an instance of KnowledgeRequest",
    ):
        _service().execute(
            request="invalid-request"
        )
