# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF InMemoryIndexRegistry.
#
# Responsibilities:
# - Validate logical index-provider registration.
# - Validate provider resolution by logical index reference.
# - Validate deterministic provider preservation.
# - Validate duplicate registration rejection.
# - Validate registry membership and size semantics.
# - Validate index and provider identity validation.
#
# Must Not:
# - Test physical index persistence.
# - Test vector databases or search engines.
# - Test representation generation or retrieval.
# - Test Index Intelligence or lifecycle orchestration.
# - Test concurrency, batching, or NFT execution policy.
# - Depend on external RAG or orchestration frameworks.

import pytest

from alhf.rag.indexing.interfaces.index_provider import (
    IndexProvider,
)
from alhf.rag.indexing.providers.in_memory_index_registry import (
    InMemoryIndexRegistry,
)
from alhf.rag.representation.contracts.knowledge_representation import (
    KnowledgeRepresentation,
)


class StubIndexProvider(IndexProvider):
    """Minimal concrete provider for registry testing."""

    def __init__(
        self,
        provider_ref: str = "stub-index-provider",
        provider_version: str = "1.0",
    ) -> None:
        self._provider_ref = provider_ref
        self._provider_version = provider_version

    @property
    def provider_ref(self) -> str:
        return self._provider_ref

    @property
    def provider_version(self) -> str:
        return self._provider_version

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

    def delete(
        self,
        representation_id: str,
    ) -> None:
        return None


def _provider(
    provider_ref: str = "stub-index-provider",
) -> StubIndexProvider:
    return StubIndexProvider(
        provider_ref=provider_ref,
    )


def test_create_empty_registry() -> None:
    registry = InMemoryIndexRegistry()

    assert len(registry) == 0


def test_register_provider() -> None:
    registry = InMemoryIndexRegistry()

    registry.register(
        index_ref="knowledge-index",
        provider=_provider(),
    )

    assert len(registry) == 1


def test_resolve_returns_registered_provider() -> None:
    registry = InMemoryIndexRegistry()
    provider = _provider()

    registry.register(
        index_ref="knowledge-index",
        provider=provider,
    )

    assert registry.resolve(
        "knowledge-index"
    ) is provider


def test_index_reference_is_normalized() -> None:
    registry = InMemoryIndexRegistry()
    provider = _provider()

    registry.register(
        index_ref="  knowledge-index  ",
        provider=provider,
    )

    assert registry.resolve(
        " knowledge-index "
    ) is provider


def test_contains_registered_index() -> None:
    registry = InMemoryIndexRegistry()

    registry.register(
        index_ref="knowledge-index",
        provider=_provider(),
    )

    assert registry.contains(
        "knowledge-index"
    ) is True


def test_contains_unknown_index_returns_false() -> None:
    registry = InMemoryIndexRegistry()

    assert registry.contains(
        "missing-index"
    ) is False


def test_unknown_index_raises_lookup_error() -> None:
    registry = InMemoryIndexRegistry()

    with pytest.raises(
        LookupError,
        match="index provider not found: missing-index",
    ):
        registry.resolve(
            "missing-index"
        )


def test_duplicate_index_reference_is_rejected() -> None:
    registry = InMemoryIndexRegistry()

    registry.register(
        index_ref="knowledge-index",
        provider=_provider(),
    )

    with pytest.raises(
        ValueError,
        match="index already registered: knowledge-index",
    ):
        registry.register(
            index_ref="knowledge-index",
            provider=_provider(
                "second-provider"
            ),
        )


def test_invalid_provider_is_rejected() -> None:
    registry = InMemoryIndexRegistry()

    with pytest.raises(
        TypeError,
        match="provider must be an instance of IndexProvider",
    ):
        registry.register(
            index_ref="knowledge-index",
            provider="invalid-provider",
        )


@pytest.mark.parametrize(
    "index_ref",
    (
        "",
        "   ",
    ),
)
def test_empty_index_reference_is_rejected(
    index_ref: str,
) -> None:
    registry = InMemoryIndexRegistry()

    with pytest.raises(
        ValueError,
        match="index_ref cannot be empty",
    ):
        registry.register(
            index_ref=index_ref,
            provider=_provider(),
        )


def test_non_string_index_reference_is_rejected() -> None:
    registry = InMemoryIndexRegistry()

    with pytest.raises(
        TypeError,
        match="index_ref must be a string",
    ):
        registry.register(
            index_ref=123,
            provider=_provider(),
        )


def test_invalid_provider_reference_is_rejected() -> None:
    registry = InMemoryIndexRegistry()

    with pytest.raises(
        ValueError,
        match="provider_ref cannot be empty",
    ):
        registry.register(
            index_ref="knowledge-index",
            provider=StubIndexProvider(
                provider_ref="   ",
            ),
        )


def test_invalid_provider_version_is_rejected() -> None:
    registry = InMemoryIndexRegistry()

    with pytest.raises(
        ValueError,
        match="provider_version cannot be empty",
    ):
        registry.register(
            index_ref="knowledge-index",
            provider=StubIndexProvider(
                provider_version="   ",
            ),
        )


def test_membership_operator_supports_registered_index() -> None:
    registry = InMemoryIndexRegistry()

    registry.register(
        index_ref="knowledge-index",
        provider=_provider(),
    )

    assert "knowledge-index" in registry
    assert "  knowledge-index  " in registry


def test_membership_operator_handles_invalid_values() -> None:
    registry = InMemoryIndexRegistry()

    assert "missing-index" not in registry
    assert "   " not in registry
    assert 123 not in registry


def test_registry_tracks_multiple_indexes() -> None:
    registry = InMemoryIndexRegistry()

    first = _provider(
        "first-provider"
    )
    second = _provider(
        "second-provider"
    )

    registry.register(
        index_ref="primary-index",
        provider=first,
    )
    registry.register(
        index_ref="secondary-index",
        provider=second,
    )

    assert len(registry) == 2
    assert registry.resolve("primary-index") is first
    assert registry.resolve("secondary-index") is second
