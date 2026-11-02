# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF EvidenceService.
#
# Responsibilities:
# - Validate Evidence construction orchestration.
# - Validate representation resolution.
# - Validate incremental Evidence construction.
# - Validate Evidence provenance continuity.
# - Validate unresolved representation behavior.
# - Validate invalid builder, resolver, and result behavior.
#
# Must Not:
# - Perform retrieval or reranking.
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
from alhf.rag.evidence.evidence_service import (
    EvidenceService,
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


def _representation() -> KnowledgeRepresentation:
    return KnowledgeRepresentation(
        representation_id="representation-001",
        knowledge_unit_ref="unit-001",
        derivation_id="derivation-001",
        knowledge_scope_ref="scope-001",
        resource_ref="resource-001",
        revision_ref="revision-001",
        kind=RepresentationKind.LEXICAL,
        payload=b"enterprise evidence",
        media_type="text/plain",
        strategy_ref="deterministic-text-representation",
        strategy_version="1.0",
    )


def _result() -> RetrievalResult:
    return RetrievalResult(
        representation_ref="representation-001",
        representation_kind=RepresentationKind.LEXICAL,
        knowledge_unit_ref="unit-001",
        derivation_id="derivation-001",
        knowledge_scope_ref="scope-001",
        resource_ref="resource-001",
        revision_ref="revision-001",
        index_ref="knowledge-index",
        index_version="v1",
        score=0.9,
        rank=1,
    )


def _service() -> EvidenceService:
    representation = _representation()

    def resolve(
        representation_ref: str,
    ):
        if representation_ref == representation.representation_id:
            return representation

        return None

    return EvidenceService(
        builder=CandidateEvidenceBuilder(),
        resolve_representation=resolve,
    )


def test_create_evidence_service() -> None:
    assert isinstance(
        _service(),
        EvidenceService,
    )


def test_build_returns_evidence_item() -> None:
    item = _service().build(
        result=_result()
    )

    assert isinstance(
        item,
        EvidenceItem,
    )


def test_build_creates_candidate_evidence() -> None:
    item = _service().build(
        result=_result()
    )

    assert item.relation == EvidenceRelation.CANDIDATE


def test_build_resolves_representation_content() -> None:
    item = _service().build(
        result=_result()
    )

    assert item.content == b"enterprise evidence"
    assert item.media_type == "text/plain"


def test_build_preserves_retrieval_provenance() -> None:
    item = _service().build(
        result=_result()
    )

    assert item.representation_ref == "representation-001"
    assert item.knowledge_unit_ref == "unit-001"
    assert item.derivation_id == "derivation-001"
    assert item.retrieval_score == 0.9
    assert item.retrieval_rank == 1


def test_build_preserves_resource_provenance() -> None:
    item = _service().build(
        result=_result()
    )

    assert item.knowledge_scope_ref == "scope-001"
    assert item.resource_ref == "resource-001"
    assert item.revision_ref == "revision-001"


def test_build_many_returns_incremental_evidence() -> None:
    results = iter(
        (
            _result(),
        )
    )

    items = tuple(
        _service().build_many(
            results=results
        )
    )

    assert len(items) == 1
    assert isinstance(
        items[0],
        EvidenceItem,
    )


def test_missing_representation_is_rejected() -> None:
    service = EvidenceService(
        builder=CandidateEvidenceBuilder(),
        resolve_representation=lambda reference: None,
    )

    with pytest.raises(
        LookupError,
        match="representation not found: representation-001",
    ):
        service.build(
            result=_result()
        )


def test_invalid_resolved_representation_is_rejected() -> None:
    service = EvidenceService(
        builder=CandidateEvidenceBuilder(),
        resolve_representation=lambda reference: "invalid",
    )

    with pytest.raises(
        TypeError,
        match=(
            "resolver must return "
            "KnowledgeRepresentation or None"
        ),
    ):
        service.build(
            result=_result()
        )


def test_invalid_builder_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match="builder must be an instance of EvidenceBuilder",
    ):
        EvidenceService(
            builder="invalid-builder",
            resolve_representation=lambda reference: None,
        )


def test_invalid_resolver_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match="resolve_representation must be callable",
    ):
        EvidenceService(
            builder=CandidateEvidenceBuilder(),
            resolve_representation="invalid-resolver",
        )


def test_invalid_retrieval_result_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match="result must be an instance of RetrievalResult",
    ):
        _service().build(
            result="invalid-result"
        )


def test_build_many_requires_iterator() -> None:
    with pytest.raises(
        TypeError,
        match="results must be an Iterator",
    ):
        tuple(
            _service().build_many(
                results=()
            )
        )


def test_repeated_build_is_deterministic() -> None:
    service = _service()
    result = _result()

    first = service.build(
        result=result
    )
    second = service.build(
        result=result
    )

    assert first == second
    assert first.evidence_id == second.evidence_id
