# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF NormalizationService.
#
# Responsibilities:
# - Validate dynamic normalizer resolution.
# - Validate ParsedResource normalization.
# - Validate CanonicalContent output.
# - Validate ResourceIdentity continuity.
# - Validate Knowledge-scope continuity.
# - Validate canonical content semantics.
# - Validate unsupported parsed-content behavior.
# - Validate invalid registry and normalizer behavior.
#
# Must Not:
# - Test physical source acquisition.
# - Test format-specific parsing.
# - Test concrete normalization algorithms in depth.
# - Test derivation or chunking.
# - Test embedding, indexing, retrieval, or reranking.
# - Test concurrency or NFT execution strategies.
# - Test Standard RAG, GraphRAG, or Agentic RAG behavior.

import pytest

from alhf.rag.ingestion.contracts.canonical_content import (
    CanonicalContent,
    CanonicalContentKind,
)
from alhf.rag.ingestion.contracts.parsed_resource import (
    ParsedResource,
)
from alhf.rag.ingestion.contracts.resource_identity import (
    ResourceIdentity,
)
from alhf.rag.ingestion.interfaces.content_normalizer import (
    ContentNormalizer,
)
from alhf.rag.ingestion.interfaces.normalizer_registry import (
    NormalizerRegistry,
)
from alhf.rag.ingestion.normalization_service import (
    NormalizationService,
)
from alhf.rag.ingestion.normalizers.text_content_normalizer import (
    TextContentNormalizer,
)
from alhf.rag.ingestion.providers.in_memory_normalizer_registry import (
    InMemoryNormalizerRegistry,
)


def _resource(
    content_media_type: str = "text/plain",
) -> ParsedResource:
    return ParsedResource(
        identity=ResourceIdentity(
            knowledge_scope_ref="scope-001",
            source_ref="source-001",
            logical_resource_id="resource-001",
            revision_id="revision-001",
        ),
        content=b"enterprise knowledge",
        content_media_type=content_media_type,
        source_media_type="application/pdf",
        parser_ref="parser-001",
        parser_version="1.0",
    )


def _service() -> NormalizationService:
    registry = InMemoryNormalizerRegistry()
    registry.register(
        TextContentNormalizer()
    )

    return NormalizationService(
        registry=registry,
    )


def test_create_normalization_service() -> None:
    service = _service()

    assert isinstance(
        service,
        NormalizationService,
    )


def test_normalize_returns_canonical_content() -> None:
    canonical = _service().normalize(
        _resource()
    )

    assert isinstance(
        canonical,
        CanonicalContent,
    )


def test_normalize_preserves_resource_identity() -> None:
    resource = _resource()

    canonical = _service().normalize(
        resource
    )

    assert canonical.identity is resource.identity
    assert canonical.resource_ref == "resource-001"
    assert canonical.revision_ref == "revision-001"


def test_normalize_preserves_knowledge_scope() -> None:
    canonical = _service().normalize(
        _resource()
    )

    assert canonical.knowledge_scope_ref == "scope-001"


def test_normalize_produces_canonical_text() -> None:
    canonical = _service().normalize(
        _resource()
    )

    assert canonical.content_kind == CanonicalContentKind.TEXT
    assert canonical.media_type == "text/plain"
    assert canonical.content == b"enterprise knowledge"


def test_normalize_records_normalizer_identity() -> None:
    canonical = _service().normalize(
        _resource()
    )

    assert (
        canonical.normalizer_ref
        == "text-content-normalizer"
    )
    assert canonical.normalizer_version == "1.0"


def test_normalize_preserves_parser_provenance() -> None:
    canonical = _service().normalize(
        _resource()
    )

    assert canonical.parsed_artifact_ref == (
        "resource-001:"
        "revision-001:"
        "parser-001:"
        "1.0"
    )


def test_unsupported_content_type_is_rejected() -> None:
    service = _service()

    with pytest.raises(
        LookupError,
        match=(
            "normalizer not found for content media type: "
            "application/json"
        ),
    ):
        service.normalize(
            _resource(
                content_media_type="application/json"
            )
        )


def test_invalid_resource_is_rejected() -> None:
    service = _service()

    with pytest.raises(
        TypeError,
        match=(
            "resource must be an instance of ParsedResource"
        ),
    ):
        service.normalize(
            "invalid-resource"
        )


def test_invalid_registry_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "registry must be an instance of "
            "NormalizerRegistry"
        ),
    ):
        NormalizationService(
            registry="invalid-registry"
        )


class InvalidNormalizerRegistry(NormalizerRegistry):
    """Registry intentionally returning an invalid normalizer."""

    def resolve(
        self,
        content_media_type: str,
    ):
        return "invalid-normalizer"

    def contains(
        self,
        content_media_type: str,
    ) -> bool:
        return True


def test_invalid_registry_normalizer_is_rejected() -> None:
    service = NormalizationService(
        registry=InvalidNormalizerRegistry()
    )

    with pytest.raises(
        TypeError,
        match="registry must return ContentNormalizer",
    ):
        service.normalize(
            _resource()
        )


class IncompatibleNormalizer(TextContentNormalizer):
    """Normalizer incompatible after registry resolution."""

    def supports(
        self,
        content_media_type: str,
    ) -> bool:
        return False


class IncompatibleNormalizerRegistry(NormalizerRegistry):
    """Registry returning an incompatible normalizer."""

    def resolve(
        self,
        content_media_type: str,
    ) -> ContentNormalizer:
        return IncompatibleNormalizer()

    def contains(
        self,
        content_media_type: str,
    ) -> bool:
        return True


def test_incompatible_normalizer_is_rejected() -> None:
    service = NormalizationService(
        registry=IncompatibleNormalizerRegistry()
    )

    with pytest.raises(
        ValueError,
        match=(
            "resolved normalizer does not support "
            "parsed content media type"
        ),
    ):
        service.normalize(
            _resource()
        )
