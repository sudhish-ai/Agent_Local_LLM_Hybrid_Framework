# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF DerivationService.
#
# Responsibilities:
# - Validate dynamic derivation-strategy resolution.
# - Validate incremental Knowledge Unit production.
# - Validate ResourceIdentity preservation.
# - Validate Knowledge-scope preservation.
# - Validate derivation strategy identity and version.
# - Validate deterministic unit sequencing.
# - Validate canonical-artifact provenance.
# - Validate deterministic derivation behavior.
# - Validate unsupported canonical content behavior.
# - Validate invalid registry and strategy behavior.
#
# Must Not:
# - Test acquisition, parsing, or normalization.
# - Test concrete derivation algorithms in depth.
# - Test adaptive or evidence-driven Derivation Intelligence.
# - Test embedding, indexing, retrieval, or reranking.
# - Test concurrency or NFT execution strategies.
# - Depend on external RAG or orchestration frameworks.

from collections.abc import Iterator

import pytest

from alhf.rag.chunking.contracts.knowledge_unit import (
    KnowledgeUnit,
)
from alhf.rag.chunking.derivation_service import (
    DerivationService,
)
from alhf.rag.chunking.interfaces.derivation_registry import (
    DerivationRegistry,
)
from alhf.rag.chunking.interfaces.derivation_strategy import (
    DerivationStrategy,
)
from alhf.rag.chunking.providers.in_memory_derivation_registry import (
    InMemoryDerivationRegistry,
)
from alhf.rag.chunking.strategies.fixed_size_text_derivation import (
    FixedSizeTextDerivation,
)
from alhf.rag.ingestion.contracts.canonical_content import (
    CanonicalContent,
    CanonicalContentKind,
)
from alhf.rag.ingestion.contracts.resource_identity import (
    ResourceIdentity,
)


def _content(
    *,
    data: bytes = b"abcdefghij",
    content_kind: CanonicalContentKind = CanonicalContentKind.TEXT,
    media_type: str = "text/plain",
) -> CanonicalContent:
    return CanonicalContent(
        identity=ResourceIdentity(
            knowledge_scope_ref="scope-001",
            source_ref="source-001",
            logical_resource_id="resource-001",
            revision_id="revision-001",
        ),
        content=data,
        content_kind=content_kind,
        media_type=media_type,
        parsed_artifact_ref="parsed-001",
        normalizer_ref="text-normalizer",
        normalizer_version="1.0",
    )


def _strategy() -> FixedSizeTextDerivation:
    return FixedSizeTextDerivation(
        chunk_size_bytes=4,
        overlap_bytes=0,
    )


def _registry() -> InMemoryDerivationRegistry:
    registry = InMemoryDerivationRegistry()
    registry.register(
        _strategy()
    )
    return registry


def _service() -> DerivationService:
    return DerivationService(
        registry=_registry()
    )


def test_create_derivation_service() -> None:
    service = _service()

    assert isinstance(
        service,
        DerivationService,
    )


def test_derive_returns_iterator() -> None:
    units = _service().derive(
        _content()
    )

    assert isinstance(
        units,
        Iterator,
    )


def test_derive_returns_knowledge_units() -> None:
    units = tuple(
        _service().derive(
            _content()
        )
    )

    assert units
    assert all(
        isinstance(unit, KnowledgeUnit)
        for unit in units
    )


def test_derive_uses_resolved_strategy() -> None:
    units = tuple(
        _service().derive(
            _content()
        )
    )

    assert tuple(
        unit.content
        for unit in units
    ) == (
        b"abcd",
        b"efgh",
        b"ij",
    )


def test_derive_preserves_resource_identity() -> None:
    content = _content()

    units = tuple(
        _service().derive(
            content
        )
    )

    assert all(
        unit.identity is content.identity
        for unit in units
    )
    assert all(
        unit.resource_ref == "resource-001"
        for unit in units
    )
    assert all(
        unit.revision_ref == "revision-001"
        for unit in units
    )


