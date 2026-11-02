# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Validates the ALHF V1 native lexical retrieval round trip.
#
# Responsibilities:
# - Index provider-neutral lexical representations.
# - Retrieve indexed Knowledge through RetrievalService.
# - Validate deterministic lexical ranking.
# - Validate bounded retrieval.
# - Validate Knowledge and index provenance.
# - Validate no-match behavior.
# - Validate deletion removes searchable Knowledge.
#
# Must Not:
# - Test semantic or embedding retrieval.
# - Treat RetrievalResult as validated Evidence.
# - Test Evidence, Context, or generation.
# - Test adaptive Retrieval Intelligence.
# - Test GraphRAG or Agentic RAG.
# - Depend on external RAG frameworks.

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
            b"enterprise travel policy",
        )
    )
    provider.upsert(
        _representation(
            "representation-003",
            "unit-003",
            b"healthcare appointment booking",
        )
    )

    service = RetrievalService(
        retriever=InMemoryLexicalRetriever(
            provider=provider,
        )
    )

    return provider, service


def test_indexed_representation_is_retrievable() -> None:
    _, service = _pipeline()

    results = tuple(
        service.retrieve(
            query="authentication",
            index_ref="knowledge-index",
            index_version="v1",
            limit=5,
        )
    )

    assert len(results) == 1
    assert results[0].representation_ref == "representation-001"
    assert results[0].knowledge_unit_ref == "unit-001"


def test_retrieval_preserves_index_identity() -> None:
    _, service = _pipeline()

    result = next(
        service.retrieve(
            query="authentication",
            index_ref="knowledge-index",
            index_version="v1",
            limit=5,
        )
    )

    assert result.index_ref == "knowledge-index"
    assert result.index_version == "v1"


def test_retrieval_preserves_knowledge_provenance() -> None:
    _, service = _pipeline()

    result = next(
        service.retrieve(
            query="authentication",
            index_ref="knowledge-index",
            index_version="v1",
            limit=5,
        )
    )

    assert result.knowledge_unit_ref == "unit-001"
    assert result.derivation_id == "derivation-001"
    assert result.knowledge_scope_ref == "scope-001"
    assert result.resource_ref == "resource-001"
    assert result.revision_ref == "revision-001"


def test_more_complete_match_ranks_first() -> None:
    _, service = _pipeline()

    results = tuple(
        service.retrieve(
            query="enterprise authentication",
            index_ref="knowledge-index",
            index_version="v1",
            limit=5,
        )
    )

    assert results[0].representation_ref == "representation-001"
    assert results[0].score == 1.0
    assert results[0].rank == 1


def test_retrieval_limit_is_enforced() -> None:
    _, service = _pipeline()

    results = tuple(
        service.retrieve(
            query="enterprise policy",
            index_ref="knowledge-index",
            index_version="v1",
            limit=1,
        )
    )

    assert len(results) == 1
    assert results[0].rank == 1


def test_no_match_returns_empty_results() -> None:
    _, service = _pipeline()

    results = tuple(
        service.retrieve(
            query="nonexistent",
            index_ref="knowledge-index",
            index_version="v1",
            limit=5,
        )
    )

    assert results == ()


def test_deletion_removes_representation_from_retrieval() -> None:
    provider, service = _pipeline()

    provider.delete(
        "representation-001"
    )

    results = tuple(
        service.retrieve(
            query="authentication",
            index_ref="knowledge-index",
            index_version="v1",
            limit=5,
        )
    )

    assert results == ()


def test_retrieval_results_are_deterministic() -> None:
    _, service = _pipeline()

    first = tuple(
        service.retrieve(
            query="enterprise policy",
            index_ref="knowledge-index",
            index_version="v1",
            limit=5,
        )
    )
    second = tuple(
        service.retrieve(
            query="enterprise policy",
            index_ref="knowledge-index",
            index_version="v1",
            limit=5,
        )
    )

    assert first == second
