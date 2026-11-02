# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF AdapterRegistry interface.
#
# Responsibilities:
# - Validate the abstract adapter-registry boundary.
# - Validate acquisition adapter resolution.
# - Validate adapter capability resolution.
# - Validate missing-adapter behavior.
# - Protect provider-neutral adapter discovery semantics.
# - Validate resolved adapters against the acquisition interface.
#
# Must Not:
# - Test concrete plugin loading.
# - Test provider-specific registration.
# - Test physical source acquisition.
# - Test synchronization execution.
# - Test credentials or provider configuration.
# - Test parsing, chunking, embedding, indexing, or retrieval.
# - Test Standard RAG, GraphRAG, or Agentic RAG behavior.

import pytest

from alhf.rag.ingestion.contracts.adapter_capabilities import (
    AdapterCapabilities,
)
from alhf.rag.ingestion.contracts.knowledge_source import (
    KnowledgeSource,
)
from alhf.rag.ingestion.interfaces.adapter_registry import (
    AdapterRegistry,
)
from alhf.rag.ingestion.interfaces.knowledge_source_adapter import (
    KnowledgeSourceAdapter,
)


class StubKnowledgeSourceAdapter(KnowledgeSourceAdapter):
    """Minimal adapter used to validate registry resolution."""

    def acquire(
        self,
        source: KnowledgeSource,
    ):
        return iter(())


class StubAdapterRegistry(AdapterRegistry):
    """In-memory registry used to validate the interface contract."""

    def __init__(
        self,
        *,
        adapter_ref: str,
        adapter: KnowledgeSourceAdapter,
        capabilities: AdapterCapabilities,
    ) -> None:
        self._adapter_ref = adapter_ref
        self._adapter = adapter
        self._capabilities = capabilities

    def resolve(
        self,
        adapter_ref: str,
    ) -> KnowledgeSourceAdapter:
        if adapter_ref != self._adapter_ref:
            raise LookupError(
                f"adapter not found: {adapter_ref}"
            )

        return self._adapter

    def capabilities(
        self,
        adapter_ref: str,
    ) -> AdapterCapabilities:
        if adapter_ref != self._adapter_ref:
            raise LookupError(
                f"adapter not found: {adapter_ref}"
            )

        return self._capabilities


class MissingResolveRegistry(AdapterRegistry):
    """Invalid registry missing adapter resolution."""

    def capabilities(
        self,
        adapter_ref: str,
    ) -> AdapterCapabilities:
        return AdapterCapabilities()


class MissingCapabilitiesRegistry(AdapterRegistry):
    """Invalid registry missing capability resolution."""

    def resolve(
        self,
        adapter_ref: str,
    ) -> KnowledgeSourceAdapter:
        return StubKnowledgeSourceAdapter()


def _registry() -> StubAdapterRegistry:
    adapter = StubKnowledgeSourceAdapter()
    capabilities = AdapterCapabilities(
        supports_continuation=True,
        supports_resume=True,
    )

    return StubAdapterRegistry(
        adapter_ref="local-file-adapter",
        adapter=adapter,
        capabilities=capabilities,
    )


def test_adapter_registry_is_abstract() -> None:
    with pytest.raises(TypeError):
        AdapterRegistry()


def test_registry_missing_resolve_cannot_instantiate() -> None:
    with pytest.raises(TypeError):
        MissingResolveRegistry()


def test_registry_missing_capabilities_cannot_instantiate() -> None:
    with pytest.raises(TypeError):
        MissingCapabilitiesRegistry()


def test_concrete_registry_can_be_instantiated() -> None:
    registry = _registry()

    assert isinstance(
        registry,
        AdapterRegistry,
    )


def test_resolve_returns_knowledge_source_adapter() -> None:
    registry = _registry()

    adapter = registry.resolve(
        "local-file-adapter",
    )

    assert isinstance(
        adapter,
        KnowledgeSourceAdapter,
    )


def test_resolve_returns_configured_adapter_instance() -> None:
    adapter = StubKnowledgeSourceAdapter()

    registry = StubAdapterRegistry(
        adapter_ref="local-file-adapter",
        adapter=adapter,
        capabilities=AdapterCapabilities(),
    )

    resolved = registry.resolve(
        "local-file-adapter",
    )

    assert resolved is adapter


def test_capabilities_returns_adapter_capabilities() -> None:
    registry = _registry()

    capabilities = registry.capabilities(
        "local-file-adapter",
    )

    assert isinstance(
        capabilities,
        AdapterCapabilities,
    )


def test_capabilities_preserve_configured_behavior() -> None:
    registry = _registry()

    capabilities = registry.capabilities(
        "local-file-adapter",
    )

    assert capabilities.supports_continuation is True
    assert capabilities.supports_resume is True


def test_resolve_unknown_adapter_raises_lookup_error() -> None:
    registry = _registry()

    with pytest.raises(
        LookupError,
        match="adapter not found: missing-adapter",
    ):
        registry.resolve(
            "missing-adapter",
        )


def test_capabilities_unknown_adapter_raises_lookup_error() -> None:
    registry = _registry()

    with pytest.raises(
        LookupError,
        match="adapter not found: missing-adapter",
    ):
        registry.capabilities(
            "missing-adapter",
        )
