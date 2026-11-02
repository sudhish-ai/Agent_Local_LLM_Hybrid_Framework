# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF KnowledgeContext contract.
#
# Responsibilities:
# - Validate immutable Knowledge Context construction.
# - Validate Knowledge scope preservation.
# - Validate ordered Evidence references.
# - Validate Context content and size semantics.
# - Validate packing strategy identity and version.
# - Validate required text normalization.
# - Validate invalid Context inputs.
#
# Must Not:
# - Perform Evidence selection or prioritization.
# - Test retrieval or reranking.
# - Generate prompts or answers.
# - Test token budgeting or model routing.
# - Test adaptive Context Intelligence.
# - Treat Context as durable memory.
# - Depend on external RAG frameworks.

from dataclasses import FrozenInstanceError

import pytest

from alhf.rag.context_packing.contracts.knowledge_context import (
    KnowledgeContext,
)


def _context(
    **overrides,
) -> KnowledgeContext:
    values = {
        "context_id": "context-001",
        "knowledge_scope_ref": "scope-001",
        "evidence_refs": (
            "evidence-001",
            "evidence-002",
        ),
        "content": b"enterprise context",
        "media_type": "text/plain",
        "strategy_ref": "deterministic-context-packing",
        "strategy_version": "1.0",
    }
    values.update(
        overrides
    )

    return KnowledgeContext(
        **values
    )


def test_create_knowledge_context() -> None:
    context = _context()

    assert context.context_id == "context-001"
    assert context.knowledge_scope_ref == "scope-001"
    assert context.media_type == "text/plain"
    assert context.strategy_ref == "deterministic-context-packing"
    assert context.strategy_version == "1.0"


def test_context_preserves_ordered_evidence_refs() -> None:
    context = _context()

    assert context.evidence_refs == (
        "evidence-001",
        "evidence-002",
    )


def test_evidence_count_reports_reference_count() -> None:
    context = _context()

    assert context.evidence_count == 2


def test_context_preserves_content() -> None:
    context = _context(
        content=b"packed evidence context",
    )

    assert context.content == b"packed evidence context"


def test_size_bytes_reports_content_size() -> None:
    content = b"packed evidence context"

    context = _context(
        content=content,
    )

    assert context.size_bytes == len(
        content
    )


def test_empty_context_content_is_supported() -> None:
    context = _context(
        content=b"",
    )

    assert context.content == b""
    assert context.size_bytes == 0


def test_empty_evidence_refs_are_supported() -> None:
    context = _context(
        evidence_refs=(),
    )

    assert context.evidence_refs == ()
    assert context.evidence_count == 0


def test_required_text_values_are_normalized() -> None:
    context = _context(
        context_id="  context-001  ",
        knowledge_scope_ref="  scope-001  ",
        evidence_refs=(
            "  evidence-001  ",
        ),
        media_type="  text/plain  ",
        strategy_ref="  deterministic-context-packing  ",
        strategy_version="  1.0  ",
    )

    assert context.context_id == "context-001"
    assert context.knowledge_scope_ref == "scope-001"
    assert context.evidence_refs == (
        "evidence-001",
    )
    assert context.media_type == "text/plain"
    assert context.strategy_ref == "deterministic-context-packing"
    assert context.strategy_version == "1.0"


def test_duplicate_evidence_refs_are_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="evidence_refs must not contain duplicates",
    ):
        _context(
            evidence_refs=(
                "evidence-001",
                "evidence-001",
            )
        )


def test_duplicate_refs_after_normalization_are_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="evidence_refs must not contain duplicates",
    ):
        _context(
            evidence_refs=(
                "evidence-001",
                "  evidence-001  ",
            )
        )


def test_non_tuple_evidence_refs_are_rejected() -> None:
    with pytest.raises(
        TypeError,
        match="evidence_refs must be a tuple",
    ):
        _context(
            evidence_refs=[
                "evidence-001",
            ]
        )


@pytest.mark.parametrize(
    "evidence_ref",
    (
        "",
        "   ",
    ),
)
def test_empty_evidence_reference_is_rejected(
    evidence_ref: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="evidence_ref cannot be empty",
    ):
        _context(
            evidence_refs=(
                evidence_ref,
            )
        )


def test_non_string_evidence_reference_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match="evidence_ref must be a string",
    ):
        _context(
            evidence_refs=(
                123,
            )
        )


def test_non_bytes_content_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match="content must be bytes",
    ):
        _context(
            content="invalid-context"
        )


def test_knowledge_context_is_immutable() -> None:
    context = _context()

    with pytest.raises(FrozenInstanceError):
        context.context_id = "context-002"
