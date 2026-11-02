# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF IndexRegistry interface.
#
# Responsibilities:
# - Validate the abstract index-registry boundary.
# - Validate logical index-reference resolution.
# - Validate index-provider availability checks.
# - Validate configured provider preservation.
# - Validate unknown index behavior.
#
# Must Not:
# - Test physical index persistence.
# - Test concrete vector databases or search engines.
# - Test representation generation or retrieval.
# - Test Index Intelligence or provider selection.
# - Test concurrency, batching, or NFT execution policy.
# - Depend on external RAG or orchestration frameworks.

import pytest

from alhf.rag.indexing.interfaces.index_provider import (
    IndexProvider,
)
from alhf.rag.indexing.interfaces.index_registry import (
    IndexRegistry,
)
from alhf.rag.representation.contracts.knowledge_representation import (
    KnowledgeRepresentation,
)


class StubIndexProvider(IndexProvider):
    """Minimal concrete provider for registry tests."""

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


class StubIndexRegistry(IndexRegistry):
    """Minimal concrete registry for interface tests."""

    def __init__(
        self,
        *,
        index_ref: str,
        provider: IndexProvider,
    ) -> None:
        self._index_ref = index_ref
        self._provider = provider

    def resolve(
        self,
        index_ref: str,
    ) -> object:
        if index_ref != self._index_ref:
            raise LookupError(
                f"index provider not found: {index_ref}"
            )

        return self._provider

    def contains(
        self,
        index_ref: str,
    ) -> bool:
        return index_ref == self._index_ref


class MissingResolveRegistry(IndexRegistry):
    """Registry intentionally missing resolve behavior."""

    def contains(
        self,
        index_ref: str,
    ) -> bool:
        return False


class MissingContainsRegistry(IndexRegistry):
    """Registry intentionally missing contains behavior."""

    def resolve(
        self,
        index_ref: str,
    ) -> object:
        return StubIndexProvider()


def _provider() -> StubIndexProvider:
    return StubIndexProvider()


def _registry() -> StubIndexRegistry:
    return StubIndexRegistry(
        index_ref="knowledge-index",
        provider=_provider(),
    )


def test_index_registry_is_abstract() -> None:
    with pytest.raises(TypeError):
        IndexRegistry()


def test_missing_resolve_prevents_instantiation() -> None:
    with pytest.raises(TypeError):
        MissingResolveRegistry()


def test_missing_contains_prevents_instantiation() -> None:
    with pytest.raises(TypeError):
        MissingContainsRegistry()


def test_concrete_registry_can_be_instantiated() -> None:
    assert isinstance(
        _registry(),
        IndexRegistry,
    )


def test_resolve_returns_index_provider() -> None:
    resolved = _registry().resolve(
        "knowledge-index"
    )

    assert isinstance(
        resolved,
        IndexProvider,
    )


def test_resolve_returns_configured_provider() -> None:
    provider = _provider()
    registry = StubIndexRegistry(
        index_ref="knowledge-index",
        provider=provider,
    )

    assert registry.resolve(
        "knowledge-index"
    ) is provider


def test_contains_returns_true_for_registered_index() -> None:
    assert _registry().contains(
        "knowledge-index"
    ) is True


def test_contains_returns_false_for_unknown_index() -> None:
    assert _registry().contains(
        "missing-index"
    ) is False


def test_unknown_index_raises_lookup_error() -> None:
    with pytest.raises(
        LookupError,
        match="index provider not found: missing-index",
    ):
        _registry().resolve(
            "missing-index"
        )


def test_registry_preserves_provider_reference() -> None:
    provider = _registry().resolve(
        "knowledge-index"
    )

    assert provider.provider_ref == "stub-index-provider"


def test_registry_preserves_provider_version() -> None:
    provider = _registry().resolve(
        "knowledge-index"
    )

    assert provider.provider_version == "1.0"
