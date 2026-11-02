# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides canonical text normalization for the
# ALHF Knowledge Foundation ingestion plane.
#
# Problem Solved:
# Parsed textual Knowledge may originate from many physical sources and
# file formats. Downstream Knowledge processing requires one deterministic
# canonical text representation independent from those origins.
#
# Responsibilities:
# - Accept parsed UTF-8 text semantics.
# - Validate parsed content compatibility.
# - Preserve ResourceIdentity unchanged.
# - Normalize Unicode text deterministically.
# - Normalize line endings deterministically.
# - Produce CanonicalContent with TEXT semantics.
# - Preserve parsed-artifact provenance.
# - Preserve normalizer identity and version for reproducibility.
#
# Must Not:
# - Acquire physical Knowledge resources.
# - Parse PDF, DOCX, HTML, TXT, or other physical formats.
# - Depend on the original source provider.
# - Modify resource or revision identity.
# - Perform semantic rewriting or summarization.
# - Perform derivation or chunking.
# - Perform embedding, indexing, retrieval, or reranking.
# - Implement concurrency or NFT execution policy.
# - Contain Standard RAG, GraphRAG, or Agentic RAG behavior.
#
# Architectural Position:
# - Concrete ContentNormalizer for parsed textual Knowledge.
# - Converts parser output into stable canonical Knowledge semantics.
# - Sits at the ingestion abstraction firewall before downstream stages.
#
# Reuse Value:
# - Text originating from local files.
# - Text extracted from PDF or DOCX.
# - Text extracted from HTML or enterprise collaboration sources.
# - Text acquired through APIs, cloud storage, or future source adapters.
#
# Future Extensibility:
# - Additional canonical semantics use separate normalizers.
# - New textual source formats can reuse this normalizer when parsers
#   produce compatible UTF-8 text semantics.
# - Parallel normalization can evolve behind execution policy.
# - Downstream Knowledge stages remain unchanged as sources and parsers
#   are added.

from __future__ import annotations

import unicodedata

from alhf.rag.ingestion.contracts.canonical_content import (
    CanonicalContent,
    CanonicalContentKind,
)
from alhf.rag.ingestion.contracts.parsed_resource import (
    ParsedResource,
)
from alhf.rag.ingestion.interfaces.content_normalizer import (
    ContentNormalizer,
)


class TextContentNormalizer(ContentNormalizer):
    """Normalize parsed UTF-8 text into canonical ALHF text content."""

    _NORMALIZER_REF = "text-content-normalizer"
    _NORMALIZER_VERSION = "1.0"
    _SUPPORTED_MEDIA_TYPES = frozenset(
        {
            "text/plain",
        }
    )

    @property
    def normalizer_ref(self) -> str:
        """Return the stable logical normalizer identifier."""

        return self._NORMALIZER_REF

    @property
    def normalizer_version(self) -> str:
        """Return the stable normalizer behavior version."""

        return self._NORMALIZER_VERSION

    def supports(
        self,
        content_media_type: str,
    ) -> bool:
        """Return whether parsed content semantics are supported."""

        if not isinstance(
            content_media_type,
            str,
        ):
            return False

        normalized = content_media_type.strip().lower()

        if not normalized:
            return False

        return normalized in self._SUPPORTED_MEDIA_TYPES

    def normalize(
        self,
        resource: ParsedResource,
    ) -> CanonicalContent:
        """Normalize one parsed UTF-8 text resource."""

        if not isinstance(
            resource,
            ParsedResource,
        ):
            raise TypeError(
                "resource must be an instance of ParsedResource"
            )

        if not self.supports(
            resource.content_media_type,
        ):
            raise ValueError(
                "unsupported content media type for "
                "TextContentNormalizer"
            )

        try:
            text = resource.content.decode(
                "utf-8"
            )
        except UnicodeDecodeError as error:
            raise ValueError(
                "parsed text must contain valid UTF-8 content"
            ) from error

        normalized_text = unicodedata.normalize(
            "NFC",
            text,
        )

        normalized_text = normalized_text.replace(
            "\r\n",
            "\n",
        ).replace(
            "\r",
            "\n",
        )

        canonical_content = normalized_text.encode(
            "utf-8"
        )

        return CanonicalContent(
            identity=resource.identity,
            content=canonical_content,
            content_kind=CanonicalContentKind.TEXT,
            media_type="text/plain",
            parsed_artifact_ref=self._parsed_artifact_ref(
                resource,
            ),
            normalizer_ref=self.normalizer_ref,
            normalizer_version=self.normalizer_version,
        )

    @staticmethod
    def _parsed_artifact_ref(
        resource: ParsedResource,
    ) -> str:
        """Build deterministic provenance for the parsed representation."""

        return (
            f"{resource.resource_ref}:"
            f"{resource.revision_ref}:"
            f"{resource.parser_ref}:"
            f"{resource.parser_version}"
        )
