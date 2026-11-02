# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides the plain-text resource parser used by the
# ALHF Knowledge Foundation ingestion plane.
#
# Problem Solved:
# Plain-text Knowledge resources must be validated and converted into
# the stable ParsedResource contract without leaking format-specific
# behavior into downstream Knowledge Foundation layers.
#
# Responsibilities:
# - Support configured plain-text media types.
# - Validate acquired resource compatibility.
# - Validate acquired content as UTF-8 text.
# - Preserve ResourceIdentity unchanged.
# - Produce a canonical UTF-8 text representation.
# - Preserve source media type.
# - Preserve parser identity and version for reproducibility.
#
# Must Not:
# - Acquire physical Knowledge resources.
# - Modify resource or revision identity.
# - Perform semantic normalization.
# - Perform chunking, embedding, indexing, or retrieval.
# - Contain downstream file-type conditionals.
# - Perform charset guessing.
# - Implement concurrency or NFT execution policy.
# - Contain Standard RAG, GraphRAG, or Agentic RAG behavior.
#
# Architectural Position:
# - Concrete ResourceParser for plain-text Knowledge.
# - First real parser behind the universal parsing boundary.
# - Converts format-specific input into stable ParsedResource output.
#
# Reuse Value:
# - Local text files.
# - Text acquired from cloud or enterprise source adapters.
# - Deterministic ingestion integration testing.
# - Future source-independent plain-text acquisition.
#
# Future Extensibility:
# - Additional text encodings can use separate parsing policy or parsers.
# - New content formats require new ResourceParser implementations.
# - Parser execution can later be parallelized behind execution policy.
# - Downstream Knowledge layers remain unchanged as parsers are added.

from __future__ import annotations

from alhf.rag.ingestion.contracts.acquired_resource import (
    AcquiredResource,
)
from alhf.rag.ingestion.contracts.parsed_resource import (
    ParsedResource,
)
from alhf.rag.ingestion.interfaces.resource_parser import (
    ResourceParser,
)


class TextResourceParser(ResourceParser):
    """Parse UTF-8 plain-text resources."""

    _PARSER_REF = "text-resource-parser"
    _PARSER_VERSION = "1.0"
    _SUPPORTED_MEDIA_TYPES = frozenset(
        {
            "text/plain",
        }
    )

    @property
    def parser_ref(self) -> str:
        """Return the stable logical parser identifier."""

        return self._PARSER_REF

    @property
    def parser_version(self) -> str:
        """Return the stable parser behavior version."""

        return self._PARSER_VERSION

    def supports(
        self,
        media_type: str,
    ) -> bool:
        """Return whether the media type is supported."""

        if not isinstance(
            media_type,
            str,
        ):
            return False

        normalized = media_type.strip().lower()

        if not normalized:
            return False

        return normalized in self._SUPPORTED_MEDIA_TYPES

    def parse(
        self,
        resource: AcquiredResource,
    ) -> ParsedResource:
        """Parse one UTF-8 plain-text resource."""

        if not isinstance(
            resource,
            AcquiredResource,
        ):
            raise TypeError(
                "resource must be an instance of AcquiredResource"
            )

        if not self.supports(
            resource.media_type,
        ):
            raise ValueError(
                "unsupported media type for TextResourceParser"
            )

        try:
            text = resource.content.decode(
                "utf-8"
            )
        except UnicodeDecodeError as error:
            raise ValueError(
                "text resource must contain valid UTF-8 content"
            ) from error

        canonical_content = text.encode(
            "utf-8"
        )

        return ParsedResource(
            identity=resource.identity,
            content=canonical_content,
            content_media_type="text/plain",
            source_media_type=resource.media_type,
            parser_ref=self.parser_ref,
            parser_version=self.parser_version,
        )
