# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Validates real PDF parsing through the ALHF canonical ingestion boundary.
#
# Responsibilities:
# - Generate real text-bearing PDF bytes without parser mocks.
# - Parse PDF through PdfResourceParser.
# - Normalize parsed text through the normalizer registry and service.
# - Preserve identity and parsing/normalization provenance.
# - Prove PDF-specific behavior terminates before canonical Knowledge.
#
# Must Not:
# - Perform derivation, representation, indexing, or retrieval.
# - Mock PDF extraction.
# - Introduce PDF-specific downstream behavior.

from io import BytesIO

from reportlab.pdfgen import canvas

from alhf.rag.ingestion.contracts.acquired_resource import (
    AcquiredResource,
)
from alhf.rag.ingestion.contracts.canonical_content import (
    CanonicalContentKind,
)
from alhf.rag.ingestion.contracts.resource_identity import (
    ResourceIdentity,
)
from alhf.rag.ingestion.normalization_service import (
    NormalizationService,
)
from alhf.rag.ingestion.normalizers.text_content_normalizer import (
    TextContentNormalizer,
)
from alhf.rag.ingestion.parsers.pdf_resource_parser import (
    PdfResourceParser,
)
from alhf.rag.ingestion.providers.in_memory_normalizer_registry import (
    InMemoryNormalizerRegistry,
)


def _pdf_bytes() -> bytes:
    stream = BytesIO()

    pdf = canvas.Canvas(
        stream
    )

    pdf.drawString(
        72,
        720,
        "Enterprise authentication policy requires MFA.",
    )

    pdf.showPage()

    pdf.drawString(
        72,
        720,
        "Privileged access requires additional approval.",
    )

    pdf.save()

    return stream.getvalue()


def _resource() -> AcquiredResource:
    return AcquiredResource(
        identity=ResourceIdentity(
            knowledge_scope_ref="scope-001",
            source_ref="source-001",
            logical_resource_id="policy.pdf",
            revision_id="revision-001",
        ),
        content=_pdf_bytes(),
        media_type="application/pdf",
        content_fingerprint="sha256:test-pdf",
    )


def _normalization_service() -> NormalizationService:
    registry = InMemoryNormalizerRegistry()

    registry.register(
        TextContentNormalizer()
    )

    return NormalizationService(
        registry=registry,
    )


def _run():
    resource = _resource()

    parsed = PdfResourceParser().parse(
        resource
    )

    canonical = _normalization_service().normalize(
        parsed
    )

    return resource, parsed, canonical


def test_real_pdf_reaches_canonical_boundary() -> None:
    _, _, canonical = _run()

    text = canonical.content.decode(
        "utf-8"
    )

    assert (
        "Enterprise authentication policy requires MFA."
        in text
    )
    assert (
        "Privileged access requires additional approval."
        in text
    )

    assert canonical.content_kind == CanonicalContentKind.TEXT
    assert canonical.media_type == "text/plain"


def test_pdf_parsing_preserves_resource_identity() -> None:
    resource, parsed, _ = _run()

    assert parsed.identity is resource.identity
    assert parsed.resource_ref == resource.resource_ref
    assert parsed.revision_ref == resource.revision_ref
    assert parsed.source_media_type == "application/pdf"
    assert parsed.content_media_type == "text/plain"


def test_normalization_preserves_resource_identity() -> None:
    resource, _, canonical = _run()

    assert canonical.identity is resource.identity
    assert canonical.resource_ref == resource.resource_ref
    assert canonical.revision_ref == resource.revision_ref
    assert canonical.knowledge_scope_ref == "scope-001"


def test_pdf_parser_provenance_reaches_canonical_content() -> None:
    _, parsed, canonical = _run()

    expected = (
        f"{parsed.resource_ref}:"
        f"{parsed.revision_ref}:"
        f"{parsed.parser_ref}:"
        f"{parsed.parser_version}"
    )

    assert parsed.parser_ref == "pdf-resource-parser"
    assert parsed.parser_version == "1.0"
    assert canonical.parsed_artifact_ref == expected


def test_existing_text_normalizer_handles_pdf_derived_text() -> None:
    _, _, canonical = _run()

    assert canonical.normalizer_ref == (
        "text-content-normalizer"
    )
    assert canonical.normalizer_version == "1.0"


def test_pdf_ingestion_round_trip_is_deterministic() -> None:
    _, first_parsed, first = _run()
    _, second_parsed, second = _run()

    assert first_parsed.content == second_parsed.content
    assert first.content == second.content
    assert (
        first.parsed_artifact_ref
        == second.parsed_artifact_ref
    )
