# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines one provider-neutral retrieval result returned by the ALHF
# Knowledge Foundation retrieval layer.
#
# Problem Solved:
# Retrieval candidates must remain independent from physical index
# technologies while preserving enough Knowledge provenance for
# downstream ranking, evidence construction, and failure analysis.
#
# Responsibilities:
# - Identify the retrieved Knowledge representation.
# - Preserve Knowledge Unit and derivation provenance.
# - Preserve Knowledge scope, resource, and revision provenance.
# - Preserve representation kind.
# - Preserve retrieval score and rank.
# - Record the logical index and exact index version searched.
# - Provide immutable provider-neutral retrieval semantics.
#
# Must Not:
# - Treat a retrieval result as validated Evidence.
# - Contain provider-specific database result objects.
# - Perform reranking or evidence construction.
# - Perform context construction or generation.
# - Apply authorization policy.
# - Implement adaptive retrieval or Retrieval Intelligence.
# - Assume dense-vector retrieval is the only retrieval mode.
# - Depend on external RAG or orchestration frameworks.
#
# Architectural Position:
# - Stable output boundary of candidate retrieval.
# - Separates retrieval candidates from Evidence.
# - Preserves lineage required for downstream RCA.
#
# Reuse Value:
# - Lexical retrieval.
# - Dense and sparse retrieval.
# - Hybrid retrieval.
# - Structured and graph retrieval.
# - Future Agentic RAG retrieval.
#
# Future Extensibility:
# - Reranking can consume this contract without provider knowledge.
# - Evidence construction can validate candidates independently.
# - Multiple retrieval strategies can emit the same result contract.
# - Additional retrieval intelligence can evolve above this boundary.

from __future__ import annotations

import math
from dataclasses import dataclass

from alhf.rag.representation.contracts.knowledge_representation import (
    RepresentationKind,
)


@dataclass(frozen=True, slots=True)
class RetrievalResult:
    """Immutable provider-neutral retrieval candidate."""

    representation_ref: str
    representation_kind: RepresentationKind
    knowledge_unit_ref: str
    derivation_id: str
    knowledge_scope_ref: str
    resource_ref: str
    revision_ref: str
    index_ref: str
    index_version: str
    score: float
    rank: int

    def __post_init__(self) -> None:
        fields = (
            "representation_ref",
            "knowledge_unit_ref",
            "derivation_id",
            "knowledge_scope_ref",
            "resource_ref",
            "revision_ref",
            "index_ref",
            "index_version",
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
            self.representation_kind,
            RepresentationKind,
        ):
            raise TypeError(
                "representation_kind must be an instance of "
                "RepresentationKind"
            )

        if isinstance(
            self.score,
            bool,
        ) or not isinstance(
            self.score,
            (int, float),
        ):
            raise TypeError(
                "score must be a number"
            )

        normalized_score = float(
            self.score
        )

        if not math.isfinite(
            normalized_score
        ):
            raise ValueError(
                "score must be finite"
            )

        object.__setattr__(
            self,
            "score",
            normalized_score,
        )

        if isinstance(
            self.rank,
            bool,
        ) or not isinstance(
            self.rank,
            int,
        ):
            raise TypeError(
                "rank must be an int"
            )

        if self.rank < 1:
            raise ValueError(
                "rank must be greater than zero"
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
