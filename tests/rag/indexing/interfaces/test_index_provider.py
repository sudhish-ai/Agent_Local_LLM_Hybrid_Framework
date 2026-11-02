# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF IndexProvider interface.
#
# Responsibilities:
# - Validate the abstract indexing-provider boundary.
# - Validate provider identity and version contracts.
# - Validate representation compatibility behavior.
# - Validate idempotent indexing boundary semantics.
# - Validate representation deletion boundary semantics.
# - Protect Knowledge contracts from physical index technology.
#
# Must Not:
# - Test concrete vector databases or search engines.
# - Generate Knowledge representations.
# - Test retrieval, reranking, or context construction.
# - Test Index Intelligence or provider selection.
# - Test batching, concurrency, or NFT execution strategies.
# - Depend on external RAG or orchestration frameworks.

import pytest

from alhf.rag.indexing.interfaces.index_provider import (
    IndexProvider,
)
from alhf.rag.representation.contracts.knowledge_representation import (
    KnowledgeRepresentation,
    RepresentationKind,
)


class StubIndexProvider(IndexProvider):
    """Minimal provider used to validate the indexing boundary."""

    def __init__(self) -> None:
        self.indexed: dict[str, KnowledgeRepresentation] = {}

    @property
    def provider_ref(self) -> str:
        return "stub-index-provider"

    @property
    def provider_version(self) -> str:
        return "1.0"

    def supports(
        self,
        representation: KnowledgeRepresentation,
    ) -> bool:
        return representation.kind == RepresentationKind.LEXICAL

    def upsert(
        self,
        representation: KnowledgeRepresentation,
    ) -> None:
        self.indexed[
            representation.representation_id
        ] = representation

    def delete(
        self,
        representation_id: str,
    ) -> None:
        self.indexed.pop(
            representation_id,
            None,
        )


class MissingUpsertProvider(IndexProvider):
    """Invalid provider intentionally missing upsert behavior."""

    @property
    def provider_ref(self) -> str:
        return "missing-upsert"

    @property
    def provider_version(self) -> str:
        return "1.0"

    def supports(
        self,
        representation: KnowledgeRepresentation,
    ) -> bool:
        return True

    def delete(
        self,
        representation_id: str,
    ) -> None:
        return None


class MissingDeleteProvider(IndexProvider):
    """Invalid provider intentionally missing delete behavior."""

    @property
    def provider_ref(self) -> str:
        return "missing-delete"

    @property
    def provider_version(self) -> str:
        return "1.0"

    def supports(
        self,
        representation: KnowledgeRepresentation,
    ) -> bool:
        return True

    def upsert(
        self,
        representation: KnowledgeRepresentation,
    ) -> None:
        return None


def _representation(
    *,
    kind: RepresentationKind = RepresentationKind.LEXICAL,
) -> KnowledgeRepresentation:
    return KnowledgeRepresentation(
        representation_id="representation-001",
        knowledge_unit_ref="unit-001",
        derivation_id="derivation-001",
        knowledge_scope_ref="scope-001",
        resource_ref="resource-001",
        revision_ref="revision-001",
        kind=kind,
        payload=b"enterprise knowledge",
        media_type="text/plain",
        strategy_ref="deterministic-text-representation",
        strategy_version="1.0",
    )


def test_index_provider_is_abstract() -> None:
    with pytest.raises(TypeError):
        IndexProvider()


def test_missing_upsert_prevents_instantiation() -> None:
    with pytest.raises(TypeError):
        MissingUpsertProvider()


def test_missing_delete_prevents_instantiation() -> None:
    with pytest.raises(TypeError):
        MissingDeleteProvider()


def test_concrete_provider_can_be_instantiated() -> None:
    provider = StubIndexProvider()

    assert isinstance(
        provider,
        IndexProvider,
    )


def test_provider_exposes_stable_reference() -> None:
    provider = StubIndexProvider()

    assert provider.provider_ref == "stub-index-provider"


def test_provider_exposes_stable_version() -> None:
    provider = StubIndexProvider()

    assert provider.provider_version == "1.0"


def test_provider_supports_lexical_representation() -> None:
    provider = StubIndexProvider()

    assert provider.supports(
        _representation()
    ) is True


def test_provider_rejects_unsupported_representation() -> None:
    provider = StubIndexProvider()

    assert provider.supports(
        _representation(
            kind=RepresentationKind.DENSE,
        )
    ) is False


def test_upsert_makes_representation_searchable() -> None:
    provider = StubIndexProvider()
    representation = _representation()

    provider.upsert(
        representation
    )

    assert representation.representation_id in provider.indexed
    assert (
        provider.indexed[representation.representation_id]
        is representation
    )


def test_repeated_upsert_is_idempotent() -> None:
    provider = StubIndexProvider()
    representation = _representation()

    provider.upsert(
        representation
    )
    provider.upsert(
        representation
    )

    assert len(provider.indexed) == 1
    assert provider.indexed[
        representation.representation_id
    ] is representation


def test_delete_removes_representation() -> None:
    provider = StubIndexProvider()
    representation = _representation()

    provider.upsert(
        representation
    )
    provider.delete(
        representation.representation_id
    )

    assert representation.representation_id not in provider.indexed


def test_delete_missing_representation_is_idempotent() -> None:
    provider = StubIndexProvider()

    provider.delete(
        "missing-representation"
    )

    assert provider.indexed == {}


def test_upsert_preserves_representation_identity() -> None:
    provider = StubIndexProvider()
    representation = _representation()

    provider.upsert(
        representation
    )

    stored = provider.indexed[
        representation.representation_id
    ]

    assert stored.representation_id == "representation-001"
    assert stored.knowledge_unit_ref == "unit-001"
    assert stored.derivation_id == "derivation-001"


def test_upsert_preserves_knowledge_provenance() -> None:
    provider = StubIndexProvider()
    representation = _representation()

    provider.upsert(
        representation
    )

    stored = provider.indexed[
        representation.representation_id
    ]

    assert stored.knowledge_scope_ref == "scope-001"
    assert stored.resource_ref == "resource-001"
    assert stored.revision_ref == "revision-001"
