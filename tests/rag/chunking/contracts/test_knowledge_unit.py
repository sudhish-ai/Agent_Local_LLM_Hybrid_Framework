# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF KnowledgeUnit contract.
#
# Responsibilities:
# - Validate derived Knowledge Unit construction.
# - Validate ResourceIdentity preservation.
# - Validate canonical-artifact provenance.
# - Validate derivation identity and sequence.
# - Validate bounded unit content.
# - Validate canonical content-kind preservation.
# - Validate derivation strategy reproducibility.
# - Validate required-field normalization.
# - Validate contract immutability.
#
# Must Not:
# - Test physical source acquisition.
# - Test format-specific parsing or normalization.
# - Test concrete chunking algorithms.
# - Test embedding, indexing, retrieval, or reranking.
# - Test concurrency or NFT execution strategies.
# - Test Standard RAG, GraphRAG, or Agentic RAG behavior.

from dataclasses import FrozenInstanceError

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


def _identity() -> ResourceIdentity:
    return ResourceIdentity(
        knowledge_scope_ref="scope-001",
        source_ref="source-001",
        logical_resource_id="resource-001",
        revision_id="revision-001",
    )


def _unit() -> KnowledgeUnit:
    return KnowledgeUnit(
        unit_id="unit-001",
        identity=_identity(),
        canonical_artifact_ref="canonical-001",
        derivation_id="derivation-001",
        sequence=0,
        content=b"bounded enterprise knowledge",
        content_kind=CanonicalContentKind.TEXT,
        media_type="text/plain",
        strategy_ref="text-chunking",
        strategy_version="1.0",
    )


def test_create_knowledge_unit() -> None:
    unit = _unit()

    assert unit.unit_id == "unit-001"
    assert unit.canonical_artifact_ref == "canonical-001"
    assert unit.derivation_id == "derivation-001"
    assert unit.sequence == 0
    assert unit.content == b"bounded enterprise knowledge"
    assert unit.content_kind == CanonicalContentKind.TEXT
    assert unit.media_type == "text/plain"
    assert unit.strategy_ref == "text-chunking"
    assert unit.strategy_version == "1.0"


def test_resource_identity_is_preserved() -> None:
    identity = _identity()

    unit = KnowledgeUnit(
        unit_id="unit-001",
        identity=identity,
        canonical_artifact_ref="canonical-001",
        derivation_id="derivation-001",
        sequence=0,
        content=b"knowledge",
        content_kind=CanonicalContentKind.TEXT,
        media_type="text/plain",
        strategy_ref="text-chunking",
        strategy_version="1.0",
    )

    assert unit.identity is identity


def test_identity_properties_are_exposed() -> None:
    unit = _unit()

    assert unit.resource_ref == "resource-001"
    assert unit.revision_ref == "revision-001"
    assert unit.knowledge_scope_ref == "scope-001"


def test_size_bytes_reports_unit_size() -> None:
    unit = _unit()

    assert unit.size_bytes == len(
        b"bounded enterprise knowledge"
    )


def test_zero_sequence_is_supported() -> None:
    unit = _unit()

    assert unit.sequence == 0


def test_positive_sequence_is_supported() -> None:
    unit = KnowledgeUnit(
        unit_id="unit-010",
        identity=_identity(),
        canonical_artifact_ref="canonical-001",
        derivation_id="derivation-001",
        sequence=9,
        content=b"knowledge",
        content_kind=CanonicalContentKind.TEXT,
        media_type="text/plain",
        strategy_ref="text-chunking",
        strategy_version="1.0",
    )

    assert unit.sequence == 9


def test_empty_unit_content_is_supported() -> None:
    unit = KnowledgeUnit(
        unit_id="unit-empty",
        identity=_identity(),
        canonical_artifact_ref="canonical-001",
        derivation_id="derivation-001",
        sequence=0,
        content=b"",
        content_kind=CanonicalContentKind.TEXT,
        media_type="text/plain",
        strategy_ref="text-chunking",
        strategy_version="1.0",
    )

    assert unit.content == b""
    assert unit.size_bytes == 0


@pytest.mark.parametrize(
    "content_kind",
    tuple(CanonicalContentKind),
)
def test_all_canonical_content_kinds_are_supported(
    content_kind: CanonicalContentKind,
) -> None:
    unit = KnowledgeUnit(
        unit_id="unit-001",
        identity=_identity(),
        canonical_artifact_ref="canonical-001",
        derivation_id="derivation-001",
        sequence=0,
        content=b"knowledge",
        content_kind=content_kind,
        media_type="application/octet-stream",
        strategy_ref="derivation-strategy",
        strategy_version="1.0",
    )

    assert unit.content_kind == content_kind


