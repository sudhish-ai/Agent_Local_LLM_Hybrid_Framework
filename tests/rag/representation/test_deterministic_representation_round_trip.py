# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Validates the ALHF V1 deterministic representation path from a
# governed Knowledge Unit to provider-neutral KnowledgeRepresentation.
#
# Responsibilities:
# - Register the native deterministic representation provider.
# - Resolve the provider through InMemoryRepresentationRegistry.
# - Produce a real KnowledgeRepresentation from a KnowledgeUnit.
# - Validate representation kind and payload.
# - Validate Knowledge Unit and derivation provenance.
# - Validate Knowledge scope, resource, and revision provenance.
# - Validate deterministic representation identity.
# - Validate provider independence from model-specific behavior.
#
# Must Not:
# - Generate dense embeddings.
# - Test vector-store-specific behavior.
# - Test indexing, retrieval, reranking, or context construction.
# - Test Representation Intelligence or adaptive provider selection.
# - Test external RAG or orchestration frameworks.
# - Test concurrency, batching, or NFT execution strategies.

from alhf.rag.chunking.contracts.knowledge_unit import (
    KnowledgeUnit,
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


def _unit(
    *,
    content: bytes = b"enterprise knowledge",
) -> KnowledgeUnit:
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
        content=content,
        content_kind=CanonicalContentKind.TEXT,
        media_type="text/plain",
        strategy_ref="text-derivation",
        strategy_version="1.0",
    )


def _registry() -> InMemoryRepresentationRegistry:
    registry = InMemoryRepresentationRegistry()

    registry.register(
        DeterministicTextRepresentationProvider()
    )

    return registry


def test_text_unit_reaches_representation_boundary() -> None:
    unit = _unit()

    provider = _registry().resolve(
        unit
    )
    representation = provider.represent(
        unit
    )

    assert isinstance(
        representation,
        KnowledgeRepresentation,
    )

    assert representation.kind == RepresentationKind.LEXICAL
    assert representation.payload == unit.content
    assert representation.media_type == "text/plain"


def test_registry_resolves_native_text_provider() -> None:
    provider = _registry().resolve(
        _unit()
    )

    assert isinstance(
        provider,
        DeterministicTextRepresentationProvider,
    )

    assert provider.provider_ref == (
        "deterministic-text-representation"
    )
    assert provider.provider_version == "1.0"


def test_representation_preserves_unit_provenance() -> None:
    unit = _unit()

    representation = _registry().resolve(
        unit
    ).represent(
        unit
    )

    assert representation.knowledge_unit_ref == unit.unit_id
    assert representation.derivation_id == unit.derivation_id
    assert representation.knowledge_scope_ref == (
        unit.knowledge_scope_ref
    )


def test_representation_preserves_resource_provenance() -> None:
    unit = _unit()

    representation = _registry().resolve(
        unit
    ).represent(
        unit
    )

    assert representation.resource_ref == unit.resource_ref
    assert representation.revision_ref == unit.revision_ref


def test_representation_records_provider_identity() -> None:
    unit = _unit()

    representation = _registry().resolve(
        unit
    ).represent(
        unit
    )

    assert representation.strategy_ref == (
        "deterministic-text-representation"
    )
    assert representation.strategy_version == "1.0"


def test_deterministic_provider_requires_no_model() -> None:
    unit = _unit()

    representation = _registry().resolve(
        unit
    ).represent(
        unit
    )

    assert representation.model_ref is None
    assert representation.model_version is None


def test_same_unit_produces_stable_representation_identity() -> None:
    unit = _unit()
    provider = _registry().resolve(
        unit
    )

    first = provider.represent(
        unit
    )
    second = provider.represent(
        unit
    )

    assert first.representation_id == second.representation_id
    assert first == second


def test_content_change_produces_distinct_unit_representation() -> None:
    provider = DeterministicTextRepresentationProvider()

    first = provider.represent(
        _unit(
            content=b"version one"
        )
    )
    second = provider.represent(
        KnowledgeUnit(
            unit_id="unit-002",
            identity=ResourceIdentity(
                knowledge_scope_ref="scope-001",
                source_ref="source-001",
                logical_resource_id="resource-001",
                revision_id="revision-002",
            ),
            canonical_artifact_ref="canonical-002",
            derivation_id="derivation-002",
            sequence=0,
            content=b"version two",
            content_kind=CanonicalContentKind.TEXT,
            media_type="text/plain",
            strategy_ref="text-derivation",
            strategy_version="1.0",
        )
    )

    assert first.representation_id != second.representation_id
    assert first.revision_ref != second.revision_ref


def test_multiple_units_are_represented_independently() -> None:
    provider = DeterministicTextRepresentationProvider()

    first = provider.represent(
        _unit(
            content=b"knowledge one"
        )
    )

    second_unit = KnowledgeUnit(
        unit_id="unit-002",
        identity=ResourceIdentity(
            knowledge_scope_ref="scope-001",
            source_ref="source-001",
            logical_resource_id="resource-001",
            revision_id="revision-001",
        ),
        canonical_artifact_ref="canonical-001",
        derivation_id="derivation-001",
        sequence=1,
        content=b"knowledge two",
        content_kind=CanonicalContentKind.TEXT,
        media_type="text/plain",
        strategy_ref="text-derivation",
        strategy_version="1.0",
    )

    second = provider.represent(
        second_unit
    )

    assert first.knowledge_unit_ref == "unit-001"
    assert second.knowledge_unit_ref == "unit-002"
    assert first.representation_id != second.representation_id
