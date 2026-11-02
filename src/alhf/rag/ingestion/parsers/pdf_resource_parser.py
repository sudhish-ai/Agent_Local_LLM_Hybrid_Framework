# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides PDF text extraction behind the universal ALHF ResourceParser
# boundary for the Knowledge Foundation ingestion plane.
#
# Problem Solved:
# Text-bearing PDF Knowledge resources must enter the common ingestion
# pipeline without leaking PDF-specific behavior into downstream stages.
#
# Responsibilities:
# - Support the application/pdf media type.
# - Validate acquired PDF resources.
# - Extract text from PDF pages deterministically.
# - Preserve ResourceIdentity unchanged.
# - Produce UTF-8 text ParsedResource output.
# - Preserve original PDF media type.
# - Preserve parser identity and version.
# - Fail explicitly when no text can be extracted.
#
# Must Not:
# - Acquire physical PDF resources.
# - Modify resource or revision identity.
# - Perform OCR for image-only PDFs.
# - Perform semantic normalization.
# - Perform chunking, representation, indexing, or retrieval.
# - Implement concurrency or execution policy.
# - Leak PDF behavior into downstream Knowledge layers.
# - Depend on external RAG or orchestration frameworks.
#
# Architectural Position:
# - Concrete ResourceParser for text-bearing PDF Knowledge.
# - Extends ingestion by format without downstream modifications.
# - Produces the same ParsedResource boundary as other parsers.
#
# Reuse Value:
# - Local PDF files.
# - PDFs acquired from future cloud and enterprise adapters.
# - Real PDF V1 end-to-end Knowledge Foundation validation.
#
# Future Extensibility:
# - OCR-capable parsing can be added independently for scanned PDFs.
# - Layout-aware parsing can evolve through another parser strategy.
# - Large-resource execution limits can evolve through ingestion policy.
# - Downstream Knowledge stages remain unchanged as PDF support evolves.

from __future__ import annotations

from io import BytesIO

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from alhf.rag.ingestion.contracts.acquired_resource import (
    AcquiredResource,
)
from alhf.rag.ingestion.contracts.parsed_resource import (
    ParsedResource,
)
from alhf.rag.ingestion.interfaces.resource_parser import (
    ResourceParser,
)


class PdfResourceParser(ResourceParser):
    """Parse text-bearing PDF resources into UTF-8 text."""

    _PARSER_REF = "pdf-resource-parser"
    _PARSER_VERSION = "1.0"
    _SUPPORTED_MEDIA_TYPES = frozenset(
        {
            "application/pdf",
        }
    )
    _PAGE_SEPARATOR = "\n\n"

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
        """Extract UTF-8 text from one acquired PDF resource."""

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
                "unsupported media type for PdfResourceParser"
            )

        if not resource.content:
            raise ValueError(
                "PDF resource content cannot be empty"
            )

        reader = self._reader(
            resource.content
        )

        if reader.is_encrypted:
            raise ValueError(
                "encrypted PDF resources are not supported"
            )

        page_text: list[str] = []

        try:
            for page in reader.pages:
                text = page.extract_text()

                if not text:
                    continue

                normalized = text.strip()

                if normalized:
                    page_text.append(
                        normalized
                    )
        except Exception as error:
            raise ValueError(
                "PDF text extraction failed"
            ) from error

        if not page_text:
            raise ValueError(
                "PDF resource contains no extractable text"
            )

        content = self._PAGE_SEPARATOR.join(
            page_text
        ).encode("utf-8")

        return ParsedResource(
            identity=resource.identity,
            content=content,
            content_media_type="text/plain",
            source_media_type=resource.media_type,
            parser_ref=self.parser_ref,
            parser_version=self.parser_version,
        )

    @staticmethod
    def _reader(
        content: bytes,
    ) -> PdfReader:
        """Construct a PDF reader from acquired in-memory content."""

        try:
            return PdfReader(
                BytesIO(content),
                strict=False,
            )
        except (
            PdfReadError,
            EOFError,
            ValueError,
        ) as error:
            raise ValueError(
                "invalid PDF resource content"
            ) from error
