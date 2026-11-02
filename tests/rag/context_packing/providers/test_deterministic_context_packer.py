# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF DeterministicContextPacker.
#
# Responsibilities:
# - Validate stable packer identity and version.
# - Validate deterministic Evidence packing.
# - Validate Evidence ordering and references.
# - Validate whole-Evidence byte-bound behavior.
# - Validate Knowledge scope continuity.
# - Validate deterministic Context identity.
# - Validate invalid Evidence and packing inputs.
#
# Must Not:
# - Test token-aware Context packing.
# - Test model routing or token budgeting.
# - Perform retrieval or Evidence construction.
# - Generate prompts or answers.
# - Test adaptive Context Intelligence.
# - Treat Context as durable memory.
# - Depend on external RAG frameworks.

import pytest

from alhf.rag.context_packing.contracts.knowledge_context import (
    KnowledgeContext,
)
from alhf.rag.context_packing.providers.deterministic_context_packer import (
    DeterministicContextPacker,
)
from alhf.rag.evidence.contracts.evidence_item import (
    EvidenceItem,
    EvidenceRelation,
)


def _evidence(
    *,
    evidence_id: str = "evidence-001",
    content: bytes = b"alpha",
    rank: int = 1,
    scope: str = "scope-001",
    media_type: str = "text/plain",
) -> EvidenceItem:
    return EvidenceItem(
        evidence_id=evidence_id,
        representation_ref=f"representation-{rank:03d}",
        knowledge_unit_ref=f"unit-{rank:03d}",
        derivation_id="derivation-001",
        knowledge_scope_ref=scope,
        resource_ref="resource-001",
        revision_ref="revision-001",
        content=content,
        media_type=media_type,
        relation=EvidenceRelation.CANDIDATE,
        retrieval_score=1.0,
        retrieval_rank=rank,
    )


def _packer() -> DeterministicContextPacker:
    return DeterministicContextPacker()


def test_packer_exposes_stable_identity() -> None:
    packer = _packer()

    assert packer.packer_ref == "deterministic-context-packer"
    assert packer.packer_version == "1.0"


def test_pack_returns_knowledge_context() -> None:
    context = _packer().pack(
        evidence=iter((_evidence(),)),
        knowledge_scope_ref="scope-001",
        max_bytes=100,
    )

    assert isinstance(context, KnowledgeContext)
    assert context.content == b"alpha"
    assert context.evidence_refs == ("evidence-001",)


def test_pack_preserves_evidence_order() -> None:
    first = _evidence(
        evidence_id="evidence-001",
        content=b"alpha",
        rank=1,
    )
    second = _evidence(
        evidence_id="evidence-002",
        content=b"beta",
        rank=2,
    )

    context = _packer().pack(
        evidence=iter((first, second)),
        knowledge_scope_ref="scope-001",
        max_bytes=100,
    )

    assert context.evidence_refs == (
        "evidence-001",
        "evidence-002",
    )
    assert context.content == b"alpha\n\nbeta"


def test_pack_preserves_knowledge_scope() -> None:
    context = _packer().pack(
        evidence=iter((_evidence(),)),
        knowledge_scope_ref="scope-001",
        max_bytes=100,
    )

    assert context.knowledge_scope_ref == "scope-001"


def test_pack_records_strategy_identity() -> None:
    context = _packer().pack(
        evidence=iter((_evidence(),)),
        knowledge_scope_ref="scope-001",
        max_bytes=100,
    )

    assert context.strategy_ref == "deterministic-context-packer"
    assert context.strategy_version == "1.0"


def test_pack_preserves_whole_evidence_boundary() -> None:
    first = _evidence(
        evidence_id="evidence-001",
        content=b"alpha",
        rank=1,
    )
    second = _evidence(
        evidence_id="evidence-002",
        content=b"long-content",
        rank=2,
    )

    context = _packer().pack(
        evidence=iter((first, second)),
        knowledge_scope_ref="scope-001",
        max_bytes=5,
    )

    assert context.content == b"alpha"
    assert context.evidence_refs == ("evidence-001",)
    assert context.size_bytes == 5


def test_first_oversized_evidence_produces_empty_context() -> None:
    context = _packer().pack(
        evidence=iter(
            (
                _evidence(
                    content=b"oversized",
                ),
            )
        ),
        knowledge_scope_ref="scope-001",
        max_bytes=3,
    )

    assert context.content == b""
    assert context.evidence_refs == ()
    assert context.evidence_count == 0


def test_empty_evidence_stream_produces_empty_context() -> None:
    context = _packer().pack(
        evidence=iter(()),
        knowledge_scope_ref="scope-001",
        max_bytes=100,
    )

    assert context.content == b""
    assert context.evidence_refs == ()
    assert context.evidence_count == 0


def test_context_identity_is_deterministic() -> None:
    packer = _packer()

    first = packer.pack(
        evidence=iter((_evidence(),)),
        knowledge_scope_ref="scope-001",
        max_bytes=100,
    )
    second = packer.pack(
        evidence=iter((_evidence(),)),
        knowledge_scope_ref="scope-001",
        max_bytes=100,
    )

    assert first.context_id == second.context_id
    assert first.context_id.startswith("context:")


def test_scope_mismatch_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="Evidence knowledge_scope_ref must match Context scope",
    ):
        _packer().pack(
            evidence=iter(
                (
                    _evidence(
                        scope="scope-002",
                    ),
                )
            ),
            knowledge_scope_ref="scope-001",
            max_bytes=100,
        )


def test_unsupported_media_type_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "DeterministicContextPacker requires "
            "text/plain Evidence"
        ),
    ):
        _packer().pack(
            evidence=iter(
                (
                    _evidence(
                        media_type="application/json",
                    ),
                )
            ),
            knowledge_scope_ref="scope-001",
            max_bytes=100,
        )


def test_invalid_evidence_item_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match="evidence must yield EvidenceItem",
    ):
        _packer().pack(
            evidence=iter(("invalid-evidence",)),
            knowledge_scope_ref="scope-001",
            max_bytes=100,
        )


def test_non_iterator_evidence_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match="evidence must be an Iterator",
    ):
        _packer().pack(
            evidence=(),
            knowledge_scope_ref="scope-001",
            max_bytes=100,
        )


@pytest.mark.parametrize(
    "max_bytes",
    (0, -1),
)
def test_non_positive_max_bytes_is_rejected(
    max_bytes: int,
) -> None:
    with pytest.raises(
        ValueError,
        match="max_bytes must be greater than zero",
    ):
        _packer().pack(
            evidence=iter(()),
            knowledge_scope_ref="scope-001",
            max_bytes=max_bytes,
        )


@pytest.mark.parametrize(
    "max_bytes",
    (True, 1.5, "10", None),
)
def test_invalid_max_bytes_type_is_rejected(
    max_bytes: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="max_bytes must be an int",
    ):
        _packer().pack(
            evidence=iter(()),
            knowledge_scope_ref="scope-001",
            max_bytes=max_bytes,
        )
