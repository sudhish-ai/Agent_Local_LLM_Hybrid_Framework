# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Validates the ALHF V1 consumer-facing Knowledge query round trip.
#
# Responsibilities:
# - Execute one governed KnowledgeRequest.
# - Retrieve indexed Knowledge.
# - Construct governed Evidence.
# - Pack bounded KnowledgeContext.
# - Evaluate the constructed Context.
# - Validate bounded and no-match behavior.
# - Validate deterministic query execution.
#
# Must Not:
# - Test ingestion or representation generation.
# - Perform semantic or hybrid retrieval.
# - Generate prompts or invoke models.
# - Claim semantic groundedness or completeness.
# - Implement adaptive Knowledge Intelligence.
# - Implement self-learning or promotion.

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


def _service() -> KnowledgeQueryService:
    provider = InMemoryIndexProvider()

    representations = (
        (
            "representation-001",
            "unit-001",
            b"enterprise authentication policy",
        ),
        (
            "representation-002",
            "unit-002",
            b"enterprise travel policy",
        ),
    )

    for representation_id, unit_ref, payload in representations:
        provider.upsert(
            KnowledgeRepresentation(
                representation_id=representation_id,
                knowledge_unit_ref=unit_ref,
                derivation_id="derivation-001",
                knowledge_scope_ref="scope-001",
                resource_ref="resource-001",
                revision_ref="revision-001",
                kind=RepresentationKind.LEXICAL,
                payload=payload,
                media_type="text/plain",
                strategy_ref="deterministic-text-representation",
                strategy_version="1.0",
            )
        )

    return KnowledgeQueryService(
        retrieval_service=RetrievalService(
            retriever=InMemoryLexicalRetriever(
                provider=provider,
            )
        ),
        evidence_service=EvidenceService(
            builder=CandidateEvidenceBuilder(),
            resolve_representation=provider.get,
        ),
        context_packing_service=ContextPackingService(
            packer=DeterministicContextPacker(),
        ),
        evaluation_service=EvaluationService(
            evaluator=DeterministicContextEvaluator(),
        ),
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


def test_request_reaches_context_and_evaluation() -> None:
    context, evaluation = _service().execute(
        request=_request()
    )

    assert context.content == (
        b"enterprise authentication policy"
    )
    assert context.evidence_count == 1
    assert evaluation.subject_ref == context.context_id
    assert evaluation.status == EvaluationStatus.PASS


def test_ranked_multi_match_reaches_context() -> None:
    context, evaluation = _service().execute(
        request=_request(
            query="enterprise policy",
        )
    )

    assert context.content == (
        b"enterprise authentication policy"
        b"\n\n"
        b"enterprise travel policy"
    )
    assert context.evidence_count == 2
    assert evaluation.status == EvaluationStatus.PASS


def test_request_limit_bounds_evidence() -> None:
    context, _ = _service().execute(
        request=_request(
            query="enterprise policy",
            retrieval_limit=1,
        )
    )

    assert context.evidence_count == 1


def test_context_budget_can_produce_inconclusive_result() -> None:
    context, evaluation = _service().execute(
        request=_request(
            max_context_bytes=3,
        )
    )

    assert context.content == b""
    assert context.evidence_refs == ()
    assert evaluation.status == EvaluationStatus.INCONCLUSIVE


def test_no_match_is_inconclusive() -> None:
    context, evaluation = _service().execute(
        request=_request(
            query="nonexistent",
        )
    )

    assert context.content == b""
    assert context.evidence_refs == ()
    assert evaluation.status == EvaluationStatus.INCONCLUSIVE
    assert evaluation.score == 0.0


def test_round_trip_is_deterministic() -> None:
    first = _service().execute(
        request=_request(
            query="enterprise policy",
        )
    )

    second = _service().execute(
        request=_request(
            query="enterprise policy",
        )
    )

    assert first == second
