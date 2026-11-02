# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF EvidenceBuilder interface.
#
# Responsibilities:
# - Validate the abstract Evidence-builder boundary.
# - Validate stable builder identity and version.
# - Validate EvidenceItem construction.
# - Validate retrieval provenance preservation.
# - Validate representation content preservation.
# - Validate V1 candidate-Evidence semantics.
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
from alhf.rag.evidence.interfaces.evidence_builder import (
    EvidenceBuilder,
)
from alhf.rag.representation.contracts.knowledge_representation import (
    KnowledgeRepresentation,
    RepresentationKind,
)
from alhf.rag.retrieval.contracts.retrieval_result import (
    RetrievalResult,
)


class StubEvidenceBuilder(EvidenceBuilder):
    """Minimal concrete Evidence builder for interface testing."""

    @property
    def builder_ref(self) -> str:
        return "stub-evidence-builder"

    @property
    def builder_version(self) -> str:
        return "1.0"

    def build(
        self,
        *,
        result: RetrievalResult,
        representation: KnowledgeRepresentation,
    ) -> EvidenceItem:
        return EvidenceItem(
            evidence_id="evidence-001",
            representation_ref=result.representation_ref,
            knowledge_unit_ref=result.knowledge_unit_ref,
            derivation_id=result.derivation_id,
            knowledge_scope_ref=result.knowledge_scope_ref,
            resource_ref=result.resource_ref,
            revision_ref=result.revision_ref,
            content=representation.payload,
            media_type=representation.media_type,
            relation=EvidenceRelation.CANDIDATE,
            retrieval_score=result.score,
            retrieval_rank=result.rank,
        )


class MissingBuildEvidenceBuilder(EvidenceBuilder):
    """Invalid builder intentionally missing build behavior."""

    @property
    def builder_ref(self) -> str:
        return "missing-build"

    @property
    def builder_version(self) -> str:
        return "1.0"


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


def test_evidence_builder_is_abstract() -> None:
    with pytest.raises(TypeError):
        EvidenceBuilder()


def test_missing_build_prevents_instantiation() -> None:
    with pytest.raises(TypeError):
        MissingBuildEvidenceBuilder()


def test_concrete_builder_can_be_instantiated() -> None:
    assert isinstance(
        StubEvidenceBuilder(),
        EvidenceBuilder,
    )


def test_builder_exposes_stable_identity() -> None:
    builder = StubEvidenceBuilder()

    assert builder.builder_ref == "stub-evidence-builder"
    assert builder.builder_version == "1.0"


def test_build_returns_evidence_item() -> None:
    item = StubEvidenceBuilder().build(
        result=_result(),
        representation=_representation(),
    )

    assert isinstance(
        item,
        EvidenceItem,
    )


def test_build_preserves_retrieval_provenance() -> None:
    item = StubEvidenceBuilder().build(
        result=_result(),
        representation=_representation(),
    )

    assert item.representation_ref == "representation-001"
    assert item.knowledge_unit_ref == "unit-001"
    assert item.derivation_id == "derivation-001"
    assert item.retrieval_score == 0.9
    assert item.retrieval_rank == 1


def test_build_preserves_resource_provenance() -> None:
    item = StubEvidenceBuilder().build(
        result=_result(),
        representation=_representation(),
    )

    assert item.knowledge_scope_ref == "scope-001"
    assert item.resource_ref == "resource-001"
    assert item.revision_ref == "revision-001"


def test_build_uses_representation_content() -> None:
    item = StubEvidenceBuilder().build(
        result=_result(),
        representation=_representation(),
    )

    assert item.content == b"enterprise evidence"
    assert item.media_type == "text/plain"


def test_v1_builder_creates_candidate_evidence() -> None:
    item = StubEvidenceBuilder().build(
        result=_result(),
        representation=_representation(),
    )

    assert item.relation == EvidenceRelation.CANDIDATE
