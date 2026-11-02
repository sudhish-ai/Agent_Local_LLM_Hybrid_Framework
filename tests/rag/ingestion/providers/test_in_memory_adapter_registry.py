# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF InMemoryAdapterRegistry provider.
#
# Responsibilities:
# - Validate adapter registration.
# - Validate provider-neutral capability registration.
# - Validate adapter resolution by stable reference.
# - Validate capability resolution by stable reference.
# - Validate duplicate-registration rejection.
# - Validate adapter-reference normalization.
# - Validate missing-adapter behavior.
# - Validate registry size and membership semantics.
#
# Must Not:
# - Test plugin loading or dynamic discovery.
# - Test concrete source acquisition.
# - Test provider-specific configuration.
# - Test credentials or connection information.
# - Test synchronization execution.
# - Test parsing, chunking, embedding, indexing, or retrieval.
# - Test Standard RAG, GraphRAG, or Agentic RAG behavior.

import pytest

from alhf.rag.ingestion.contracts.adapter_capabilities import (
    AdapterCapabilities,
)
from alhf.rag.ingestion.contracts.knowledge_source import (
    KnowledgeSource,
)
from alhf.rag.ingestion.interfaces.knowledge_source_adapter import (
    KnowledgeSourceAdapter,
)
from alhf.rag.ingestion.providers.in_memory_adapter_registry import (
    InMemoryAdapterRegistry,
)


class StubKnowledgeSourceAdapter(KnowledgeSourceAdapter):
    """Minimal acquisition adapter used for registry testing."""

    def acquire(
        self,
        source: KnowledgeSource,
    ):
        return iter(())


def _adapter() -> StubKnowledgeSourceAdapter:
    return StubKnowledgeSourceAdapter()


def _capabilities() -> AdapterCapabilities:
    return AdapterCapabilities(
        supports_synchronization=True,
        supports_continuation=True,
        supports_incremental_changes=True,
        supports_deletion_detection=True,
        supports_resume=True,
    )


def test_create_empty_registry() -> None:
    registry = InMemoryAdapterRegistry()

    assert len(registry) == 0


def test_register_adapter() -> None:
    registry = InMemoryAdapterRegistry()

    registry.register(
        adapter_ref="local-file-adapter",
        adapter=_adapter(),
        capabilities=_capabilities(),
    )

    assert len(registry) == 1


def test_resolve_returns_registered_adapter() -> None:
    registry = InMemoryAdapterRegistry()
    adapter = _adapter()

    registry.register(
        adapter_ref="local-file-adapter",
        adapter=adapter,
        capabilities=_capabilities(),
    )

    resolved = registry.resolve(
        "local-file-adapter",
    )

    assert resolved is adapter


def test_capabilities_returns_registered_capabilities() -> None:
    registry = InMemoryAdapterRegistry()
    capabilities = _capabilities()

    registry.register(
        adapter_ref="local-file-adapter",
        adapter=_adapter(),
        capabilities=capabilities,
    )

    resolved = registry.capabilities(
        "local-file-adapter",
    )

    assert resolved is capabilities


def test_adapter_reference_is_normalized() -> None:
    registry = InMemoryAdapterRegistry()
    adapter = _adapter()

    registry.register(
        adapter_ref="  local-file-adapter  ",
        adapter=adapter,
        capabilities=_capabilities(),
    )

    assert registry.resolve(
        "local-file-adapter",
    ) is adapter


def test_resolution_reference_is_normalized() -> None:
    registry = InMemoryAdapterRegistry()
    adapter = _adapter()

    registry.register(
        adapter_ref="local-file-adapter",
        adapter=adapter,
        capabilities=_capabilities(),
    )

    assert registry.resolve(
        "  local-file-adapter  ",
    ) is adapter


def test_duplicate_adapter_reference_is_rejected() -> None:
    registry = InMemoryAdapterRegistry()

    registry.register(
        adapter_ref="local-file-adapter",
        adapter=_adapter(),
        capabilities=_capabilities(),
    )

    with pytest.raises(
        ValueError,
        match="adapter already registered: local-file-adapter",
    ):
        registry.register(
            adapter_ref="local-file-adapter",
            adapter=_adapter(),
            capabilities=_capabilities(),
        )


def test_unknown_adapter_resolution_fails() -> None:
    registry = InMemoryAdapterRegistry()

    with pytest.raises(
        LookupError,
        match="adapter not found: missing-adapter",
    ):
        registry.resolve(
            "missing-adapter",
        )


def test_unknown_adapter_capabilities_fail() -> None:
    registry = InMemoryAdapterRegistry()

    with pytest.raises(
        LookupError,
        match="adapter not found: missing-adapter",
    ):
        registry.capabilities(
            "missing-adapter",
        )


@pytest.mark.parametrize(
    "adapter_ref",
    (
        "",
        "   ",
    ),
)
def test_register_rejects_empty_adapter_reference(
    adapter_ref: str,
) -> None:
    registry = InMemoryAdapterRegistry()

    with pytest.raises(
        ValueError,
        match="adapter_ref cannot be empty",
    ):
        registry.register(
            adapter_ref=adapter_ref,
            adapter=_adapter(),
            capabilities=_capabilities(),
        )


def test_register_rejects_non_string_adapter_reference() -> None:
    registry = InMemoryAdapterRegistry()

    with pytest.raises(
        TypeError,
        match="adapter_ref must be a string",
    ):
        registry.register(
            adapter_ref=123,
            adapter=_adapter(),
            capabilities=_capabilities(),
        )


def test_register_rejects_invalid_adapter() -> None:
    registry = InMemoryAdapterRegistry()

    with pytest.raises(
        TypeError,
        match=(
            "adapter must be an instance of "
            "KnowledgeSourceAdapter"
        ),
    ):
        registry.register(
            adapter_ref="local-file-adapter",
            adapter="invalid-adapter",
            capabilities=_capabilities(),
        )


def test_register_rejects_invalid_capabilities() -> None:
    registry = InMemoryAdapterRegistry()

    with pytest.raises(
        TypeError,
        match=(
            "capabilities must be an instance of "
            "AdapterCapabilities"
        ),
    ):
        registry.register(
            adapter_ref="local-file-adapter",
            adapter=_adapter(),
            capabilities="invalid-capabilities",
        )


def test_registered_adapter_supports_membership() -> None:
    registry = InMemoryAdapterRegistry()

    registry.register(
        adapter_ref="local-file-adapter",
        adapter=_adapter(),
        capabilities=_capabilities(),
    )

    assert "local-file-adapter" in registry
    assert "  local-file-adapter  " in registry


def test_unknown_adapter_is_not_member() -> None:
    registry = InMemoryAdapterRegistry()

    assert "missing-adapter" not in registry


def test_invalid_membership_reference_returns_false() -> None:
    registry = InMemoryAdapterRegistry()

    assert 123 not in registry
    assert "   " not in registry


def test_multiple_adapters_are_independently_resolved() -> None:
    registry = InMemoryAdapterRegistry()
    first_adapter = _adapter()
    second_adapter = _adapter()

    registry.register(
        adapter_ref="adapter-a",
        adapter=first_adapter,
        capabilities=AdapterCapabilities(),
    )
    registry.register(
        adapter_ref="adapter-b",
        adapter=second_adapter,
        capabilities=AdapterCapabilities(
            supports_continuation=True,
        ),
    )

    assert len(registry) == 2
    assert registry.resolve("adapter-a") is first_adapter
    assert registry.resolve("adapter-b") is second_adapter
    assert (
        registry.capabilities(
            "adapter-b"
        ).supports_continuation
        is True
    )
