# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Validates the ALHF V1 native path from a governed Knowledge Unit
# through representation generation into indexed searchable state.
#
# Responsibilities:
# - Represent a real text KnowledgeUnit through RepresentationService.
# - Index the resulting KnowledgeRepresentation through IndexingService.
# - Validate Knowledge and derivation provenance across both stages.
# - Validate deterministic representation identity.
# - Validate idempotent indexing behavior.
# - Validate representation removal from searchable state.
#
# Must Not:
# - Test retrieval or ranking behavior.
# - Test external embedding models or vector databases.
# - Test Evidence or Context construction.
# - Test Index or Representation Intelligence.
# - Test concurrency, batching, or NFT execution policy.
# - Depend on external RAG or orchestration frameworks.

from alhf.rag.chunking.contracts.knowledge_unit import (
    KnowledgeUnit,
)
from alhf.rag.indexing.indexing_service import (
    IndexingService,
)
from alhf.rag.indexing.providers.in_memory_index_provider import (
    InMemoryIndexProvider,
)
from alhf.rag.indexing.providers.in_memory_index_registry import (
    InMemoryIndexRegistry,
)
from alhf.rag.ingestion.contracts.canonical_content import (
    CanonicalContentKind,
)
from alhf.rag.ingestion.contracts.resource_identity import (
    ResourceIdentity,
)
from alhf.rag.representation.contracts.knowledge_representation import (
    KnowledgeRepresentation,
    RepresentationKind,
)
from alhf.rag.representation.providers.deterministic_text_representation_provider import (
    DeterministicTextRepresentationProvider,
)
from alhf.rag.representation.providers.in_memory_representation_registry import (
    InMemoryRepresentationRegistry,
)
from alhf.rag.representation.representation_service import (
    RepresentationService,
)


def _unit() -> KnowledgeUnit:
    return KnowledgeUnit(
        unit_id="unit-001",
        identity=ResourceIdentity(
            knowledge_scope_ref="scope-001",
            source_ref="source-001",
            logical_resource_id="resource-001",
            revision_id="revision-001",
        ),
        canonical_artifact_ref="canonical-001",
        derivation_id="derivation-001",
        sequence=0,
        content=b"enterprise knowledge",
        content_kind=CanonicalContentKind.TEXT,
        media_type="text/plain",
        strategy_ref="text-derivation",
        strategy_version="1.0",
    )


def _representation_service() -> RepresentationService:
    registry = InMemoryRepresentationRegistry()
    registry.register(
        DeterministicTextRepresentationProvider()
    )

    return RepresentationService(
        registry=registry,
    )


def _indexing_service(
    provider: InMemoryIndexProvider,
) -> IndexingService:
    registry = InMemoryIndexRegistry()
    registry.register(
        index_ref="knowledge-index",
        provider=provider,
    )

    return IndexingService(
        registry=registry,
    )


def _represent_and_index(
    provider: InMemoryIndexProvider,
) -> KnowledgeRepresentation:
    representation = _representation_service().represent(
        _unit()
    )

    _indexing_service(
        provider
    ).index(
        index_ref="knowledge-index",
        representation=representation,
    )

    return representation


def test_knowledge_unit_reaches_searchable_index_state() -> None:
    provider = InMemoryIndexProvider()

    representation = _represent_and_index(
        provider
    )

    assert representation.representation_id in provider
    assert provider.get(
        representation.representation_id
    ) is representation


def test_round_trip_preserves_knowledge_provenance() -> None:
    provider = InMemoryIndexProvider()

    representation = _represent_and_index(
        provider
    )
    indexed = provider.get(
        representation.representation_id
    )

    assert indexed is not None
    assert indexed.knowledge_unit_ref == "unit-001"
    assert indexed.derivation_id == "derivation-001"
    assert indexed.knowledge_scope_ref == "scope-001"
    assert indexed.resource_ref == "resource-001"
    assert indexed.revision_ref == "revision-001"


def test_round_trip_preserves_representation_semantics() -> None:
    provider = InMemoryIndexProvider()

    representation = _represent_and_index(
        provider
    )
    indexed = provider.get(
        representation.representation_id
    )

    assert indexed is not None
    assert indexed.kind == RepresentationKind.LEXICAL
    assert indexed.payload == b"enterprise knowledge"
    assert indexed.media_type == "text/plain"


def test_round_trip_preserves_provider_identity() -> None:
    provider = InMemoryIndexProvider()

    representation = _represent_and_index(
        provider
    )

    assert representation.strategy_ref == (
        "deterministic-text-representation"
    )
    assert representation.strategy_version == "1.0"


def test_repeated_round_trip_is_idempotent() -> None:
    provider = InMemoryIndexProvider()

    first = _represent_and_index(
        provider
    )
    second = _represent_and_index(
        provider
    )

    assert first.representation_id == second.representation_id
    assert len(provider) == 1


def test_indexed_representation_can_be_enumerated() -> None:
    provider = InMemoryIndexProvider()

    representation = _represent_and_index(
        provider
    )

    assert tuple(
        provider.representations()
    ) == (
        representation,
    )


def test_indexed_representation_can_be_removed() -> None:
    provider = InMemoryIndexProvider()

    representation = _represent_and_index(
        provider
    )

    _indexing_service(
        provider
    ).delete(
        index_ref="knowledge-index",
        representation_id=representation.representation_id,
    )

    assert representation.representation_id not in provider
    assert len(provider) == 0
