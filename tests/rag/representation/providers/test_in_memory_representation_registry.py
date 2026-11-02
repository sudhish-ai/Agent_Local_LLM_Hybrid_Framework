# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF InMemoryRepresentationRegistry provider.
#
# Responsibilities:
# - Validate representation-provider registration.
# - Validate provider resolution for supported Knowledge Units.
# - Validate provider availability checks.
# - Validate deterministic registration-order resolution.
# - Validate duplicate provider-reference rejection.
# - Validate unsupported Knowledge Unit behavior.
# - Validate registry membership and size semantics.
#
# Must Not:
# - Test concrete embedding models.
# - Test representation generation algorithms.
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
)
from alhf.rag.representation.interfaces.representation_provider import (
    RepresentationProvider,
)
from alhf.rag.representation.providers.in_memory_representation_registry import (
    InMemoryRepresentationRegistry,
)


class StubRepresentationProvider(RepresentationProvider):
    """Configurable provider used for registry testing."""

    def __init__(
        self,
        *,
        provider_ref: str,
        content_kind: CanonicalContentKind,
    ) -> None:
        self._provider_ref = provider_ref
        self._content_kind = content_kind

    @property
    def provider_ref(self) -> str:
        return self._provider_ref

    @property
    def provider_version(self) -> str:
        return "1.0"

    def supports(
        self,
        unit: KnowledgeUnit,
    ) -> bool:
        return unit.content_kind == self._content_kind

    def represent(
        self,
        unit: KnowledgeUnit,
    ) -> KnowledgeRepresentation:
        raise NotImplementedError


def _unit(
    content_kind: CanonicalContentKind = CanonicalContentKind.TEXT,
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
        content=b"enterprise knowledge",
        content_kind=content_kind,
        media_type="text/plain",
        strategy_ref="text-derivation",
        strategy_version="1.0",
    )


def _provider(
    provider_ref: str = "text-provider",
    content_kind: CanonicalContentKind = CanonicalContentKind.TEXT,
) -> StubRepresentationProvider:
    return StubRepresentationProvider(
        provider_ref=provider_ref,
        content_kind=content_kind,
    )


def test_create_empty_registry() -> None:
    registry = InMemoryRepresentationRegistry()

    assert len(registry) == 0


def test_register_provider() -> None:
    registry = InMemoryRepresentationRegistry()

    registry.register(
        _provider()
    )

    assert len(registry) == 1


def test_resolve_returns_registered_provider() -> None:
    registry = InMemoryRepresentationRegistry()
    provider = _provider()

    registry.register(
        provider
    )

    resolved = registry.resolve(
        _unit()
    )

    assert resolved is provider


def test_contains_supported_unit() -> None:
    registry = InMemoryRepresentationRegistry()

    registry.register(
        _provider()
    )

    assert registry.contains(
        _unit()
    ) is True


def test_contains_unsupported_unit() -> None:
    registry = InMemoryRepresentationRegistry()

    registry.register(
        _provider()
    )

    assert registry.contains(
        _unit(
            CanonicalContentKind.STRUCTURED
        )
    ) is False


def test_unsupported_unit_raises_lookup_error() -> None:
    registry = InMemoryRepresentationRegistry()

    registry.register(
        _provider()
    )

    with pytest.raises(
        LookupError,
        match=(
            "representation provider not found for "
            "Knowledge Unit"
        ),
    ):
        registry.resolve(
            _unit(
                CanonicalContentKind.STRUCTURED
            )
        )


def test_multiple_providers_resolve_independently() -> None:
    registry = InMemoryRepresentationRegistry()

    text_provider = _provider(
        "text-provider",
        CanonicalContentKind.TEXT,
    )
    structured_provider = _provider(
        "structured-provider",
        CanonicalContentKind.STRUCTURED,
    )

    registry.register(
        text_provider
    )
    registry.register(
        structured_provider
    )

    assert registry.resolve(
        _unit(
            CanonicalContentKind.TEXT
        )
    ) is text_provider

    assert registry.resolve(
        _unit(
            CanonicalContentKind.STRUCTURED
        )
    ) is structured_provider


def test_first_compatible_provider_is_selected() -> None:
    registry = InMemoryRepresentationRegistry()

    first = _provider(
        "first-text-provider"
    )
    second = _provider(
        "second-text-provider"
    )

    registry.register(
        first
    )
    registry.register(
        second
    )

    assert registry.resolve(
        _unit()
    ) is first


def test_duplicate_provider_reference_is_rejected() -> None:
    registry = InMemoryRepresentationRegistry()

    registry.register(
        _provider()
    )

    with pytest.raises(
        ValueError,
        match="provider already registered: text-provider",
    ):
        registry.register(
            _provider()
        )


def test_invalid_provider_is_rejected() -> None:
    registry = InMemoryRepresentationRegistry()

    with pytest.raises(
        TypeError,
        match=(
            "provider must be an instance of "
            "RepresentationProvider"
        ),
    ):
        registry.register(
            "invalid-provider"
        )


def test_registered_provider_supports_membership() -> None:
    registry = InMemoryRepresentationRegistry()

    registry.register(
        _provider()
    )

    assert "text-provider" in registry
    assert "  text-provider  " in registry


def test_unknown_provider_is_not_member() -> None:
    registry = InMemoryRepresentationRegistry()

    assert "missing-provider" not in registry


def test_invalid_membership_value_returns_false() -> None:
    registry = InMemoryRepresentationRegistry()

    assert 123 not in registry
    assert "   " not in registry


def test_invalid_unit_is_rejected_by_resolve() -> None:
    registry = InMemoryRepresentationRegistry()

    with pytest.raises(
        TypeError,
        match="unit must be an instance of KnowledgeUnit",
    ):
        registry.resolve(
            "invalid-unit"
        )


def test_invalid_unit_is_rejected_by_contains() -> None:
    registry = InMemoryRepresentationRegistry()

    with pytest.raises(
        TypeError,
        match="unit must be an instance of KnowledgeUnit",
    ):
        registry.contains(
            "invalid-unit"
        )


def test_registry_size_tracks_multiple_providers() -> None:
    registry = InMemoryRepresentationRegistry()

    registry.register(
        _provider(
            "text-provider",
            CanonicalContentKind.TEXT,
        )
    )
    registry.register(
        _provider(
            "structured-provider",
            CanonicalContentKind.STRUCTURED,
        )
    )

    assert len(registry) == 2
