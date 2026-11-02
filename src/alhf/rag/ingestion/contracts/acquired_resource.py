# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines one acquired Knowledge resource revision produced by the
# ALHF Knowledge Foundation ingestion plane.
#
# Problem Solved:
# Acquisition must hand downstream processing a provider-neutral resource
# without exposing filesystem, object-storage, API, or database details.
#
# Responsibilities:
# - Preserve stable resource and revision identity.
# - Preserve provider-neutral acquired content.
# - Preserve a declared media type.
# - Preserve an optional content fingerprint.
# - Normalize and validate acquisition values.
# - Represent exactly one acquired resource revision.
#
# Must Not:
# - Represent an unbounded collection of resources.
# - Store credentials, URLs, paths, buckets, or connection details.
# - Parse or normalize acquired content.
# - Perform chunking, embedding, indexing, or retrieval.
# - Generate resource or revision identities.
# - Decide whether content changed.
# - Perform synchronization.
# - Contain Standard, Graph, or Agentic RAG behavior.
# - Contain arbitrary metadata dictionaries.
#
# Architectural Position:
# - Provider-neutral output contract of the acquisition boundary.
# - Input to later parsing and normalization stages.
# - Keeps physical source adapters outside downstream processing.
#
# Future Extensibility:
# - Streaming acquisition can use bounded resources around this contract.
# - Multimodal parsing can interpret content through media_type.
# - Fingerprint generation remains adapter or acquisition-policy behavior.
# - Provenance continues through ResourceIdentity.

from __future__ import annotations

from dataclasses import dataclass

from alhf.rag.ingestion.contracts.resource_identity import (
    ResourceIdentity,
)


@dataclass(frozen=True, slots=True)
class AcquiredResource:
    """
    Immutable acquired representation of one Knowledge resource revision.

    identity:
        Stable logical-resource and exact-revision identity.

    content:
        Acquired resource bytes exactly as handed to downstream parsing.

    media_type:
        Provider-neutral content type used to select compatible parsing
        behavior.

    content_fingerprint:
        Optional stable fingerprint produced by acquisition infrastructure
        for integrity, change detection, or reproducibility.
    """

    identity: ResourceIdentity
    content: bytes
    media_type: str
    content_fingerprint: str | None = None

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

        media_type = self._required_text(
            value=self.media_type,
            field_name="media_type",
        )
        content_fingerprint = self._optional_text(
            value=self.content_fingerprint,
            field_name="content_fingerprint",
        )

        object.__setattr__(
            self,
            "media_type",
            media_type,
        )
        object.__setattr__(
            self,
            "content_fingerprint",
            content_fingerprint,
        )

    @property
    def resource_ref(self) -> str:
        """Return the stable logical-resource reference."""

        return self.identity.resource_ref

    @property
    def revision_ref(self) -> str:
        """Return the exact acquired revision reference."""

        return self.identity.revision_ref

    @property
    def size_bytes(self) -> int:
        """Return the acquired resource size without duplicating content."""

        return len(self.content)

    @staticmethod
    def _required_text(
        *,
        value: str,
        field_name: str,
    ) -> str:
        """Validate and normalize required acquisition text."""

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

    @staticmethod
    def _optional_text(
        *,
        value: str | None,
        field_name: str,
    ) -> str | None:
        """Validate and normalize optional acquisition text."""

        if value is None:
            return None

        if not isinstance(value, str):
            raise TypeError(
                f"{field_name} must be a string or None"
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                f"{field_name} cannot be empty when provided"
            )

        return normalized