def test_required_text_values_are_normalized() -> None:
    unit = KnowledgeUnit(
        unit_id="  unit-001  ",
        identity=_identity(),
        canonical_artifact_ref="  canonical-001  ",
        derivation_id="  derivation-001  ",
        sequence=0,
        content=b"knowledge",
        content_kind=CanonicalContentKind.TEXT,
        media_type="  text/plain  ",
        strategy_ref="  text-chunking  ",
        strategy_version="  1.0  ",
    )

    assert unit.unit_id == "unit-001"
    assert unit.canonical_artifact_ref == "canonical-001"
    assert unit.derivation_id == "derivation-001"
    assert unit.media_type == "text/plain"
    assert unit.strategy_ref == "text-chunking"
    assert unit.strategy_version == "1.0"


def test_invalid_identity_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match="identity must be an instance of ResourceIdentity",
    ):
        KnowledgeUnit(
            unit_id="unit-001",
            identity="invalid-identity",
            canonical_artifact_ref="canonical-001",
            derivation_id="derivation-001",
            sequence=0,
            content=b"knowledge",
            content_kind=CanonicalContentKind.TEXT,
            media_type="text/plain",
            strategy_ref="text-chunking",
            strategy_version="1.0",
        )


@pytest.mark.parametrize(
    "sequence",
    (
        True,
        False,
        1.5,
        "1",
        None,
    ),
)
def test_sequence_rejects_non_integer_value(
    sequence: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="sequence must be an int",
    ):
        KnowledgeUnit(
            unit_id="unit-001",
            identity=_identity(),
            canonical_artifact_ref="canonical-001",
            derivation_id="derivation-001",
            sequence=sequence,
            content=b"knowledge",
            content_kind=CanonicalContentKind.TEXT,
            media_type="text/plain",
            strategy_ref="text-chunking",
            strategy_version="1.0",
        )


def test_negative_sequence_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="sequence cannot be negative",
    ):
        KnowledgeUnit(
            unit_id="unit-001",
            identity=_identity(),
            canonical_artifact_ref="canonical-001",
            derivation_id="derivation-001",
            sequence=-1,
            content=b"knowledge",
            content_kind=CanonicalContentKind.TEXT,
            media_type="text/plain",
            strategy_ref="text-chunking",
            strategy_version="1.0",
        )


def test_non_bytes_content_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match="content must be bytes",
    ):
        KnowledgeUnit(
            unit_id="unit-001",
            identity=_identity(),
            canonical_artifact_ref="canonical-001",
            derivation_id="derivation-001",
            sequence=0,
            content="knowledge",
            content_kind=CanonicalContentKind.TEXT,
            media_type="text/plain",
            strategy_ref="text-chunking",
            strategy_version="1.0",
        )


def test_invalid_content_kind_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "content_kind must be an instance of "
            "CanonicalContentKind"
        ),
    ):
        KnowledgeUnit(
            unit_id="unit-001",
            identity=_identity(),
            canonical_artifact_ref="canonical-001",
            derivation_id="derivation-001",
            sequence=0,
            content=b"knowledge",
            content_kind="TEXT",
            media_type="text/plain",
            strategy_ref="text-chunking",
            strategy_version="1.0",
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "unit_id",
        "canonical_artifact_ref",
        "derivation_id",
        "media_type",
        "strategy_ref",
        "strategy_version",
    ),
)
def test_required_text_rejects_empty_value(
    field_name: str,
) -> None:
    values = {
        "unit_id": "unit-001",
        "identity": _identity(),
        "canonical_artifact_ref": "canonical-001",
        "derivation_id": "derivation-001",
        "sequence": 0,
        "content": b"knowledge",
        "content_kind": CanonicalContentKind.TEXT,
        "media_type": "text/plain",
        "strategy_ref": "text-chunking",
        "strategy_version": "1.0",
    }
    values[field_name] = "   "

    with pytest.raises(
        ValueError,
        match=f"{field_name} cannot be empty",
    ):
        KnowledgeUnit(**values)


def test_knowledge_unit_is_immutable() -> None:
    unit = _unit()

    with pytest.raises(FrozenInstanceError):
        unit.sequence = 1
