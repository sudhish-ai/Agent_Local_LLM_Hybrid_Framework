# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides provider-neutral normalization orchestration for the
# ALHF Knowledge Foundation ingestion plane.
#
# Problem Solved:
# Parsed Knowledge representations require canonicalization before
# downstream processing, but common ingestion logic must remain
# independent from source technologies, original file formats,
# parser implementations, and concrete normalization strategies.
#
# Responsibilities:
# - Accept one provider-neutral ParsedResource.
# - Resolve a compatible normalizer through NormalizerRegistry.
# - Delegate canonicalization to ContentNormalizer.
# - Validate normalizer compatibility before normalization.
# - Validate ResourceIdentity continuity across normalization.
# - Validate canonical-content provenance and media semantics.
# - Return stable CanonicalContent for downstream Knowledge processing.
#
# Must Not:
# - Contain source-specific behavior.
# - Contain PDF, DOCX, CSV, HTML, or other file-format conditionals.
# - Acquire or parse physical Knowledge resources.
# - Implement concrete normalization algorithms.
# - Generate or modify resource or revision identities.
# - Perform derivation or chunking.
# - Perform embedding, indexing, retrieval, or reranking.
# - Materialize collections of Knowledge resources.
# - Implement concurrency or NFT execution policy.
# - Contain Standard RAG, GraphRAG, or Agentic RAG behavior.
#
# Architectural Position:
# - Common canonicalization orchestration inside the ingestion plane.
# - Connects ParsedResource to dynamically selected ContentNormalizer.
# - Produces the canonical boundary consumed by downstream Knowledge
#   Foundation stages.
#
# Reuse Value:
# - Text canonicalization.
# - Structured and tabular canonicalization.
# - Code canonicalization.
# - Future multimodal canonicalization.
# - Local, cloud, hybrid, and customer-specific ingestion pipelines.
#
# Future Extensibility:
# - New source technologies require no service changes.
# - New formats require no service changes when parsers map them to
#   supported parsed semantics.
# - New canonical semantic types can add compatible normalizers.
# - Selection intelligence can evolve behind NormalizerRegistry.
# - Parallel, batched, or distributed normalization can later wrap this
#   semantic boundary without changing downstream contracts.

from __future__ import annotations

from alhf.rag.ingestion.contracts.canonical_content import (
    CanonicalContent,
)
from alhf.rag.ingestion.contracts.parsed_resource import (
    ParsedResource,
)
from alhf.rag.ingestion.interfaces.content_normalizer import (
    ContentNormalizer,
)
from alhf.rag.ingestion.interfaces.normalizer_registry import (
    NormalizerRegistry,
)


class NormalizationService:
    """Provider-neutral orchestration for Knowledge canonicalization."""

    def __init__(
        self,
        *,
        registry: NormalizerRegistry,
    ) -> None:
        if not isinstance(
            registry,
            NormalizerRegistry,
        ):
            raise TypeError(
                "registry must be an instance of NormalizerRegistry"
            )

        self._registry = registry

    def normalize(
        self,
        resource: ParsedResource,
    ) -> CanonicalContent:
        """Resolve and invoke the compatible content normalizer."""

        if not isinstance(
            resource,
            ParsedResource,
        ):
            raise TypeError(
                "resource must be an instance of ParsedResource"
            )

        normalizer = self._registry.resolve(
            resource.content_media_type,
        )

        self._validate_normalizer(
            normalizer=normalizer,
            content_media_type=resource.content_media_type,
        )

        canonical = normalizer.normalize(
            resource,
        )

        self._validate_result(
            resource=resource,
            canonical=canonical,
        )

        return canonical

    @staticmethod
    def _validate_normalizer(
        *,
        normalizer: ContentNormalizer,
        content_media_type: str,
    ) -> None:
        """Validate registry output and declared compatibility."""

        if not isinstance(
            normalizer,
            ContentNormalizer,
        ):
            raise TypeError(
                "registry must return ContentNormalizer"
            )

        if not normalizer.supports(
            content_media_type,
        ):
            raise ValueError(
                "resolved normalizer does not support "
                "parsed content media type"
            )

    @staticmethod
    def _validate_result(
        *,
        resource: ParsedResource,
        canonical: CanonicalContent,
    ) -> None:
        """Protect identity and provenance across canonicalization."""

        if not isinstance(
            canonical,
            CanonicalContent,
        ):
            raise TypeError(
                "normalizer must return CanonicalContent"
            )

        if canonical.identity != resource.identity:
            raise ValueError(
                "canonical identity must match parsed resource"
            )

        if (
            canonical.normalizer_ref.strip() == ""
            or canonical.normalizer_version.strip() == ""
        ):
            raise ValueError(
                "canonical content requires normalizer provenance"
            )
