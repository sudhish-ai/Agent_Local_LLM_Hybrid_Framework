# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF RetrievalService.
#
# Responsibilities:
# - Validate bounded retrieval orchestration.
# - Validate Retriever delegation.
# - Validate RetrievalResult integrity.
# - Validate index identity preservation.
# - Validate contiguous ranking.
# - Validate input and provider failures.
#
# Must Not:
# - Test lexical scoring in depth.
# - Test semantic or hybrid retrieval.
# - Treat RetrievalResult as Evidence.
# - Test reranking, Evidence, Context, or generation.
# - Test adaptive Retrieval Intelligence.
# - Depend on external RAG frameworks.

from collections.abc import Iterator

import pytest

from alhf.rag.indexing.providers.in_memory_index_provider import (
    InMemoryIndexProvider,
)
from alhf.rag.representation.contracts.knowledge_representation import (
    KnowledgeRepresentation,
    RepresentationKind,
)
from alhf.rag.retrieval.contracts.retrieval_result import (
    RetrievalResult,
)
from alhf.rag.retrieval.interfaces.retriever import (
    Retriever,
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


def _service() -> RetrievalService:
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
            b"travel booking information",
        )
    )

    return RetrievalService(
        retriever=InMemoryLexicalRetriever(
            provider=provider,
        )
    )


def test_create_retrieval_service() -> None:
    assert isinstance(
        _service(),
        RetrievalService,
    )


def test_retrieve_returns_iterator() -> None:
    results = _service().retrieve(
        query="enterprise",
        index_ref="knowledge-index",
        index_version="v1",
        limit=5,
    )

    assert isinstance(
        results,
        Iterator,
    )


def test_retrieve_returns_matching_result() -> None:
    results = tuple(
        _service().retrieve(
            query="enterprise",
            index_ref="knowledge-index",
            index_version="v1",
            limit=5,
        )
    )

    assert len(results) == 1
    assert isinstance(
        results[0],
        RetrievalResult,
    )
    assert results[0].knowledge_unit_ref == "unit-001"


def test_retrieve_preserves_index_identity() -> None:
    result = next(
        _service().retrieve(
            query="enterprise",
            index_ref="knowledge-index",
            index_version="v1",
            limit=5,
        )
    )

    assert result.index_ref == "knowledge-index"
    assert result.index_version == "v1"


def test_retrieve_preserves_rank() -> None:
    result = next(
        _service().retrieve(
            query="enterprise",
            index_ref="knowledge-index",
            index_version="v1",
            limit=5,
        )
    )

    assert result.rank == 1


def test_no_match_returns_empty_results() -> None:
    results = tuple(
        _service().retrieve(
            query="nonexistent",
            index_ref="knowledge-index",
            index_version="v1",
            limit=5,
        )
    )

    assert results == ()


def test_invalid_retriever_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match="retriever must be an instance of Retriever",
    ):
        RetrievalService(
            retriever="invalid-retriever"
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "query",
        "index_ref",
        "index_version",
    ),
)
def test_empty_required_text_is_rejected(
    field_name: str,
) -> None:
    values = {
        "query": "enterprise",
        "index_ref": "knowledge-index",
        "index_version": "v1",
        "limit": 5,
    }
    values[field_name] = "   "

    with pytest.raises(
        ValueError,
        match=f"{field_name} cannot be empty",
    ):
        tuple(
            _service().retrieve(
                **values
            )
        )


@pytest.mark.parametrize(
    "limit",
    (
        0,
        -1,
    ),
)
def test_non_positive_limit_is_rejected(
    limit: int,
) -> None:
    with pytest.raises(
        ValueError,
        match="limit must be greater than zero",
    ):
        tuple(
            _service().retrieve(
                query="enterprise",
                index_ref="knowledge-index",
                index_version="v1",
                limit=limit,
            )
        )


@pytest.mark.parametrize(
    "limit",
    (
        True,
        1.5,
        "1",
        None,
    ),
)
def test_invalid_limit_type_is_rejected(
    limit: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="limit must be an int",
    ):
        tuple(
            _service().retrieve(
                query="enterprise",
                index_ref="knowledge-index",
                index_version="v1",
                limit=limit,
            )
        )


class NonIteratorRetriever(InMemoryLexicalRetriever):
    """Retriever intentionally violating iterator contract."""

    def retrieve(
        self,
        **kwargs,
    ):
        return ()


def test_non_iterator_retriever_output_is_rejected() -> None:
    provider = InMemoryIndexProvider()

    service = RetrievalService(
        retriever=NonIteratorRetriever(
            provider=provider,
        )
    )

    with pytest.raises(
        TypeError,
        match="retriever must return an Iterator",
    ):
        tuple(
            service.retrieve(
                query="enterprise",
                index_ref="knowledge-index",
                index_version="v1",
                limit=5,
            )
        )
