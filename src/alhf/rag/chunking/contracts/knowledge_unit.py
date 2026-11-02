# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the stable Knowledge Unit produced by ALHF derivation and
# chunking for downstream representation, indexing, and retrieval.
#
# Problem Solved:
# Downstream Knowledge stages require bounded semantic units without
# depending on physical sources, original file formats, parsers, or
# normalization implementations.
#
# Responsibilities:
# - Identify one derived Knowledge Unit.
# - Preserve source resource and revision identity.
# - Preserve the canonical artifact from which the unit was derived.
# - Preserve derivation identity and sequence position.
# - Preserve bounded unit content and semantic content kind.
# - Preserve derivation strategy identity and version.
# - Provide immutable downstream Knowledge semantics.
#
# Must Not:
# - Acquire or parse physical resources.
# - Contain source-specific or file-format-specific behavior.
# - Normalize canonical content.
# - Generate embeddings or representations.
# - Perform indexing, retrieval, reranking, or context construction.
# - Contain embedding-provider or vector-store behavior.
# - Materialize collections of Knowledge Units.
# - Implement concurrency or NFT execution policy.
# - Contain Standard RAG, GraphRAG, or Agentic RAG retrieval logic.
#
# Architectural Position:
# - Stable output contract of the derivation/chunking boundary.
# - Consumed by representation, indexing, and retrieval foundations.
# - Independent from source and input-format technologies.
#
# Reuse Value:
# - Standard RAG chunking.
# - GraphRAG Knowledge units.
# - Agentic RAG evidence units.
# - Hybrid and future retrieval strategies.
#
# Future Extensibility:
# - Different derivation strategies can produce the same contract.
# - Hierarchical and semantic derivation can evolve independently.
# - Graph relationships can reference Knowledge Unit identity.
# - Representation providers can change without redefining units.
# - Parallel derivation can evolve behind execution policies.

from __future__ import annotations

from dataclasses import dataclass

from alhf.rag.ingestion.contracts.canonical_content import (
    CanonicalContentKind,
)
from alhf.rag.ingestion.contracts.resource_identity import (
    ResourceIdentity,
)


@dataclass(frozen=True, slots=True)
class KnowledgeUnit:
    """
    Immutable bounded unit derived from canonical Knowledge content.

    unit_id:
        Stable identity of this derived Knowledge Unit.

    identity:
        Original logical-resource and exact-revision identity.

    canonical_artifact_ref:
        Provenance reference to the canonical content used for derivation.

    derivation_id:
        Identity of the concrete derivation execution.

    sequence:
        Zero-based position of this unit within its derivation.

    content:
        Bounded Knowledge content represented as bytes.

    content_kind:
        Universal semantic category inherited from canonical content.

    media_type:
        Media type of the unit representation.

    strategy_ref / strategy_version:
        Reproducibility identity of the derivation strategy.
    """

    unit_id: str
    identity: ResourceIdentity
    canonical_artifact_ref: str
    derivation_id: str
    sequence: int
    content: bytes
    content_kind: CanonicalContentKind
    media_type: str
    strategy_ref: str
    strategy_version: str

    def __post_init__(self) -> None:
        if not isinstance(self.identity, ResourceIdentity):
            raise TypeError(
                "identity must be an instance of ResourceIdentity"
            )

        if isinstance(self.sequence, bool) or not isinstance(
            self.sequence,
            int,
        ):
            raise TypeError(
                "sequence must be an int"
            )

        if self.sequence < 0:
            raise ValueError(
                "sequence cannot be negative"
            )

        if not isinstance(self.content, bytes):
            raise TypeError(
                "content must be bytes"
            )

        if not isinstance(
            self.content_kind,
            CanonicalContentKind,
        ):
            raise TypeError(
                "content_kind must be an instance of "
                "CanonicalContentKind"
            )

        fields = (
            "unit_id",
            "canonical_artifact_ref",
            "derivation_id",
            "media_type",
            "strategy_ref",
            "strategy_version",
        )

        for field_name in fields:
            value = self._required_text(
                value=getattr(self, field_name),
                field_name=field_name,
            )
            object.__setattr__(
                self,
                field_name,
                value,
            )

    @property
    def resource_ref(self) -> str:
        """Return the originating logical-resource reference."""

        return self.identity.resource_ref

    @property
    def revision_ref(self) -> str:
        """Return the originating exact-revision reference."""

        return self.identity.revision_ref

    @property
    def knowledge_scope_ref(self) -> str:
        """Return the governed Knowledge-scope reference."""

        return self.identity.knowledge_scope_ref

    @property
    def size_bytes(self) -> int:
        """Return unit size without copying content."""

        return len(self.content)

    @staticmethod
    def _required_text(
        *,
        value: str,
        field_name: str,
    ) -> str:
        if not isinstance(value, str):
            raise TypeError(
                f"{field_name} must be a string"
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                f"{field_name} cannot be empty"
            )

        return normalized
