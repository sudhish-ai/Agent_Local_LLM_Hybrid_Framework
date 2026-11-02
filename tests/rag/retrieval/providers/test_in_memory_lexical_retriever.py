# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF InMemoryLexicalRetriever.
#
# Responsibilities:
# - Validate stable retriever identity and version.
# - Validate lexical representation compatibility.
# - Validate deterministic lexical scoring.
# - Validate deterministic candidate ranking.
# - Validate bounded retrieval.
# - Validate no-match behavior.
# - Validate Knowledge and index provenance.
# - Validate invalid retrieval inputs.
#
# Must Not:
# - Test semantic or embedding retrieval.
# - Test reranking, Evidence, or Context construction.
# - Test adaptive Retrieval Intelligence.
# - Test GraphRAG or Agentic RAG.
# - Depend on external RAG frameworks.

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
from alhf.rag.retrieval.providers.in_memory_lexical_retriever import (
    InMemoryLexicalRetriever,
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


def _provider() -> InMemoryIndexProvider:
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
            b"authentication policy enterprise security",
        )
    )
    provider.upsert(
        _representation(
            "representation-003",
            "unit-003",
            b"unrelated travel booking information",
        )
    )

    return provider


def _retriever() -> InMemoryLexicalRetriever:
    return InMemoryLexicalRetriever(
        provider=_provider(),
    )


def _results(
    query: str = "enterprise authentication",
    limit: int = 5,
):
    return tuple(
        _retriever().retrieve(
            query=query,
            index_ref="knowledge-index",
            index_version="v1",
            limit=limit,
        )
    )


def test_retriever_exposes_stable_identity() -> None:
    retriever = _retriever()

    assert retriever.retriever_ref == (
        "in-memory-lexical-retriever"
    )
    assert retriever.retriever_version == "1.0"


def test_retriever_uses_lexical_representation() -> None:
    assert _retriever().representation_kind == (
        RepresentationKind.LEXICAL
    )


def test_retrieve_returns_retrieval_results() -> None:
    results = _results()

    assert results
    assert all(
        isinstance(result, RetrievalResult)
        for result in results
    )


def test_retrieve_matches_query_terms() -> None:
    results = _results(
        query="enterprise authentication",
    )

    assert len(results) == 2

    assert {
        result.knowledge_unit_ref
        for result in results
    } == {
        "unit-001",
        "unit-002",
    }


def test_retrieve_excludes_unmatched_content() -> None:
    results = _results(
        query="enterprise authentication",
    )

    assert all(
        result.knowledge_unit_ref != "unit-003"
        for result in results
    )


def test_complete_term_match_scores_one() -> None:
    results = _results(
        query="enterprise authentication",
    )

    assert all(
        result.score == 1.0
        for result in results
    )


def test_partial_match_has_fractional_score() -> None:
    results = _results(
        query="enterprise missing",
    )

    assert results
    assert results[0].score == 0.5


def test_results_have_one_based_rank() -> None:
    results = _results()

    assert tuple(
        result.rank
        for result in results
    ) == (
        1,
        2,
    )


def test_equal_scores_use_deterministic_identity_order() -> None:
    results = _results()

    assert tuple(
        result.representation_ref
        for result in results
    ) == (
        "representation-001",
        "representation-002",
    )


def test_limit_bounds_results() -> None:
    results = _results(
        limit=1,
    )

    assert len(results) == 1
    assert results[0].rank == 1


def test_no_match_returns_empty_result() -> None:
    results = _results(
        query="nonexistent",
    )

    assert results == ()


def test_result_preserves_index_identity() -> None:
    result = _results(
        limit=1,
    )[0]

    assert result.index_ref == "knowledge-index"
    assert result.index_version == "v1"


def test_result_preserves_knowledge_provenance() -> None:
    result = _results(
        limit=1,
    )[0]

    assert result.derivation_id == "derivation-001"
    assert result.knowledge_scope_ref == "scope-001"
    assert result.resource_ref == "resource-001"
    assert result.revision_ref == "revision-001"


def test_invalid_provider_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "provider must be an instance of "
            "InMemoryIndexProvider"
        ),
    ):
        InMemoryLexicalRetriever(
            provider="invalid-provider"
        )


@pytest.mark.parametrize(
    "query",
    (
        "",
        "   ",
    ),
)
def test_empty_query_is_rejected(
    query: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="query cannot be empty",
    ):
        _results(
            query=query,
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
        _results(
            limit=limit,
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
        _results(
            limit=limit,
        )


def test_invalid_index_reference_is_rejected() -> None:
    retriever = _retriever()

    with pytest.raises(
        ValueError,
        match="index_ref cannot be empty",
    ):
        tuple(
            retriever.retrieve(
                query="enterprise",
                index_ref="   ",
                index_version="v1",
                limit=5,
            )
        )


def test_invalid_index_version_is_rejected() -> None:
    retriever = _retriever()

    with pytest.raises(
        ValueError,
        match="index_version cannot be empty",
    ):
        tuple(
            retriever.retrieve(
                query="enterprise",
                index_ref="knowledge-index",
                index_version="   ",
                limit=5,
            )
        )
