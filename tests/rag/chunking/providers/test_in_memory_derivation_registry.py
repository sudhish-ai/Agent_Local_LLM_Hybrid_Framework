# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF InMemoryDerivationRegistry provider.
#
# Responsibilities:
# - Validate derivation-strategy registration.
# - Validate strategy resolution for canonical Knowledge.
# - Validate strategy availability checks.
# - Validate deterministic registration-order selection.
# - Validate duplicate strategy-reference rejection.
# - Validate unsupported canonical-content behavior.
# - Validate registry membership and size semantics.
#
# Must Not:
# - Test concrete derivation algorithms.
# - Test acquisition, parsing, or normalization.
# - Test embedding, indexing, retrieval, or reranking.
# - Test North-Star Derivation Intelligence.
# - Test adaptive strategy selection.
# - Test concurrency or NFT execution strategies.
# - Test Standard RAG, GraphRAG, or Agentic RAG behavior.

import pytest

from alhf.rag.chunking.contracts.knowledge_unit import (
    KnowledgeUnit,
)
from alhf.rag.chunking.interfaces.derivation_strategy import (
    DerivationStrategy,
)
from alhf.rag.chunking.providers.in_memory_derivation_registry import (
    InMemoryDerivationRegistry,
)
from alhf.rag.ingestion.contracts.canonical_content import (
    CanonicalContent,
    CanonicalContentKind,
)
from alhf.rag.ingestion.contracts.resource_identity import (
    ResourceIdentity,
)


class StubDerivationStrategy(DerivationStrategy):
    """Configurable strategy used for registry testing."""

    def __init__(
        self,
        *,
        strategy_ref: str,
        content_kind: CanonicalContentKind,
    ) -> None:
        self._strategy_ref = strategy_ref
        self._content_kind = content_kind

    @property
    def strategy_ref(self) -> str:
        return self._strategy_ref

    @property
    def strategy_version(self) -> str:
        return "1.0"

    def supports(
        self,
        content: CanonicalContent,
    ) -> bool:
        return content.content_kind == self._content_kind

    def derive(
        self,
        content: CanonicalContent,
    ):
        return iter(())


def _content(
    content_kind: CanonicalContentKind = CanonicalContentKind.TEXT,
) -> CanonicalContent:
    return CanonicalContent(
        identity=ResourceIdentity(
            knowledge_scope_ref="scope-001",
            source_ref="source-001",
            logical_resource_id="resource-001",
            revision_id="revision-001",
        ),
        content=b"canonical knowledge",
        content_kind=content_kind,
        media_type="text/plain",
        parsed_artifact_ref="parsed-001",
        normalizer_ref="normalizer-001",
        normalizer_version="1.0",
    )


def _strategy(
    strategy_ref: str = "text-derivation",
    content_kind: CanonicalContentKind = CanonicalContentKind.TEXT,
) -> StubDerivationStrategy:
    return StubDerivationStrategy(
        strategy_ref=strategy_ref,
        content_kind=content_kind,
    )


def test_create_empty_registry() -> None:
    registry = InMemoryDerivationRegistry()

    assert len(registry) == 0


def test_register_strategy() -> None:
    registry = InMemoryDerivationRegistry()

    registry.register(
        _strategy()
    )

    assert len(registry) == 1


def test_resolve_returns_registered_strategy() -> None:
    registry = InMemoryDerivationRegistry()
    strategy = _strategy()

    registry.register(
        strategy
    )

    resolved = registry.resolve(
        _content()
    )

    assert resolved is strategy


def test_contains_supported_content() -> None:
    registry = InMemoryDerivationRegistry()

    registry.register(
        _strategy()
    )

    assert registry.contains(
        _content()
    ) is True


def test_contains_unsupported_content() -> None:
    registry = InMemoryDerivationRegistry()

    registry.register(
        _strategy()
    )

    assert registry.contains(
        _content(
            CanonicalContentKind.STRUCTURED
        )
    ) is False


def test_unsupported_content_raises_lookup_error() -> None:
    registry = InMemoryDerivationRegistry()

    registry.register(
        _strategy()
    )

    with pytest.raises(
        LookupError,
        match="derivation strategy not found",
    ):
        registry.resolve(
            _content(
                CanonicalContentKind.STRUCTURED
            )
        )


def test_multiple_strategies_resolve_independently() -> None:
    registry = InMemoryDerivationRegistry()

    text_strategy = _strategy(
        "text-derivation",
        CanonicalContentKind.TEXT,
    )
    table_strategy = _strategy(
        "table-derivation",
        CanonicalContentKind.TABULAR,
    )

    registry.register(
        text_strategy
    )
    registry.register(
        table_strategy
    )

    assert registry.resolve(
        _content(
            CanonicalContentKind.TEXT
        )
    ) is text_strategy

    assert registry.resolve(
        _content(
            CanonicalContentKind.TABULAR
        )
    ) is table_strategy


def test_first_compatible_strategy_is_selected() -> None:
    registry = InMemoryDerivationRegistry()

    first = _strategy(
        "first-text-derivation",
    )
    second = _strategy(
        "second-text-derivation",
    )

    registry.register(
        first
    )
    registry.register(
        second
    )

    resolved = registry.resolve(
        _content()
    )

    assert resolved is first


def test_duplicate_strategy_reference_is_rejected() -> None:
    registry = InMemoryDerivationRegistry()

    registry.register(
        _strategy()
    )

    with pytest.raises(
        ValueError,
        match="strategy already registered: text-derivation",
    ):
        registry.register(
            _strategy()
        )


def test_invalid_strategy_is_rejected() -> None:
    registry = InMemoryDerivationRegistry()

    with pytest.raises(
        TypeError,
        match=(
            "strategy must be an instance of "
            "DerivationStrategy"
        ),
    ):
        registry.register(
            "invalid-strategy"
        )


def test_registered_strategy_supports_membership() -> None:
    registry = InMemoryDerivationRegistry()

    registry.register(
        _strategy()
    )

    assert "text-derivation" in registry
    assert "  text-derivation  " in registry


def test_unknown_strategy_is_not_member() -> None:
    registry = InMemoryDerivationRegistry()

    assert "missing-strategy" not in registry


def test_invalid_membership_value_returns_false() -> None:
    registry = InMemoryDerivationRegistry()

    assert 123 not in registry
    assert "   " not in registry


def test_registry_size_tracks_multiple_strategies() -> None:
    registry = InMemoryDerivationRegistry()

    registry.register(
        _strategy(
            "text-derivation",
            CanonicalContentKind.TEXT,
        )
    )
    registry.register(
        _strategy(
            "table-derivation",
            CanonicalContentKind.TABULAR,
        )
    )

    assert len(registry) == 2
