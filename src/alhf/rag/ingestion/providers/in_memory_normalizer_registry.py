# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides the in-memory normalizer registry implementation used by the
# ALHF Knowledge Foundation ingestion plane.
#
# Problem Solved:
# Normalization orchestration must dynamically resolve compatible
# canonicalization behavior without coupling common ingestion logic to
# individual source types, file formats, parsers, or normalizers.
#
# Responsibilities:
# - Register configured ContentNormalizer implementations.
# - Preserve deterministic registration order.
# - Resolve a compatible normalizer by parsed content media type.
# - Report normalizer availability by parsed content media type.
# - Reject duplicate normalizer references.
# - Validate normalizer identity and version during registration.
#
# Must Not:
# - Normalize Knowledge content directly.
# - Acquire or parse physical resources.
# - Contain source-specific behavior.
# - Contain PDF, DOCX, CSV, HTML, or other format-specific logic.
# - Generate or modify resource or revision identities.
# - Perform derivation, chunking, embedding, indexing, or retrieval.
# - Load plugins dynamically.
# - Implement concurrency or NFT execution policy.
# - Contain Standard RAG, GraphRAG, or Agentic RAG behavior.
#
# Architectural Position:
# - Concrete V1 implementation of NormalizerRegistry.
# - Composition mechanism for dynamically configured normalizers.
# - Protects the canonical Knowledge boundary from source and
#   file-format complexity.
#
# Reuse Value:
# - Text canonicalization.
# - Structured and tabular canonicalization.
# - Code canonicalization.
# - Future multimodal canonicalization.
# - Customer-specific canonicalization extensions.
#
# Future Extensibility:
# - Plugin-backed registries can implement NormalizerRegistry separately.
# - Selection intelligence can evolve behind the registry boundary.
# - Multiple compatible normalizers can later use explicit policy.
# - Execution parallelism can evolve outside semantic contracts.
# - New formats mapping to existing canonical semantics require no
#   downstream Knowledge Foundation changes.

from __future__ import annotations

from alhf.rag.ingestion.interfaces.content_normalizer import (
    ContentNormalizer,
)
from alhf.rag.ingestion.interfaces.normalizer_registry import (
    NormalizerRegistry,
)


class InMemoryNormalizerRegistry(NormalizerRegistry):
    """In-memory registry of configured content normalizers."""

    def __init__(self) -> None:
        self._normalizers: dict[str, ContentNormalizer] = {}

    def register(
        self,
        normalizer: ContentNormalizer,
    ) -> None:
        """Register one configured content normalizer."""

        if not isinstance(
            normalizer,
            ContentNormalizer,
        ):
            raise TypeError(
                "normalizer must be an instance of ContentNormalizer"
            )

        normalizer_ref = self._normalize_required_text(
            value=normalizer.normalizer_ref,
            field_name="normalizer_ref",
        )

        self._normalize_required_text(
            value=normalizer.normalizer_version,
            field_name="normalizer_version",
        )

        if normalizer_ref in self._normalizers:
            raise ValueError(
                f"normalizer already registered: {normalizer_ref}"
            )

        self._normalizers[normalizer_ref] = normalizer

    def resolve(
        self,
        content_media_type: str,
    ) -> ContentNormalizer:
        """Resolve the first compatible registered normalizer."""

        normalized_media_type = self._normalize_required_text(
            value=content_media_type,
            field_name="content_media_type",
        )

        for normalizer in self._normalizers.values():
            if normalizer.supports(
                normalized_media_type,
            ):
                return normalizer

        raise LookupError(
            "normalizer not found for content media type: "
            f"{normalized_media_type}"
        )

    def contains(
        self,
        content_media_type: str,
    ) -> bool:
        """Return whether a compatible normalizer is registered."""

        normalized_media_type = self._normalize_required_text(
            value=content_media_type,
            field_name="content_media_type",
        )

        return any(
            normalizer.supports(
                normalized_media_type,
            )
            for normalizer in self._normalizers.values()
        )

    def __contains__(
        self,
        normalizer_ref: object,
    ) -> bool:
        """Return whether a normalizer reference is registered."""

        if not isinstance(
            normalizer_ref,
            str,
        ):
            return False

        normalized_ref = normalizer_ref.strip()

        if not normalized_ref:
            return False

        return normalized_ref in self._normalizers

    def __len__(self) -> int:
        """Return the number of registered normalizers."""

        return len(
            self._normalizers,
        )

    @staticmethod
    def _normalize_required_text(
        *,
        value: str,
        field_name: str,
    ) -> str:
        """Validate and normalize required registry text."""

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
