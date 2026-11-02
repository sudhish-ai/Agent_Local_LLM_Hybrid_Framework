# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF RepresentationService.
#
# Responsibilities:
# - Validate dynamic representation-provider resolution.
# - Validate Knowledge Unit representation generation.
# - Validate KnowledgeRepresentation output.
# - Validate Knowledge Unit and derivation provenance continuity.
# - Validate Knowledge scope, resource, and revision continuity.
# - Validate invalid registry and provider behavior.
#
# Must Not:
# - Test concrete embedding models.
# - Test vector-store-specific behavior.
# - Test indexing, retrieval, reranking, or context construction.
# - Test Representation Intelligence or adaptive provider selection.
# - Test concurrency, batching, or NFT execution strategies.
# - Depend on external RAG or orchestration frameworks.

import pytest

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
from alhf.rag.representation.interfaces.representation_provider import (
    RepresentationProvider,
)
from alhf.rag.representation.interfaces.representation_registry import (
    RepresentationRegistry,
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


def _service() -> RepresentationService:
    registry = InMemoryRepresentationRegistry()

    registry.register(
        DeterministicTextRepresentationProvider()
    )

    return RepresentationService(
        registry=registry,
    )


def test_create_representation_service() -> None:
    service = _service()

    assert isinstance(
        service,
        RepresentationService,
    )


def test_represent_returns_knowledge_representation() -> None:
    representation = _service().represent(
        _unit()
    )

    assert isinstance(
        representation,
        KnowledgeRepresentation,
    )


def test_represent_preserves_knowledge_unit_reference() -> None:
    unit = _unit()

    representation = _service().represent(
        unit
    )

    assert representation.knowledge_unit_ref == unit.unit_id


def test_represent_preserves_derivation_identity() -> None:
    unit = _unit()

    representation = _service().represent(
        unit
    )

    assert representation.derivation_id == unit.derivation_id


def test_represent_preserves_knowledge_scope() -> None:
    representation = _service().represent(
        _unit()
    )

    assert representation.knowledge_scope_ref == "scope-001"


def test_represent_preserves_resource_provenance() -> None:
    representation = _service().represent(
        _unit()
    )

    assert representation.resource_ref == "resource-001"
    assert representation.revision_ref == "revision-001"


def test_represent_uses_resolved_provider() -> None:
    representation = _service().represent(
        _unit()
    )

    assert representation.kind == RepresentationKind.LEXICAL
    assert representation.strategy_ref == (
        "deterministic-text-representation"
    )
    assert representation.strategy_version == "1.0"


def test_represent_preserves_deterministic_payload() -> None:
    unit = _unit()

    representation = _service().represent(
        unit
    )

    assert representation.payload == unit.content


def test_invalid_unit_is_rejected() -> None:
    service = _service()

    with pytest.raises(
        TypeError,
        match="unit must be an instance of KnowledgeUnit",
    ):
        service.represent(
            "invalid-unit"
        )


def test_invalid_registry_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "registry must be an instance of "
            "RepresentationRegistry"
        ),
    ):
        RepresentationService(
            registry="invalid-registry"
        )


class InvalidProviderRegistry(RepresentationRegistry):
    """Registry intentionally returning an invalid provider."""

    def resolve(
        self,
        unit: KnowledgeUnit,
    ):
        return "invalid-provider"

    def contains(
        self,
        unit: KnowledgeUnit,
    ) -> bool:
        return True


def test_invalid_registry_provider_is_rejected() -> None:
    service = RepresentationService(
        registry=InvalidProviderRegistry()
    )

    with pytest.raises(
        TypeError,
        match="registry must return RepresentationProvider",
    ):
        service.represent(
            _unit()
        )


class IncompatibleProvider(
    DeterministicTextRepresentationProvider
):
    """Provider intentionally incompatible after resolution."""

    def supports(
        self,
        unit: KnowledgeUnit,
    ) -> bool:
        return False


class IncompatibleProviderRegistry(RepresentationRegistry):
    """Registry intentionally returning incompatible provider."""

    def resolve(
        self,
        unit: KnowledgeUnit,
    ) -> RepresentationProvider:
        return IncompatibleProvider()

    def contains(
        self,
        unit: KnowledgeUnit,
    ) -> bool:
        return True


def test_incompatible_provider_is_rejected() -> None:
    service = RepresentationService(
        registry=IncompatibleProviderRegistry()
    )

    with pytest.raises(
        ValueError,
        match=(
            "resolved provider does not support "
            "Knowledge Unit"
        ),
    ):
        service.represent(
            _unit()
        )
