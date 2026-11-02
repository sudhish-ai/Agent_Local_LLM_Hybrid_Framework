# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines one provider-neutral Evidence item constructed from retrieved
# ALHF Knowledge.
#
# Problem Solved:
# Retrieval relevance does not establish evidentiary support. ALHF needs
# an explicit artifact separating retrieved candidates from Evidence
# consumed by downstream Context and agent reasoning.
#
# Responsibilities:
# - Identify one Evidence item.
# - Preserve representation and Knowledge Unit provenance.
# - Preserve derivation, resource, and revision provenance.
# - Preserve evidence content independently from retrieval technology.
# - Record the Evidence relation.
# - Preserve originating retrieval score and rank.
# - Provide immutable provider-neutral semantics.
#
# Must Not:
# - Treat retrieval score as proof of evidentiary support.
# - Perform retrieval or reranking.
# - Determine evidence-set sufficiency.
# - Resolve contradictions between Evidence items.
# - Construct model Context or generate answers.
# - Implement Evidence Intelligence or adaptive verification.
# - Depend on external RAG or orchestration frameworks.
#
# Architectural Position:
# - Stable boundary between RetrievalResult and downstream Evidence use.
# - Keeps retrieval candidates distinct from evidentiary artifacts.
# - Preserves provenance required for explanation and RCA.
#
# Reuse Value:
# - V1 Standard RAG Evidence construction.
# - Future verified supporting or refuting Evidence.
# - GraphRAG and Agentic RAG Evidence.
# - Evidence-backed agent decisions.
#
# Future Extensibility:
# - Evidence verification can promote CANDIDATE to richer relations.
# - Evidence-set sufficiency remains a separate concern.
# - Authority, freshness, and conflict intelligence can evolve later.
# - Citation construction can consume this stable provenance boundary.

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum


class EvidenceRelation(str, Enum):
    """Relationship between Evidence and the information need."""

    CANDIDATE = "CANDIDATE"
    SUPPORTING = "SUPPORTING"
    REFUTING = "REFUTING"
    CONFLICTING = "CONFLICTING"


@dataclass(frozen=True, slots=True)
class EvidenceItem:
    """Immutable provider-neutral Evidence artifact."""

    evidence_id: str
    representation_ref: str
    knowledge_unit_ref: str
    derivation_id: str
    knowledge_scope_ref: str
    resource_ref: str
    revision_ref: str
    content: bytes
    media_type: str
    relation: EvidenceRelation
    retrieval_score: float
    retrieval_rank: int

    def __post_init__(self) -> None:
        fields = (
            "evidence_id",
            "representation_ref",
            "knowledge_unit_ref",
            "derivation_id",
            "knowledge_scope_ref",
            "resource_ref",
            "revision_ref",
            "media_type",
        )

        for field_name in fields:
            normalized = self._required_text(
                value=getattr(
                    self,
                    field_name,
                ),
                field_name=field_name,
            )
            object.__setattr__(
                self,
                field_name,
                normalized,
            )

        if not isinstance(
            self.content,
            bytes,
        ):
            raise TypeError(
                "content must be bytes"
            )

        if not isinstance(
            self.relation,
            EvidenceRelation,
        ):
            raise TypeError(
                "relation must be an instance of EvidenceRelation"
            )

        self._validate_score()
        self._validate_rank()

    @property
    def size_bytes(self) -> int:
        """Return Evidence content size without copying it."""

        return len(
            self.content
        )

    def _validate_score(self) -> None:
        if isinstance(
            self.retrieval_score,
            bool,
        ) or not isinstance(
            self.retrieval_score,
            (int, float),
        ):
            raise TypeError(
                "retrieval_score must be a number"
            )

        score = float(
            self.retrieval_score
        )

        if not math.isfinite(
            score
        ):
            raise ValueError(
                "retrieval_score must be finite"
            )

        object.__setattr__(
            self,
            "retrieval_score",
            score,
        )

    def _validate_rank(self) -> None:
        if isinstance(
            self.retrieval_rank,
            bool,
        ) or not isinstance(
            self.retrieval_rank,
            int,
        ):
            raise TypeError(
                "retrieval_rank must be an int"
            )

        if self.retrieval_rank < 1:
            raise ValueError(
                "retrieval_rank must be greater than zero"
            )

    @staticmethod
    def _required_text(
        *,
        value: str,
        field_name: str,
    ) -> str:
        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                f"{field_name} must be a string"
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                f"{field_name} cannot be empty"
            )

        return normalized
