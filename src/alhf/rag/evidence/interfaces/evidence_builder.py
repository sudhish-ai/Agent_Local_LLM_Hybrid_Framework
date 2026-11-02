# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the universal Evidence-construction boundary used by the
# ALHF Knowledge Foundation Evidence layer.
#
# Problem Solved:
# RetrievalResult identifies a ranked candidate but does not contain
# the governed content required by downstream Evidence consumers.
# ALHF needs an explicit boundary that combines retrieval provenance
# with the originating KnowledgeRepresentation.
#
# Responsibilities:
# - Accept one RetrievalResult candidate.
# - Accept its originating KnowledgeRepresentation.
# - Produce one provider-neutral EvidenceItem.
# - Expose stable Evidence-builder identity and version.
# - Preserve Knowledge and retrieval provenance.
# - Keep Evidence construction independent from retrieval algorithms.
#
# Must Not:
# - Perform retrieval or reranking.
# - Retrieve representation storage directly.
# - Determine Evidence-set sufficiency.
# - Claim candidate Evidence is factually supporting by default.
# - Resolve contradictions between Evidence items.
# - Construct model Context or generate answers.
# - Implement Evidence Intelligence or adaptive verification.
# - Depend on external RAG or orchestration frameworks.
#
# Architectural Position:
# - Stable boundary between retrieval candidates and Evidence artifacts.
# - Keeps RetrievalResult distinct from EvidenceItem.
# - Preserves provenance required for explanation and production RCA.
#
# Reuse Value:
# - V1 candidate Evidence construction.
# - Future Evidence verification.
# - GraphRAG Evidence construction.
# - Agentic RAG Evidence construction.
# - Evidence-backed agent reasoning.
#
# Future Extensibility:
# - Different Evidence builders can implement richer verification.
# - Authority, freshness, and conflict analysis can evolve separately.
# - Evidence sufficiency remains a downstream governed decision.
# - External implementations can remain behind this ALHF boundary.

from __future__ import annotations

from abc import ABC, abstractmethod

from alhf.rag.evidence.contracts.evidence_item import (
    EvidenceItem,
)
from alhf.rag.representation.contracts.knowledge_representation import (
    KnowledgeRepresentation,
)
from alhf.rag.retrieval.contracts.retrieval_result import (
    RetrievalResult,
)


class EvidenceBuilder(ABC):
    """Universal provider-neutral Evidence-construction boundary."""

    @property
    @abstractmethod
    def builder_ref(self) -> str:
        """Return the stable logical Evidence-builder identifier."""

        raise NotImplementedError

    @property
    @abstractmethod
    def builder_version(self) -> str:
        """Return the stable Evidence-builder behavior version."""

        raise NotImplementedError

    @abstractmethod
    def build(
        self,
        *,
        result: RetrievalResult,
        representation: KnowledgeRepresentation,
    ) -> EvidenceItem:
        """
        Construct one Evidence item from one retrieval candidate.

        Implementations must validate that retrieval and representation
        provenance correspond before constructing Evidence.
        """

        raise NotImplementedError
