# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Validates the ALHF V1 retrieval-to-Evidence round trip.
#
# Responsibilities:
# - Retrieve indexed lexical Knowledge.
# - Resolve originating KnowledgeRepresentation artifacts.
# - Construct governed candidate Evidence.
# - Validate content and provenance continuity.
# - Validate retrieval score and rank preservation.
# - Validate deterministic Evidence construction.
# - Validate no-match behavior.
#
# Must Not:
# - Test semantic or embedding retrieval.
# - Treat candidate Evidence as verified support.
# - Determine Evidence sufficiency.
# - Resolve Evidence conflicts.
# - Construct Context or generate answers.
# - Test Evidence Intelligence.
# - Depend on external RAG frameworks.

from alhf.rag.evidence.contracts.evidence_item import (
    EvidenceItem,
    EvidenceRelation,
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


def _representation(
    representation_id: str,
    unit_ref: str,
    payload: bytes,
) -> KnowledgeRepresentation:
    return KnowledgeRepresentation(
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


def _pipeline():
    provider = InMemoryIndexProvider()

    provider.upsert(
        _representation(
            "representation-001",
            "unit-001",
            b"enterprise authentication policy",
        )
    )
    provider.upsert(
        _representation(
            "representation-002",
            "unit-002",
            b"travel booking policy",
        )
    )

    retrieval = RetrievalService(
        retriever=InMemoryLexicalRetriever(
            provider=provider,
        )
    )

    evidence = EvidenceService(
        builder=CandidateEvidenceBuilder(),
        resolve_representation=provider.get,
    )

    return retrieval, evidence


def test_retrieval_results_reach_evidence_layer() -> None:
    retrieval, evidence = _pipeline()

    results = retrieval.retrieve(
        query="authentication",
        index_ref="knowledge-index",
        index_version="v1",
        limit=5,
    )

    items = tuple(
        evidence.build_many(
            results=results
        )
    )

    assert len(items) == 1
    assert isinstance(
        items[0],
        EvidenceItem,
    )
    assert items[0].relation == EvidenceRelation.CANDIDATE


def test_evidence_preserves_retrieved_content() -> None:
    retrieval, evidence = _pipeline()

    result = next(
        retrieval.retrieve(
            query="authentication",
            index_ref="knowledge-index",
            index_version="v1",
            limit=5,
        )
    )

    item = evidence.build(
        result=result
    )

    assert item.content == b"enterprise authentication policy"
    assert item.representation_ref == result.representation_ref
    assert item.knowledge_unit_ref == result.knowledge_unit_ref


def test_evidence_preserves_knowledge_provenance() -> None:
    retrieval, evidence = _pipeline()

    result = next(
        retrieval.retrieve(
            query="authentication",
            index_ref="knowledge-index",
            index_version="v1",
            limit=5,
        )
    )

    item = evidence.build(
        result=result
    )

    assert item.derivation_id == result.derivation_id
    assert item.knowledge_scope_ref == result.knowledge_scope_ref
    assert item.resource_ref == result.resource_ref
    assert item.revision_ref == result.revision_ref


def test_evidence_preserves_retrieval_rank_and_score() -> None:
    retrieval, evidence = _pipeline()

    result = next(
        retrieval.retrieve(
            query="authentication",
            index_ref="knowledge-index",
            index_version="v1",
            limit=5,
        )
    )

    item = evidence.build(
        result=result
    )

    assert item.retrieval_rank == result.rank
    assert item.retrieval_score == result.score


def test_no_retrieval_match_produces_no_evidence() -> None:
    retrieval, evidence = _pipeline()

    results = retrieval.retrieve(
        query="nonexistent",
        index_ref="knowledge-index",
        index_version="v1",
        limit=5,
    )

    items = tuple(
        evidence.build_many(
            results=results
        )
    )

    assert items == ()


def test_retrieval_to_evidence_is_deterministic() -> None:
    retrieval, evidence = _pipeline()

    first = tuple(
        evidence.build_many(
            results=retrieval.retrieve(
                query="policy",
                index_ref="knowledge-index",
                index_version="v1",
                limit=5,
            )
        )
    )

    second = tuple(
        evidence.build_many(
            results=retrieval.retrieve(
                query="policy",
                index_ref="knowledge-index",
                index_version="v1",
                limit=5,
            )
        )
    )

    assert first == second
