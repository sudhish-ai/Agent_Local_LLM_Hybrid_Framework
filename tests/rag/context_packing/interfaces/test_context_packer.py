# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF ContextPacker interface.
#
# Responsibilities:
# - Validate the abstract Context-packing boundary.
# - Validate stable packer identity and version.
# - Validate Evidence-to-KnowledgeContext construction.
# - Validate Evidence ordering and references.
# - Validate bounded Context content.
# - Validate Knowledge scope preservation.
#
# Must Not:
# - Test adaptive Context Intelligence.
# - Test token budgeting or model routing.
# - Perform retrieval or Evidence construction.
# - Generate prompts or answers.
# - Treat Context as durable memory.
# - Depend on external RAG frameworks.

from collections.abc import Iterator

import pytest

from alhf.rag.context_packing.contracts.knowledge_context import (
    KnowledgeContext,
)
from alhf.rag.context_packing.interfaces.context_packer import (
    ContextPacker,
)
from alhf.rag.evidence.contracts.evidence_item import (
    EvidenceItem,
    EvidenceRelation,
)


class StubContextPacker(ContextPacker):
    """Minimal deterministic packer for interface testing."""

    @property
    def packer_ref(self) -> str:
        return "stub-context-packer"

    @property
    def packer_version(self) -> str:
        return "1.0"

    def pack(
        self,
        *,
        evidence: Iterator[EvidenceItem],
        knowledge_scope_ref: str,
        max_bytes: int,
    ) -> KnowledgeContext:
        items = tuple(
            evidence
        )

        content = b"\n".join(
            item.content
            for item in items
        )[:max_bytes]

        return KnowledgeContext(
            context_id="context-001",
            knowledge_scope_ref=knowledge_scope_ref,
            evidence_refs=tuple(
                item.evidence_id
                for item in items
            ),
            content=content,
            media_type="text/plain",
            strategy_ref=self.packer_ref,
            strategy_version=self.packer_version,
        )


class MissingPackContextPacker(ContextPacker):
    """Invalid packer intentionally missing pack behavior."""

    @property
    def packer_ref(self) -> str:
        return "missing-pack"

    @property
    def packer_version(self) -> str:
        return "1.0"


def _evidence(
    *,
    evidence_id: str = "evidence-001",
    content: bytes = b"enterprise evidence",
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


def test_context_packer_is_abstract() -> None:
    with pytest.raises(TypeError):
        ContextPacker()


def test_missing_pack_prevents_instantiation() -> None:
    with pytest.raises(TypeError):
        MissingPackContextPacker()


def test_concrete_packer_can_be_instantiated() -> None:
    assert isinstance(
        StubContextPacker(),
        ContextPacker,
    )


def test_packer_exposes_stable_identity() -> None:
    packer = StubContextPacker()

    assert packer.packer_ref == "stub-context-packer"
    assert packer.packer_version == "1.0"


def test_pack_returns_knowledge_context() -> None:
    context = StubContextPacker().pack(
        evidence=iter(
            (
                _evidence(),
            )
        ),
        knowledge_scope_ref="scope-001",
        max_bytes=100,
    )

    assert isinstance(
        context,
        KnowledgeContext,
    )


def test_pack_preserves_knowledge_scope() -> None:
    context = StubContextPacker().pack(
        evidence=iter(
            (
                _evidence(),
            )
        ),
        knowledge_scope_ref="scope-001",
        max_bytes=100,
    )

    assert context.knowledge_scope_ref == "scope-001"


def test_pack_preserves_evidence_reference() -> None:
    context = StubContextPacker().pack(
        evidence=iter(
            (
                _evidence(),
            )
        ),
        knowledge_scope_ref="scope-001",
        max_bytes=100,
    )

    assert context.evidence_refs == (
        "evidence-001",
    )


def test_pack_preserves_evidence_order() -> None:
    first = _evidence(
        evidence_id="evidence-001",
        content=b"first",
        rank=1,
    )
    second = _evidence(
        evidence_id="evidence-002",
        content=b"second",
        rank=2,
    )

    context = StubContextPacker().pack(
        evidence=iter(
            (
                first,
                second,
            )
        ),
        knowledge_scope_ref="scope-001",
        max_bytes=100,
    )

    assert context.evidence_refs == (
        "evidence-001",
        "evidence-002",
    )
    assert context.content == b"first\nsecond"


def test_pack_respects_max_bytes() -> None:
    context = StubContextPacker().pack(
        evidence=iter(
            (
                _evidence(
                    content=b"abcdef"
                ),
            )
        ),
        knowledge_scope_ref="scope-001",
        max_bytes=3,
    )

    assert context.content == b"abc"
    assert context.size_bytes == 3


def test_pack_records_strategy_identity() -> None:
    context = StubContextPacker().pack(
        evidence=iter(
            (
                _evidence(),
            )
        ),
        knowledge_scope_ref="scope-001",
        max_bytes=100,
    )

    assert context.strategy_ref == "stub-context-packer"
    assert context.strategy_version == "1.0"
