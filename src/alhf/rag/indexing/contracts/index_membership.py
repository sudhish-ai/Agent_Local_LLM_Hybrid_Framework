# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines provider-neutral membership of one governed representation in
# one ALHF Knowledge index.
#
# Problem Solved:
# Retrieval indexes are derived release artifacts and must not become
# Knowledge truth. ALHF requires explicit traceability between a
# representation and the logical index version in which it participates.
#
# Responsibilities:
# - Identify one index membership deterministically.
# - Reference the indexed Knowledge representation.
# - Preserve Knowledge scope, resource, and revision provenance.
# - Preserve derivation provenance.
# - Identify the logical index and exact index version.
# - Preserve representation kind for compatibility validation.
# - Provide immutable provider-neutral membership semantics.
#
# Must Not:
# - Store vector-database-specific record identifiers.
# - Store physical collection, namespace, shard, or table names.
# - Duplicate representation payloads.
# - Perform index writes or provider operations.
# - Perform retrieval, reranking, or context construction.
# - Treat the index as Knowledge truth.
# - Implement promotion, rollback, or lifecycle orchestration.
# - Implement concurrency, batching, or NFT execution policy.
# - Depend on external RAG or orchestration frameworks.
#
# Architectural Position:
# - Stable boundary between KnowledgeRepresentation and index providers.
# - Makes representation-to-index participation explicit and traceable.
# - Keeps physical index technology outside governed Knowledge contracts.
#
# Reuse Value:
# - Dense indexes.
# - Sparse and lexical indexes.
# - Structured and graph indexes.
# - Local, cloud, and hybrid index providers.
# - Candidate and production index versions.
#
# Future Extensibility:
# - Multiple index versions may reference the same representation.
# - Candidate indexes may coexist with active versions.
# - Provider adapters can map membership into physical index records.
# - Lifecycle, promotion, rollback, and reconciliation remain separate.
# - Partitioned and distributed indexing can evolve without changing
#   this contract.

from __future__ import annotations

from dataclasses import dataclass

from alhf.rag.representation.contracts.knowledge_representation import (
    RepresentationKind,
)


@dataclass(frozen=True, slots=True)
class IndexMembership:
    """Immutable membership of one representation in one index version."""

    membership_id: str
    index_ref: str
    index_version: str
    representation_ref: str
    representation_kind: RepresentationKind
    knowledge_unit_ref: str
    derivation_id: str
    knowledge_scope_ref: str
    resource_ref: str
    revision_ref: str

    def __post_init__(self) -> None:
        fields = (
            "membership_id",
            "index_ref",
            "index_version",
            "representation_ref",
            "knowledge_unit_ref",
            "derivation_id",
            "knowledge_scope_ref",
            "resource_ref",
            "revision_ref",
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

    @staticmethod
    def _required_text(
        *,
        value: str,
        field_name: str,
    ) -> str:
        """Validate and normalize required membership text."""

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
