# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF Retriever interface.
#
# Responsibilities:
# - Validate the abstract retrieval boundary.
# - Validate retriever identity and version contracts.
# - Validate representation-kind declaration.
# - Validate bounded incremental retrieval.
# - Validate provider-neutral RetrievalResult output.
# - Validate index and Knowledge provenance preservation.
#
# Must Not:
# - Test concrete retrieval algorithms.
# - Test indexing or representation generation.
# - Treat retrieval candidates as validated Evidence.
# - Test reranking, Evidence, Context, or generation.
# - Test adaptive Retrieval Intelligence.
# - Depend on external RAG or orchestration frameworks.

from collections.abc import Iterator

import pytest

from alhf.rag.representation.contracts.knowledge_representation import (
    RepresentationKind,
)
from alhf.rag.retrieval.contracts.retrieval_result import (
    RetrievalResult,
)
from alhf.rag.retrieval.interfaces.retriever import (
    Retriever,
)


class StubRetriever(Retriever):
    """Minimal concrete retriever for interface testing."""

    @property
    def retriever_ref(self) -> str:
        return "stub-lexical-retriever"

    @property
    def retriever_version(self) -> str:
        return "1.0"

    @property
    def representation_kind(self) -> RepresentationKind:
        return RepresentationKind.LEXICAL

    def retrieve(
        self,
        *,
        query: str,
        index_ref: str,
        index_version: str,
        limit: int,
    ):
        del query, limit

        yield RetrievalResult(
            representation_ref="representation-001",
            representation_kind=self.representation_kind,
            knowledge_unit_ref="unit-001",
            derivation_id="derivation-001",
            knowledge_scope_ref="scope-001",
            resource_ref="resource-001",
            revision_ref="revision-001",
            index_ref=index_ref,
            index_version=index_version,
            score=1.0,
            rank=1,
        )


class MissingRetrieveRetriever(Retriever):
    """Invalid retriever intentionally missing retrieval behavior."""

    @property
    def retriever_ref(self) -> str:
        return "missing-retrieve"

    @property
    def retriever_version(self) -> str:
        return "1.0"

    @property
    def representation_kind(self) -> RepresentationKind:
        return RepresentationKind.LEXICAL


def _retriever() -> StubRetriever:
    return StubRetriever()


def _retrieve():
    return _retriever().retrieve(
        query="enterprise",
        index_ref="knowledge-index",
        index_version="v1",
        limit=5,
    )


def test_retriever_is_abstract() -> None:
    with pytest.raises(TypeError):
        Retriever()


def test_missing_retrieve_prevents_instantiation() -> None:
    with pytest.raises(TypeError):
        MissingRetrieveRetriever()


def test_concrete_retriever_can_be_instantiated() -> None:
    assert isinstance(
        _retriever(),
        Retriever,
    )


def test_retriever_exposes_stable_reference() -> None:
    assert _retriever().retriever_ref == (
        "stub-lexical-retriever"
    )


def test_retriever_exposes_stable_version() -> None:
    assert _retriever().retriever_version == "1.0"


def test_retriever_exposes_representation_kind() -> None:
    assert _retriever().representation_kind == (
        RepresentationKind.LEXICAL
    )


def test_retrieve_returns_iterator() -> None:
    assert isinstance(
        _retrieve(),
        Iterator,
    )


def test_retrieve_yields_retrieval_result() -> None:
    results = tuple(
        _retrieve()
    )

    assert len(results) == 1
    assert isinstance(
        results[0],
        RetrievalResult,
    )


def test_retrieve_preserves_index_identity() -> None:
    result = next(
        _retrieve()
    )

    assert result.index_ref == "knowledge-index"
    assert result.index_version == "v1"


def test_retrieve_preserves_representation_kind() -> None:
    result = next(
        _retrieve()
    )

    assert result.representation_kind == (
        RepresentationKind.LEXICAL
    )


def test_retrieve_preserves_knowledge_provenance() -> None:
    result = next(
        _retrieve()
    )

    assert result.knowledge_unit_ref == "unit-001"
    assert result.derivation_id == "derivation-001"
    assert result.knowledge_scope_ref == "scope-001"
    assert result.resource_ref == "resource-001"
    assert result.revision_ref == "revision-001"


def test_retrieve_preserves_rank_and_score() -> None:
    result = next(
        _retrieve()
    )

    assert result.score == 1.0
    assert result.rank == 1
