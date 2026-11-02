# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF EvidenceItem contract.
#
# Responsibilities:
# - Validate immutable Evidence construction.
# - Validate Knowledge and representation provenance.
# - Validate Evidence relation semantics.
# - Validate retrieval score and rank preservation.
# - Validate Evidence content and size semantics.
# - Validate required field normalization.
# - Validate invalid Evidence inputs.
#
# Must Not:
# - Perform retrieval or reranking.
# - Determine Evidence sufficiency.
# - Resolve Evidence conflicts.
# - Construct Context or generate answers.
# - Test Evidence Intelligence.
# - Depend on external RAG frameworks.

import math
from dataclasses import FrozenInstanceError

import pytest

from alhf.rag.evidence.contracts.evidence_item import (
    EvidenceItem,
    EvidenceRelation,
)


def _item(
    *,
    relation: EvidenceRelation = EvidenceRelation.CANDIDATE,
    score: float = 0.9,
    rank: int = 1,
    content: bytes = b"enterprise evidence",
) -> EvidenceItem:
    return EvidenceItem(
        evidence_id="evidence-001",
        representation_ref="representation-001",
        knowledge_unit_ref="unit-001",
        derivation_id="derivation-001",
        knowledge_scope_ref="scope-001",
        resource_ref="resource-001",
        revision_ref="revision-001",
        content=content,
        media_type="text/plain",
        relation=relation,
        retrieval_score=score,
        retrieval_rank=rank,
    )


def test_create_evidence_item() -> None:
    item = _item()

    assert item.evidence_id == "evidence-001"
    assert item.relation == EvidenceRelation.CANDIDATE
    assert item.retrieval_score == 0.9
    assert item.retrieval_rank == 1


def test_evidence_preserves_representation_provenance() -> None:
    item = _item()

    assert item.representation_ref == "representation-001"
    assert item.knowledge_unit_ref == "unit-001"
    assert item.derivation_id == "derivation-001"


def test_evidence_preserves_resource_provenance() -> None:
    item = _item()

    assert item.knowledge_scope_ref == "scope-001"
    assert item.resource_ref == "resource-001"
    assert item.revision_ref == "revision-001"


def test_evidence_preserves_content() -> None:
    item = _item(
        content=b"policy evidence",
    )

    assert item.content == b"policy evidence"
    assert item.media_type == "text/plain"


def test_size_bytes_returns_content_size() -> None:
    content = b"policy evidence"
    item = _item(
        content=content,
    )

    assert item.size_bytes == len(content)


def test_empty_evidence_content_is_supported() -> None:
    item = _item(
        content=b"",
    )

    assert item.content == b""
    assert item.size_bytes == 0


@pytest.mark.parametrize(
    "relation",
    tuple(EvidenceRelation),
)
def test_all_evidence_relations_are_supported(
    relation: EvidenceRelation,
) -> None:
    item = _item(
        relation=relation,
    )

    assert item.relation == relation


def test_integer_retrieval_score_is_normalized() -> None:
    item = _item(
        score=1,
    )

    assert item.retrieval_score == 1.0
    assert isinstance(
        item.retrieval_score,
        float,
    )


@pytest.mark.parametrize(
    "score",
    (
        math.inf,
        -math.inf,
        math.nan,
    ),
)
def test_non_finite_retrieval_score_is_rejected(
    score: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="retrieval_score must be finite",
    ):
        _item(
            score=score,
        )


@pytest.mark.parametrize(
    "score",
    (
        True,
        "1.0",
        None,
    ),
)
def test_invalid_retrieval_score_type_is_rejected(
    score: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="retrieval_score must be a number",
    ):
        _item(
            score=score,
        )


@pytest.mark.parametrize(
    "rank",
    (
        0,
        -1,
    ),
)
def test_non_positive_retrieval_rank_is_rejected(
    rank: int,
) -> None:
    with pytest.raises(
        ValueError,
        match="retrieval_rank must be greater than zero",
    ):
        _item(
            rank=rank,
        )


@pytest.mark.parametrize(
    "rank",
    (
        True,
        1.5,
        "1",
        None,
    ),
)
def test_invalid_retrieval_rank_type_is_rejected(
    rank: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="retrieval_rank must be an int",
    ):
        _item(
            rank=rank,
        )


def test_non_bytes_content_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match="content must be bytes",
    ):
        _item(
            content="invalid-content",
        )


def test_invalid_evidence_relation_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "relation must be an instance of "
            "EvidenceRelation"
        ),
    ):
        _item(
            relation="CANDIDATE",
        )


def test_required_text_values_are_normalized() -> None:
    item = EvidenceItem(
        evidence_id="  evidence-001  ",
        representation_ref="  representation-001  ",
        knowledge_unit_ref="  unit-001  ",
        derivation_id="  derivation-001  ",
        knowledge_scope_ref="  scope-001  ",
        resource_ref="  resource-001  ",
        revision_ref="  revision-001  ",
        content=b"evidence",
        media_type="  text/plain  ",
        relation=EvidenceRelation.CANDIDATE,
        retrieval_score=0.9,
        retrieval_rank=1,
    )

    assert item.evidence_id == "evidence-001"
    assert item.representation_ref == "representation-001"
    assert item.knowledge_unit_ref == "unit-001"
    assert item.derivation_id == "derivation-001"
    assert item.knowledge_scope_ref == "scope-001"
    assert item.resource_ref == "resource-001"
    assert item.revision_ref == "revision-001"
    assert item.media_type == "text/plain"


def test_evidence_item_is_immutable() -> None:
    item = _item()

    with pytest.raises(FrozenInstanceError):
        item.retrieval_rank = 2
