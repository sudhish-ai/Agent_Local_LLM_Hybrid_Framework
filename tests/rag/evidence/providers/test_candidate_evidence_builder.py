# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF CandidateEvidenceBuilder.
#
# Responsibilities:
# - Validate stable builder identity and version.
# - Validate deterministic candidate Evidence construction.
# - Validate representation and Knowledge provenance preservation.
# - Validate retrieved content preservation.
# - Validate retrieval score and rank preservation.
# - Validate provenance mismatch rejection.
# - Validate invalid input rejection.
#
# Must Not:
# - Perform retrieval or reranking.
# - Treat candidate Evidence as verified support.
# - Determine Evidence sufficiency.
# - Resolve Evidence conflicts.
# - Construct Context or generate answers.
# - Test Evidence Intelligence.
# - Depend on external RAG frameworks.

import pytest

from alhf.rag.evidence.contracts.evidence_item import (
    EvidenceItem,
    EvidenceRelation,
)
from alhf.rag.evidence.providers.candidate_evidence_builder import (
    CandidateEvidenceBuilder,
)
from alhf.rag.representation.contracts.knowledge_representation import (
    KnowledgeRepresentation,
    RepresentationKind,
)
from alhf.rag.retrieval.contracts.retrieval_result import (
    RetrievalResult,
)


def _representation(
    **overrides,
) -> KnowledgeRepresentation:
    values = {
        "representation_id": "representation-001",
        "knowledge_unit_ref": "unit-001",
        "derivation_id": "derivation-001",
        "knowledge_scope_ref": "scope-001",
        "resource_ref": "resource-001",
        "revision_ref": "revision-001",
        "kind": RepresentationKind.LEXICAL,
        "payload": b"enterprise evidence",
        "media_type": "text/plain",
        "strategy_ref": "deterministic-text-representation",
        "strategy_version": "1.0",
    }
    values.update(
        overrides
    )

    return KnowledgeRepresentation(
        **values
    )


def _result(
    **overrides,
) -> RetrievalResult:
    values = {
        "representation_ref": "representation-001",
        "representation_kind": RepresentationKind.LEXICAL,
        "knowledge_unit_ref": "unit-001",
        "derivation_id": "derivation-001",
        "knowledge_scope_ref": "scope-001",
        "resource_ref": "resource-001",
        "revision_ref": "revision-001",
        "index_ref": "knowledge-index",
        "index_version": "v1",
        "score": 0.9,
        "rank": 1,
    }
    values.update(
        overrides
    )

    return RetrievalResult(
        **values
    )


def _build(
    *,
    result=None,
    representation=None,
) -> EvidenceItem:
    return CandidateEvidenceBuilder().build(
        result=result or _result(),
        representation=representation or _representation(),
    )


def test_builder_exposes_stable_identity() -> None:
    builder = CandidateEvidenceBuilder()

    assert builder.builder_ref == "candidate-evidence-builder"
    assert builder.builder_version == "1.0"


def test_build_returns_evidence_item() -> None:
    item = _build()

    assert isinstance(
        item,
        EvidenceItem,
    )


def test_build_creates_candidate_evidence() -> None:
    item = _build()

    assert item.relation == EvidenceRelation.CANDIDATE


def test_build_preserves_retrieval_provenance() -> None:
    item = _build()

    assert item.representation_ref == "representation-001"
    assert item.knowledge_unit_ref == "unit-001"
    assert item.derivation_id == "derivation-001"
    assert item.retrieval_score == 0.9
    assert item.retrieval_rank == 1


def test_build_preserves_resource_provenance() -> None:
    item = _build()

    assert item.knowledge_scope_ref == "scope-001"
    assert item.resource_ref == "resource-001"
    assert item.revision_ref == "revision-001"


def test_build_preserves_representation_content() -> None:
    item = _build()

    assert item.content == b"enterprise evidence"
    assert item.media_type == "text/plain"


def test_evidence_identity_is_deterministic() -> None:
    first = _build()
    second = _build()

    assert first.evidence_id == second.evidence_id
    assert first.evidence_id.startswith(
        "evidence:"
    )


def test_retrieval_rank_changes_evidence_identity() -> None:
    first = _build()

    second = _build(
        result=_result(
            rank=2,
        )
    )

    assert first.evidence_id != second.evidence_id


@pytest.mark.parametrize(
    ("field_name", "value", "label"),
    (
        (
            "representation_ref",
            "representation-x",
            "representation",
        ),
        (
            "knowledge_unit_ref",
            "unit-x",
            "Knowledge Unit",
        ),
        (
            "derivation_id",
            "derivation-x",
            "derivation",
        ),
        (
            "knowledge_scope_ref",
            "scope-x",
            "Knowledge scope",
        ),
        (
            "resource_ref",
            "resource-x",
            "resource",
        ),
        (
            "revision_ref",
            "revision-x",
            "revision",
        ),
    ),
)
def test_provenance_mismatch_is_rejected(
    field_name: str,
    value: str,
    label: str,
) -> None:
    result = _result(
        **{
            field_name: value,
        }
    )

    with pytest.raises(
        ValueError,
        match=(
            f"{label} provenance must match "
            "representation"
        ),
    ):
        _build(
            result=result,
        )


def test_invalid_retrieval_result_is_rejected() -> None:
    builder = CandidateEvidenceBuilder()

    with pytest.raises(
        TypeError,
        match="result must be an instance of RetrievalResult",
    ):
        builder.build(
            result="invalid-result",
            representation=_representation(),
        )


def test_invalid_representation_is_rejected() -> None:
    builder = CandidateEvidenceBuilder()

    with pytest.raises(
        TypeError,
        match=(
            "representation must be an instance of "
            "KnowledgeRepresentation"
        ),
    ):
        builder.build(
            result=_result(),
            representation="invalid-representation",
        )
