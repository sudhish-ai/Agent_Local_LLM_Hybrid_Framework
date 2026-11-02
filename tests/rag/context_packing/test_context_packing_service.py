# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF ContextPackingService.
#
# Responsibilities:
# - Validate Context-packing orchestration.
# - Validate deterministic packer delegation.
# - Validate Evidence ordering and Context provenance.
# - Validate Context size boundaries.
# - Validate Knowledge scope normalization.
# - Validate invalid packer and request inputs.
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

from alhf.rag.context_packing.context_packing_service import (
    ContextPackingService,
)
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
) -> EvidenceItem:
    return EvidenceItem(
        evidence_id=evidence_id,
        representation_ref=f"representation-{rank:03d}",
        knowledge_unit_ref=f"unit-{rank:03d}",
        derivation_id="derivation-001",
        knowledge_scope_ref="scope-001",
        resource_ref="resource-001",
        revision_ref="revision-001",
        content=content,
        media_type="text/plain",
        relation=EvidenceRelation.CANDIDATE,
        retrieval_score=1.0,
        retrieval_rank=rank,
    )


def _service() -> ContextPackingService:
    return ContextPackingService(
        packer=DeterministicContextPacker(),
    )


def test_create_context_packing_service() -> None:
    assert isinstance(
        _service(),
        ContextPackingService,
    )


def test_pack_returns_knowledge_context() -> None:
    context = _service().pack(
        evidence=iter((_evidence(),)),
        knowledge_scope_ref="scope-001",
        max_bytes=100,
    )

    assert isinstance(
        context,
        KnowledgeContext,
    )


def test_pack_preserves_evidence_content() -> None:
    context = _service().pack(
        evidence=iter((_evidence(),)),
        knowledge_scope_ref="scope-001",
        max_bytes=100,
    )

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

    context = _service().pack(
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
    context = _service().pack(
        evidence=iter((_evidence(),)),
        knowledge_scope_ref="  scope-001  ",
        max_bytes=100,
    )

    assert context.knowledge_scope_ref == "scope-001"


def test_pack_respects_max_bytes() -> None:
    context = _service().pack(
        evidence=iter(
            (
                _evidence(
                    content=b"abcdef",
                ),
            )
        ),
        knowledge_scope_ref="scope-001",
        max_bytes=3,
    )

    assert context.size_bytes <= 3


def test_empty_evidence_produces_empty_context() -> None:
    context = _service().pack(
        evidence=iter(()),
        knowledge_scope_ref="scope-001",
        max_bytes=100,
    )

    assert context.content == b""
    assert context.evidence_refs == ()
    assert context.evidence_count == 0


def test_context_identity_is_deterministic() -> None:
    service = _service()

    first = service.pack(
        evidence=iter((_evidence(),)),
        knowledge_scope_ref="scope-001",
        max_bytes=100,
    )
    second = service.pack(
        evidence=iter((_evidence(),)),
        knowledge_scope_ref="scope-001",
        max_bytes=100,
    )

    assert first.context_id == second.context_id


def test_invalid_packer_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match="packer must be an instance of ContextPacker",
    ):
        ContextPackingService(
            packer="invalid-packer"
        )


def test_non_iterator_evidence_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match="evidence must be an Iterator",
    ):
        _service().pack(
            evidence=(),
            knowledge_scope_ref="scope-001",
            max_bytes=100,
        )


@pytest.mark.parametrize(
    "knowledge_scope_ref",
    ("", "   "),
)
def test_empty_knowledge_scope_is_rejected(
    knowledge_scope_ref: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="knowledge_scope_ref cannot be empty",
    ):
        _service().pack(
            evidence=iter(()),
            knowledge_scope_ref=knowledge_scope_ref,
            max_bytes=100,
        )


def test_non_string_knowledge_scope_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match="knowledge_scope_ref must be a string",
    ):
        _service().pack(
            evidence=iter(()),
            knowledge_scope_ref=123,
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
        _service().pack(
            evidence=iter(()),
            knowledge_scope_ref="scope-001",
            max_bytes=max_bytes,
        )


@pytest.mark.parametrize(
    "max_bytes",
    (True, 1.5, "100", None),
)
def test_invalid_max_bytes_type_is_rejected(
    max_bytes: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="max_bytes must be an int",
    ):
        _service().pack(
            evidence=iter(()),
            knowledge_scope_ref="scope-001",
            max_bytes=max_bytes,
        )