def test_derive_preserves_knowledge_scope() -> None:
    units = tuple(
        _service().derive(
            _content()
        )
    )

    assert all(
        unit.knowledge_scope_ref == "scope-001"
        for unit in units
    )


def test_derive_records_strategy_identity() -> None:
    units = tuple(
        _service().derive(
            _content()
        )
    )

    assert all(
        unit.strategy_ref == "fixed-size-text-derivation"
        for unit in units
    )
    assert all(
        unit.strategy_version == "1.0"
        for unit in units
    )


def test_derive_preserves_sequence_order() -> None:
    units = tuple(
        _service().derive(
            _content()
        )
    )

    assert tuple(
        unit.sequence
        for unit in units
    ) == (
        0,
        1,
        2,
    )


def test_derive_preserves_canonical_provenance() -> None:
    units = tuple(
        _service().derive(
            _content()
        )
    )

    assert all(
        unit.canonical_artifact_ref.startswith(
            "canonical:"
        )
        for unit in units
    )


def test_derive_is_deterministic() -> None:
    service = _service()
    content = _content()

    first = tuple(
        service.derive(
            content
        )
    )
    second = tuple(
        service.derive(
            content
        )
    )

    assert tuple(
        unit.unit_id
        for unit in first
    ) == tuple(
        unit.unit_id
        for unit in second
    )

    assert tuple(
        unit.derivation_id
        for unit in first
    ) == tuple(
        unit.derivation_id
        for unit in second
    )


def test_empty_content_produces_no_units() -> None:
    units = tuple(
        _service().derive(
            _content(
                data=b"",
            )
        )
    )

    assert units == ()


def test_unsupported_content_is_rejected() -> None:
    service = _service()

    with pytest.raises(
        LookupError,
        match="derivation strategy not found",
    ):
        tuple(
            service.derive(
                _content(
                    content_kind=CanonicalContentKind.STRUCTURED,
                    media_type="application/json",
                )
            )
        )


def test_invalid_content_is_rejected() -> None:
    service = _service()

    with pytest.raises(
        TypeError,
        match="content must be an instance of CanonicalContent",
    ):
        tuple(
            service.derive(
                "invalid-content"
            )
        )


def test_invalid_registry_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "registry must be an instance of "
            "DerivationRegistry"
        ),
    ):
        DerivationService(
            registry="invalid-registry"
        )


class InvalidStrategyRegistry(DerivationRegistry):
    """Registry intentionally returning an invalid strategy."""

    def resolve(
        self,
        content: CanonicalContent,
    ):
        return "invalid-strategy"

    def contains(
        self,
        content: CanonicalContent,
    ) -> bool:
        return True


def test_invalid_registry_strategy_is_rejected() -> None:
    service = DerivationService(
        registry=InvalidStrategyRegistry()
    )

    with pytest.raises(
        TypeError,
        match="registry must return DerivationStrategy",
    ):
        tuple(
            service.derive(
                _content()
            )
        )


class IncompatibleStrategy(DerivationStrategy):
    """Strategy intentionally incompatible with canonical content."""

    @property
    def strategy_ref(self) -> str:
        return "incompatible-strategy"

    @property
    def strategy_version(self) -> str:
        return "1.0"

    def supports(
        self,
        content: CanonicalContent,
    ) -> bool:
        return False

    def derive(
        self,
        content: CanonicalContent,
    ):
        return iter(())


class IncompatibleStrategyRegistry(DerivationRegistry):
    """Registry intentionally returning an incompatible strategy."""

    def resolve(
        self,
        content: CanonicalContent,
    ) -> DerivationStrategy:
        return IncompatibleStrategy()

    def contains(
        self,
        content: CanonicalContent,
    ) -> bool:
        return True


def test_incompatible_strategy_is_rejected() -> None:
    service = DerivationService(
        registry=IncompatibleStrategyRegistry()
    )

    with pytest.raises(
        ValueError,
        match=(
            "resolved strategy does not support "
            "canonical content"
        ),
    ):
        tuple(
            service.derive(
                _content()
            )
        )
