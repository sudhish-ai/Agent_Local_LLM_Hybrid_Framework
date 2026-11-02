# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the provider-neutral parsed representation of one Knowledge
# resource revision in the ALHF Knowledge Foundation ingestion plane.
#
# Problem Solved:
# Downstream Knowledge processing requires parser output without depending
# on the physical source adapter, original file format, or parser
# implementation that produced it.
#
# Responsibilities:
# - Preserve the exact ResourceIdentity being parsed.
# - Preserve parsed content without assuming text-only Knowledge forever.
# - Declare the media type of the parsed representation.
# - Preserve parser identity and parser version for reproducibility.
# - Preserve the original acquired media type.
# - Provide immutable, provider-neutral parsing output.
#
# Must Not:
# - Perform parsing.
# - Perform content normalization.
# - Generate resource or revision identities.
# - Contain filesystem paths, URLs, buckets, or provider locations.
# - Perform chunking, embedding, indexing, or retrieval.
# - Materialize collections of parsed resources.
# - Contain Standard RAG, GraphRAG, or Agentic RAG behavior.
# - Contain arbitrary metadata dictionaries.
#
# Architectural Position:
# - Stable output contract of the Knowledge parsing boundary.
# - Connects Acquisition to later Normalization without source coupling.
# - Preserves provenance through ResourceIdentity.
# - Avoids making text the only permanent Knowledge representation.
#
# Reuse Value:
# - Text parsing.
# - PDF parsing.
# - Document parsing.
# - Structured-data parsing.
# - Code parsing.
# - Future multimodal parsing representations.
#
# Future Extensibility:
# - New parsers can produce compatible representations without changing
#   downstream source identity semantics.
# - Structured and multimodal representations can use appropriate media
#   types without redesigning this contract.
# - Large-resource streaming can evolve behind parsing boundaries.
# - Parser execution strategy can evolve independently for NFT tuning.

from __future__ import annotations

from dataclasses import dataclass

from alhf.rag.ingestion.contracts.resource_identity import (
    ResourceIdentity,
)


@dataclass(frozen=True, slots=True)
class ParsedResource:
    """
    Immutable parsed representation of one Knowledge resource revision.

    identity:
        Stable logical-resource and exact-revision identity inherited
        from acquisition.

    content:
        Parsed representation encoded as bytes.

    content_media_type:
        Media type describing the parsed representation.

    source_media_type:
        Media type of the originally acquired resource.

    parser_ref:
        Stable logical identifier of the parser implementation.

    parser_version:
        Stable version of the parser behavior used for reproducibility.
    """

    identity: ResourceIdentity
    content: bytes
    content_media_type: str
    source_media_type: str
    parser_ref: str
    parser_version: str

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

        fields = (
            "content_media_type",
            "source_media_type",
            "parser_ref",
            "parser_version",
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
        """Return the exact source revision reference."""

        return self.identity.revision_ref

    @property
    def size_bytes(self) -> int:
        """Return parsed representation size without copying content."""

        return len(self.content)

    @staticmethod
    def _normalize_required_text(
        *,
        value: str,
        field_name: str,
    ) -> str:
        """Validate and normalize required parsing metadata."""

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
