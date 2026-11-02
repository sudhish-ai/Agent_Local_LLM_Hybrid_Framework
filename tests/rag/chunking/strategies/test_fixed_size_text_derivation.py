# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF FixedSizeTextDerivation strategy.
#
# Responsibilities:
# - Validate deterministic fixed-size text derivation.
# - Validate explicit chunk-size and overlap configuration.
# - Validate bounded incremental Knowledge Unit production.
# - Validate ResourceIdentity and canonical provenance preservation.
# - Validate deterministic derivation and unit identities.
# - Validate unit sequence and strategy reproducibility.
# - Validate unsupported content and invalid configuration rejection.
#
# Must Not:
# - Test adaptive or evidence-driven Derivation Intelligence.
# - Test acquisition, parsing, or normalization.
# - Test embeddings, indexing, retrieval, or reranking.
# - Treat fixed-size derivation as North-Star behavior.
# - Test concurrency or NFT execution strategies.
# - Depend on external RAG or orchestration frameworks.

from collections.abc import Iterator

import pytest

from alhf.rag.chunking.contracts.knowledge_unit import (
    KnowledgeUnit,
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


def _strategy(
    *,
    chunk_size_bytes: int = 4,
    overlap_bytes: int = 0,
) -> FixedSizeTextDerivation:
    return FixedSizeTextDerivation(
        chunk_size_bytes=chunk_size_bytes,
        overlap_bytes=overlap_bytes,
    )


def test_strategy_exposes_stable_identity() -> None:
    strategy = _strategy()

    assert strategy.strategy_ref == "fixed-size-text-derivation"
    assert strategy.strategy_version == "1.0"


def test_strategy_supports_canonical_text() -> None:
    strategy = _strategy()

    assert strategy.supports(
        _content()
    ) is True


def test_strategy_rejects_non_text_content_kind() -> None:
    strategy = _strategy()

    assert strategy.supports(
        _content(
            content_kind=CanonicalContentKind.STRUCTURED,
        )
    ) is False


def test_strategy_rejects_non_text_media_type() -> None:
    strategy = _strategy()

    assert strategy.supports(
        _content(
            media_type="application/json",
        )
    ) is False


def test_derive_returns_iterator() -> None:
    units = _strategy().derive(
        _content()
    )

    assert isinstance(
        units,
        Iterator,
    )


def test_derive_splits_content_by_configured_size() -> None:
    units = tuple(
        _strategy(
            chunk_size_bytes=4,
        ).derive(
            _content(
                data=b"abcdefghij",
            )
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


def test_derive_supports_configured_overlap() -> None:
    units = tuple(
        _strategy(
            chunk_size_bytes=4,
            overlap_bytes=2,
        ).derive(
            _content(
                data=b"abcdefgh",
            )
        )
    )

    assert tuple(
        unit.content
        for unit in units
    ) == (
        b"abcd",
        b"cdef",
        b"efgh",
        b"gh",
    )


def test_derive_yields_knowledge_units() -> None:
    units = tuple(
        _strategy().derive(
            _content()
        )
    )

    assert units
    assert all(
        isinstance(unit, KnowledgeUnit)
        for unit in units
    )


def test_derive_preserves_resource_identity() -> None:
    content = _content()

    units = tuple(
        _strategy().derive(
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
        _strategy().derive(
            _content()
        )
    )

    assert all(
        unit.knowledge_scope_ref == "scope-001"
        for unit in units
    )


def test_derive_assigns_zero_based_sequence() -> None:
    units = tuple(
        _strategy().derive(
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


def test_units_preserve_strategy_reproducibility() -> None:
    strategy = _strategy()

    units = tuple(
        strategy.derive(
            _content()
        )
    )

    assert all(
        unit.strategy_ref == strategy.strategy_ref
        for unit in units
    )
    assert all(
        unit.strategy_version == strategy.strategy_version
        for unit in units
    )


def test_derivation_identity_is_stable() -> None:
    strategy = _strategy()
    content = _content()

    first = tuple(
        strategy.derive(content)
    )
    second = tuple(
        strategy.derive(content)
    )

    assert first[0].derivation_id == second[0].derivation_id


def test_unit_identity_is_stable() -> None:
    strategy = _strategy()
    content = _content()

    first = tuple(
        strategy.derive(content)
    )
    second = tuple(
        strategy.derive(content)
    )

    assert tuple(
        unit.unit_id
        for unit in first
    ) == tuple(
        unit.unit_id
        for unit in second
    )


def test_configuration_changes_derivation_identity() -> None:
    content = _content()

    first = tuple(
        _strategy(
            chunk_size_bytes=4,
        ).derive(content)
    )
    second = tuple(
        _strategy(
            chunk_size_bytes=5,
        ).derive(content)
    )

    assert first[0].derivation_id != second[0].derivation_id


def test_empty_content_produces_no_units() -> None:
    units = tuple(
        _strategy().derive(
            _content(
                data=b"",
            )
        )
    )

    assert units == ()


def test_invalid_content_contract_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match="content must be an instance of CanonicalContent",
    ):
        tuple(
            _strategy().derive(
                "invalid-content"
            )
        )


def test_unsupported_content_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "FixedSizeTextDerivation requires "
            "canonical text content"
        ),
    ):
        tuple(
            _strategy().derive(
                _content(
                    content_kind=CanonicalContentKind.STRUCTURED,
                    media_type="application/json",
                )
            )
        )


@pytest.mark.parametrize(
    "chunk_size_bytes",
    (
        0,
        -1,
    ),
)
def test_chunk_size_must_be_positive(
    chunk_size_bytes: int,
) -> None:
    with pytest.raises(
        ValueError,
        match="chunk_size_bytes must be greater than zero",
    ):
        _strategy(
            chunk_size_bytes=chunk_size_bytes,
        )


@pytest.mark.parametrize(
    "chunk_size_bytes",
    (
        True,
        1.5,
        "4",
        None,
    ),
)
def test_chunk_size_must_be_integer(
    chunk_size_bytes: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="chunk_size_bytes must be an int",
    ):
        _strategy(
            chunk_size_bytes=chunk_size_bytes,
        )


def test_overlap_cannot_be_negative() -> None:
    with pytest.raises(
        ValueError,
        match="overlap_bytes cannot be negative",
    ):
        _strategy(
            overlap_bytes=-1,
        )


@pytest.mark.parametrize(
    "overlap_bytes",
    (
        True,
        1.5,
        "1",
        None,
    ),
)
def test_overlap_must_be_integer(
    overlap_bytes: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="overlap_bytes must be an int",
    ):
        _strategy(
            overlap_bytes=overlap_bytes,
        )


@pytest.mark.parametrize(
    "overlap_bytes",
    (
        4,
        5,
    ),
)
def test_overlap_must_be_smaller_than_chunk_size(
    overlap_bytes: int,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "overlap_bytes must be smaller than "
            "chunk_size_bytes"
        ),
    ):
        _strategy(
            chunk_size_bytes=4,
            overlap_bytes=overlap_bytes,
        )
