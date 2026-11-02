# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF RepresentationRegistry interface.
#
# Responsibilities:
# - Validate the abstract representation-registry boundary.
# - Validate compatible provider resolution.
# - Validate representation-provider availability checks.
# - Validate unsupported Knowledge Unit behavior.
# - Validate configured provider identity preservation.
# - Protect dynamic provider-resolution semantics.
#
# Must Not:
# - Test concrete embedding models.
# - Test vector-store-specific behavior.
# - Test representation generation algorithms.
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
from alhf.rag.representation.interfaces.representation_registry import (
    RepresentationRegistry,
)


class StubRepresentationProvider(RepresentationProvider):
    """Minimal provider used to validate registry resolution."""

    def __init__(
        self,
        *,
        content_kind: CanonicalContentKind,
    ) -> None:
        self._content_kind = content_kind

    @property
    def provider_ref(self) -> str:
        return "stub-provider"

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


class StubRepresentationRegistry(RepresentationRegistry):
    """Minimal registry used to validate the interface contract."""

    def __init__(
        self,
        provider: RepresentationProvider,
    ) -> None:
        self._provider = provider

    def resolve(
        self,
        unit: KnowledgeUnit,
    ) -> RepresentationProvider:
        if not self._provider.supports(unit):
            raise LookupError(
                "representation provider not found"
            )

        return self._provider

    def contains(
        self,
        unit: KnowledgeUnit,
    ) -> bool:
        return self._provider.supports(unit)


class MissingResolveRegistry(RepresentationRegistry):
    """Invalid registry missing provider resolution."""

    def contains(
        self,
        unit: KnowledgeUnit,
    ) -> bool:
        return False


class MissingContainsRegistry(RepresentationRegistry):
    """Invalid registry missing availability behavior."""

    def resolve(
        self,
        unit: KnowledgeUnit,
    ) -> RepresentationProvider:
        return StubRepresentationProvider(
            content_kind=CanonicalContentKind.TEXT,
        )


def _unit(
    *,
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


def _provider() -> StubRepresentationProvider:
    return StubRepresentationProvider(
        content_kind=CanonicalContentKind.TEXT,
    )


def _registry() -> StubRepresentationRegistry:
    return StubRepresentationRegistry(
        _provider()
    )


def test_representation_registry_is_abstract() -> None:
    with pytest.raises(TypeError):
        RepresentationRegistry()


def test_missing_resolve_prevents_instantiation() -> None:
    with pytest.raises(TypeError):
        MissingResolveRegistry()


def test_missing_contains_prevents_instantiation() -> None:
    with pytest.raises(TypeError):
        MissingContainsRegistry()


def test_concrete_registry_can_be_instantiated() -> None:
    registry = _registry()

    assert isinstance(
        registry,
        RepresentationRegistry,
    )


def test_resolve_returns_representation_provider() -> None:
    provider = _registry().resolve(
        _unit()
    )

    assert isinstance(
        provider,
        RepresentationProvider,
    )


def test_resolve_returns_configured_provider() -> None:
    provider = _provider()
    registry = StubRepresentationRegistry(
        provider
    )

    resolved = registry.resolve(
        _unit()
    )

    assert resolved is provider


def test_contains_returns_true_for_supported_unit() -> None:
    registry = _registry()

    assert registry.contains(
        _unit()
    ) is True


def test_contains_returns_false_for_unsupported_unit() -> None:
    registry = _registry()

    assert registry.contains(
        _unit(
            content_kind=CanonicalContentKind.STRUCTURED,
        )
    ) is False


def test_unsupported_unit_raises_lookup_error() -> None:
    registry = _registry()

    with pytest.raises(
        LookupError,
        match="representation provider not found",
    ):
        registry.resolve(
            _unit(
                content_kind=CanonicalContentKind.STRUCTURED,
            )
        )


def test_registry_preserves_provider_reference() -> None:
    provider = _registry().resolve(
        _unit()
    )

    assert provider.provider_ref == "stub-provider"


def test_registry_preserves_provider_version() -> None:
    provider = _registry().resolve(
        _unit()
    )

    assert provider.provider_version == "1.0"
