# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the canonical Knowledge content representation used after
# source acquisition and format-specific parsing in the ALHF Knowledge
# Foundation ingestion plane.
#
# Problem Solved:
# Downstream Knowledge stages must not understand physical source types,
# original file formats, or parser implementations. This contract creates
# the stable semantic boundary after which source and format complexity
# terminates.
#
# Responsibilities:
# - Preserve source ResourceIdentity and provenance continuity.
# - Represent canonical Knowledge content using governed content kinds.
# - Preserve canonical content without assuming text is the only future
#   Knowledge representation.
# - Preserve the media type of the canonical representation.
# - Preserve the parsed artifact reference used to derive the content.
# - Preserve normalizer identity and version for reproducibility.
# - Provide immutable downstream Knowledge content semantics.
#
# Must Not:
# - Acquire or parse physical Knowledge resources.
# - Contain source-provider-specific behavior.
# - Contain PDF, DOCX, CSV, HTML, or other format-specific logic.
# - Generate or modify source resource identity.
# - Perform derivation, chunking, embedding, indexing, or retrieval.
# - Materialize collections of Knowledge resources.
# - Contain arbitrary metadata dictionaries.
# - Implement concurrency or NFT execution policy.
# - Contain Standard RAG, GraphRAG, or Agentic RAG behavior.
#
# Architectural Position:
# - Stable canonical boundary between ingestion format handling and
#   downstream Knowledge processing.
# - Source and input-format complexity must terminate before this point.
# - Downstream stages operate on canonical Knowledge semantics.
#
# Reuse Value:
# - Text-based enterprise Knowledge.
# - Structured Knowledge representations.
# - Code and tabular Knowledge.
# - Future multimodal canonical representations.
# - Standard RAG, GraphRAG, and Agentic RAG ingestion foundations.
#
# Future Extensibility:
# - Additional universal content kinds can be introduced deliberately.
# - New source types must not require this contract to change.
# - New file formats must not require this contract to change when they
#   map to existing canonical content semantics.
# - Future execution strategies can process canonical content in bounded
#   parallel or distributed pipelines without changing the contract.

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from alhf.rag.ingestion.contracts.resource_identity import (
    ResourceIdentity,
)


class CanonicalContentKind(str, Enum):
    """Universal semantic categories of canonical Knowledge content."""

    TEXT = "TEXT"
    STRUCTURED = "STRUCTURED"
    TABULAR = "TABULAR"
    CODE = "CODE"
    MULTIMODAL = "MULTIMODAL"


@dataclass(frozen=True, slots=True)
class CanonicalContent:
    """
    Immutable canonical representation of one Knowledge resource revision.

    identity:
        Stable logical-resource and exact-revision identity inherited
        through acquisition and parsing.

    content:
        Canonical representation encoded as bytes.

    content_kind:
        Universal semantic category of the canonical representation.

    media_type:
        Media type describing the canonical representation.

    parsed_artifact_ref:
        Stable provenance reference to the parsed artifact from which
        this canonical content was produced.

    normalizer_ref:
        Stable logical identifier of the normalizer behavior.

    normalizer_version:
        Stable normalizer version used for reproducibility.
    """

    identity: ResourceIdentity
    content: bytes
    content_kind: CanonicalContentKind
    media_type: str
    parsed_artifact_ref: str
    normalizer_ref: str
    normalizer_version: str

    def __post_init__(self) -> None:
        if not isinstance(
            self.identity,
            ResourceIdentity,
        ):
            raise TypeError(
                "identity must be an instance of ResourceIdentity"
            )

        if not isinstance(
            self.content,
            bytes,
        ):
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
            "media_type",
            "parsed_artifact_ref",
            "normalizer_ref",
            "normalizer_version",
        )

        for field_name in fields:
            normalized = self._normalize_required_text(
                value=getattr(self, field_name),
                field_name=field_name,
            )

            object.__setattr__(
                self,
                field_name,
                normalized,
            )

    @property
    def resource_ref(self) -> str:
        """Return the stable logical-resource reference."""

        return self.identity.resource_ref

    @property
    def revision_ref(self) -> str:
        """Return the exact source-revision reference."""

        return self.identity.revision_ref

    @property
    def knowledge_scope_ref(self) -> str:
        """Return the governed Knowledge-scope reference."""

        return self.identity.knowledge_scope_ref

    @property
    def size_bytes(self) -> int:
        """Return canonical content size without copying content."""

        return len(self.content)

    @staticmethod
    def _normalize_required_text(
        *,
        value: str,
        field_name: str,
    ) -> str:
        """Validate and normalize required canonical-content text."""

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
