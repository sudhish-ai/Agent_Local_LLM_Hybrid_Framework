# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF DerivationRegistry interface.
#
# Responsibilities:
# - Validate the abstract derivation-registry boundary.
# - Validate compatible strategy resolution.
# - Validate derivation-strategy availability checks.
# - Validate unsupported canonical-content behavior.
# - Protect dynamic derivation-strategy selection semantics.
# - Protect downstream layers from concrete chunking algorithms.
#
# Must Not:
# - Test physical source acquisition.
# - Test parsing or normalization.
# - Test concrete chunking algorithms.
# - Test embedding, indexing, retrieval, or reranking.
# - Test strategy intelligence or adaptive selection.
# - Test concurrency or NFT execution strategies.
# - Test Standard RAG, GraphRAG, or Agentic RAG behavior.

import pytest

from alhf.rag.chunking.contracts.knowledge_unit import (
    KnowledgeUnit,
)
from alhf.rag.chunking.interfaces.derivation_registry import (
    DerivationRegistry,
)
from alhf.rag.chunking.interfaces.derivation_strategy import (
    DerivationStrategy,
)
from alhf.rag.ingestion.contracts.canonical_content import (
    CanonicalContent,
    CanonicalContentKind,
)
from alhf.rag.ingestion.contracts.resource_identity import (
    ResourceIdentity,
)


class StubDerivationStrategy(DerivationStrategy):
    """Minimal strategy used to validate registry resolution."""

    @property
    def strategy_ref(self) -> str:
        return "text-derivation"

    @property
    def strategy_version(self) -> str:
        return "1.0"

    def supports(
        self,
        content: CanonicalContent,
    ) -> bool:
        return content.content_kind == CanonicalContentKind.TEXT

    def derive(
        self,
        content: CanonicalContent,
    ):
        return iter(())


class StubDerivationRegistry(DerivationRegistry):
    """Minimal registry used to validate the interface contract."""

    def __init__(
        self,
        strategy: DerivationStrategy,
    ) -> None:
        self._strategy = strategy

    def resolve(
        self,
        content: CanonicalContent,
    ) -> DerivationStrategy:
        if not self._strategy.supports(content):
            raise LookupError(
                "derivation strategy not found"
            )

        return self._strategy

    def contains(
        self,
        content: CanonicalContent,
    ) -> bool:
        return self._strategy.supports(content)


class MissingResolveRegistry(DerivationRegistry):
    """Invalid registry missing strategy resolution."""

    def contains(
        self,
        content: CanonicalContent,
    ) -> bool:
        return False


class MissingContainsRegistry(DerivationRegistry):
    """Invalid registry missing availability behavior."""

    def resolve(
        self,
        content: CanonicalContent,
    ) -> DerivationStrategy:
        return StubDerivationStrategy()


def _canonical_content(
    kind: CanonicalContentKind = CanonicalContentKind.TEXT,
) -> CanonicalContent:
    return CanonicalContent(
        identity=ResourceIdentity(
            knowledge_scope_ref="scope-001",
            source_ref="source-001",
            logical_resource_id="resource-001",
            revision_id="revision-001",
        ),
        content=b"canonical knowledge",
        content_kind=kind,
        media_type="text/plain",
        parsed_artifact_ref="parsed-001",
        normalizer_ref="normalizer-001",
        normalizer_version="1.0",
    )


def _registry() -> StubDerivationRegistry:
    return StubDerivationRegistry(
        StubDerivationStrategy()
    )


def test_derivation_registry_is_abstract() -> None:
    with pytest.raises(TypeError):
        DerivationRegistry()


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
        DerivationRegistry,
    )


def test_resolve_returns_derivation_strategy() -> None:
    strategy = _registry().resolve(
        _canonical_content()
    )

    assert isinstance(
        strategy,
        DerivationStrategy,
    )


def test_resolve_returns_configured_strategy() -> None:
    strategy = StubDerivationStrategy()
    registry = StubDerivationRegistry(
        strategy
    )

    resolved = registry.resolve(
        _canonical_content()
    )

    assert resolved is strategy


def test_contains_returns_true_for_supported_content() -> None:
    registry = _registry()

    assert registry.contains(
        _canonical_content()
    ) is True


def test_contains_returns_false_for_unsupported_content() -> None:
    registry = _registry()

    assert registry.contains(
        _canonical_content(
            CanonicalContentKind.STRUCTURED
        )
    ) is False


def test_unsupported_content_raises_lookup_error() -> None:
    registry = _registry()

    with pytest.raises(
        LookupError,
        match="derivation strategy not found",
    ):
        registry.resolve(
            _canonical_content(
                CanonicalContentKind.STRUCTURED
            )
        )


def test_registry_preserves_strategy_identity() -> None:
    strategy = _registry().resolve(
        _canonical_content()
    )

    assert strategy.strategy_ref == "text-derivation"
    assert strategy.strategy_version == "1.0"
