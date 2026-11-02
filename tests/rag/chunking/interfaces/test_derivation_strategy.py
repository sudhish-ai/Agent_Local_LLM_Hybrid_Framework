# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF DerivationStrategy interface.
#
# Responsibilities:
# - Validate the abstract derivation-strategy boundary.
# - Validate derivation strategy identity and version contracts.
# - Validate canonical-content compatibility declaration.
# - Validate incremental KnowledgeUnit production.
# - Validate ResourceIdentity preservation across derivation.
# - Validate canonical-artifact provenance preservation.
# - Protect downstream layers from concrete chunking algorithms.
#
# Must Not:
# - Test physical source acquisition.
# - Test format-specific parsing or normalization.
# - Test concrete chunking algorithms.
# - Test embedding, indexing, retrieval, or reranking.
# - Materialize an unbounded Knowledge Unit collection.
# - Test concurrency or NFT execution strategies.
# - Test Standard RAG, GraphRAG, or Agentic RAG behavior.

from collections.abc import Iterator

import pytest

from alhf.rag.chunking.contracts.knowledge_unit import (
    KnowledgeUnit,
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
    """Minimal strategy used to validate the derivation boundary."""

    @property
    def strategy_ref(self) -> str:
        return "stub-text-derivation"

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
        yield KnowledgeUnit(
            unit_id="unit-001",
            identity=content.identity,
            canonical_artifact_ref="canonical-001",
            derivation_id="derivation-001",
            sequence=0,
            content=content.content,
            content_kind=content.content_kind,
            media_type=content.media_type,
            strategy_ref=self.strategy_ref,
            strategy_version=self.strategy_version,
        )


class MissingDeriveStrategy(DerivationStrategy):
    """Invalid strategy missing derivation behavior."""

    @property
    def strategy_ref(self) -> str:
        return "missing-derive"

    @property
    def strategy_version(self) -> str:
        return "1.0"

    def supports(
        self,
        content: CanonicalContent,
    ) -> bool:
        return True


class MissingSupportsStrategy(DerivationStrategy):
    """Invalid strategy missing compatibility behavior."""

    @property
    def strategy_ref(self) -> str:
        return "missing-supports"

    @property
    def strategy_version(self) -> str:
        return "1.0"

    def derive(
        self,
        content: CanonicalContent,
    ):
        return iter(())


def _canonical_content() -> CanonicalContent:
    return CanonicalContent(
        identity=ResourceIdentity(
            knowledge_scope_ref="scope-001",
            source_ref="source-001",
            logical_resource_id="resource-001",
            revision_id="revision-001",
        ),
        content=b"canonical enterprise knowledge",
        content_kind=CanonicalContentKind.TEXT,
        media_type="text/plain",
        parsed_artifact_ref="parsed-001",
        normalizer_ref="text-normalizer",
        normalizer_version="1.0",
    )


def test_derivation_strategy_is_abstract() -> None:
    with pytest.raises(TypeError):
        DerivationStrategy()


def test_missing_derive_prevents_instantiation() -> None:
    with pytest.raises(TypeError):
        MissingDeriveStrategy()


def test_missing_supports_prevents_instantiation() -> None:
    with pytest.raises(TypeError):
        MissingSupportsStrategy()


def test_concrete_strategy_can_be_instantiated() -> None:
    strategy = StubDerivationStrategy()

    assert isinstance(
        strategy,
        DerivationStrategy,
    )


def test_strategy_exposes_stable_reference() -> None:
    strategy = StubDerivationStrategy()

    assert strategy.strategy_ref == "stub-text-derivation"


def test_strategy_exposes_stable_version() -> None:
    strategy = StubDerivationStrategy()

    assert strategy.strategy_version == "1.0"


def test_strategy_supports_text_content() -> None:
    strategy = StubDerivationStrategy()

    assert strategy.supports(
        _canonical_content()
    ) is True


def test_derive_returns_iterator() -> None:
    strategy = StubDerivationStrategy()

    units = strategy.derive(
        _canonical_content()
    )

    assert isinstance(
        units,
        Iterator,
    )


def test_derive_yields_knowledge_unit() -> None:
    strategy = StubDerivationStrategy()

    unit = next(
        strategy.derive(
            _canonical_content()
        )
    )

    assert isinstance(
        unit,
        KnowledgeUnit,
    )


def test_derive_preserves_resource_identity() -> None:
    strategy = StubDerivationStrategy()
    canonical = _canonical_content()

    unit = next(
        strategy.derive(
            canonical
        )
    )

    assert unit.identity is canonical.identity
    assert unit.resource_ref == "resource-001"
    assert unit.revision_ref == "revision-001"
    assert unit.knowledge_scope_ref == "scope-001"


def test_derive_preserves_content_semantics() -> None:
    strategy = StubDerivationStrategy()
    canonical = _canonical_content()

    unit = next(
        strategy.derive(
            canonical
        )
    )

    assert unit.content == canonical.content
    assert unit.content_kind == canonical.content_kind
    assert unit.media_type == canonical.media_type


def test_derive_records_strategy_reproducibility() -> None:
    strategy = StubDerivationStrategy()

    unit = next(
        strategy.derive(
            _canonical_content()
        )
    )

    assert unit.strategy_ref == strategy.strategy_ref
    assert unit.strategy_version == strategy.strategy_version


def test_derive_preserves_sequence() -> None:
    strategy = StubDerivationStrategy()

    unit = next(
        strategy.derive(
            _canonical_content()
        )
    )

    assert unit.sequence == 0


def test_derive_preserves_canonical_provenance() -> None:
    strategy = StubDerivationStrategy()

    unit = next(
        strategy.derive(
            _canonical_content()
        )
    )

    assert unit.canonical_artifact_ref == "canonical-001"
