# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides deterministic candidate-Evidence construction for ALHF RAG V1.
#
# Problem Solved:
# RetrievalResult identifies a ranked candidate while its originating
# KnowledgeRepresentation owns the retrieved content. V1 requires a
# deterministic mechanism to combine both into governed Evidence.
#
# Responsibilities:
# - Accept one RetrievalResult and KnowledgeRepresentation.
# - Validate representation and Knowledge provenance correspondence.
# - Preserve retrieved content in the Evidence item.
# - Preserve originating retrieval score and rank.
# - Classify V1 output explicitly as CANDIDATE Evidence.
# - Generate deterministic Evidence identity.
# - Preserve stable builder identity and version.
#
# Must Not:
# - Perform retrieval or reranking.
# - Claim candidate Evidence is supporting or factually sufficient.
# - Determine Evidence sufficiency.
# - Resolve Evidence conflicts.
# - Construct Context or generate answers.
# - Implement Evidence Intelligence or adaptive verification.
# - Depend on external RAG or orchestration frameworks.
#
# Architectural Position:
# - Concrete V1 implementation of EvidenceBuilder.
# - Converts retrieved candidates into governed Evidence artifacts.
# - Protects provenance before downstream Evidence consumption.
#
# Reuse Value:
# - V1 Standard RAG Evidence construction.
# - Deterministic local-first E2E execution.
# - Evidence lineage and production failure analysis.
# - Future Evidence verification baselines.
#
# Future Extensibility:
# - Verified builders can classify supporting or refuting Evidence.
# - Authority, freshness, and conflict analysis can evolve separately.
# - Evidence sufficiency remains a downstream governed capability.
# - GraphRAG and Agentic RAG builders can use the same Evidence contract.

from __future__ import annotations

import hashlib

from alhf.rag.evidence.contracts.evidence_item import (
    EvidenceItem,
    EvidenceRelation,
)
from alhf.rag.evidence.interfaces.evidence_builder import (
    EvidenceBuilder,
)
from alhf.rag.representation.contracts.knowledge_representation import (
    KnowledgeRepresentation,
)
from alhf.rag.retrieval.contracts.retrieval_result import (
    RetrievalResult,
)


class CandidateEvidenceBuilder(EvidenceBuilder):
    """Construct deterministic V1 candidate Evidence."""

    _BUILDER_REF = "candidate-evidence-builder"
    _BUILDER_VERSION = "1.0"

    @property
    def builder_ref(self) -> str:
        return self._BUILDER_REF

    @property
    def builder_version(self) -> str:
        return self._BUILDER_VERSION

    def build(
        self,
        *,
        result: RetrievalResult,
        representation: KnowledgeRepresentation,
    ) -> EvidenceItem:
        if not isinstance(
            result,
            RetrievalResult,
        ):
            raise TypeError(
                "result must be an instance of RetrievalResult"
            )

        if not isinstance(
            representation,
            KnowledgeRepresentation,
        ):
            raise TypeError(
                "representation must be an instance of "
                "KnowledgeRepresentation"
            )

        self._validate_provenance(
            result=result,
            representation=representation,
        )

        return EvidenceItem(
            evidence_id=self._evidence_id(
                result=result,
                representation=representation,
            ),
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

    @staticmethod
    def _validate_provenance(
        *,
        result: RetrievalResult,
        representation: KnowledgeRepresentation,
    ) -> None:
        pairs = (
            (
                result.representation_ref,
                representation.representation_id,
                "representation",
            ),
            (
                result.knowledge_unit_ref,
                representation.knowledge_unit_ref,
                "Knowledge Unit",
            ),
            (
                result.derivation_id,
                representation.derivation_id,
                "derivation",
            ),
            (
                result.knowledge_scope_ref,
                representation.knowledge_scope_ref,
                "Knowledge scope",
            ),
            (
                result.resource_ref,
                representation.resource_ref,
                "resource",
            ),
            (
                result.revision_ref,
                representation.revision_ref,
                "revision",
            ),
        )

        for actual, expected, label in pairs:
            if actual != expected:
                raise ValueError(
                    f"{label} provenance must match representation"
                )

    def _evidence_id(
        self,
        *,
        result: RetrievalResult,
        representation: KnowledgeRepresentation,
    ) -> str:
        material = (
            f"{result.representation_ref}|"
            f"{result.knowledge_unit_ref}|"
            f"{result.derivation_id}|"
            f"{result.rank}|"
            f"{self.builder_ref}|"
            f"{self.builder_version}|"
            f"{representation.revision_ref}"
        ).encode("utf-8")

        digest = hashlib.sha256(
            material
        ).hexdigest()

        return f"evidence:{digest}"
