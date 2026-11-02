# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF ContentNormalizer interface.
#
# Responsibilities:
# - Validate the abstract normalization boundary.
# - Validate normalizer identity and version contracts.
# - Validate parsed-content compatibility declaration.
# - Validate ParsedResource input handling.
# - Validate CanonicalContent output behavior.
# - Validate ResourceIdentity preservation.
# - Validate parsed-artifact provenance preservation.
# - Protect source and file-format isolation from downstream layers.
#
# Must Not:
# - Test physical source acquisition.
# - Test concrete file-format parsers.
# - Test concrete normalization algorithms.
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


class StubContentNormalizer(ContentNormalizer):
    """Minimal normalizer used to validate the common boundary."""

    @property
    def normalizer_ref(self) -> str:
        return "text-normalizer"

    @property
    def normalizer_version(self) -> str:
        return "1.0"

    def supports(
        self,
        content_media_type: str,
    ) -> bool:
        return content_media_type == "text/plain"

    def normalize(
        self,
        resource: ParsedResource,
    ) -> CanonicalContent:
        return CanonicalContent(
            identity=resource.identity,
            content=resource.content,
            content_kind=CanonicalContentKind.TEXT,
            media_type="text/plain",
            parsed_artifact_ref=(
                f"{resource.resource_ref}:{resource.revision_ref}"
            ),
            normalizer_ref=self.normalizer_ref,
            normalizer_version=self.normalizer_version,
        )


class MissingNormalizeNormalizer(ContentNormalizer):
    """Invalid normalizer missing normalization behavior."""

    @property
    def normalizer_ref(self) -> str:
        return "missing-normalize"

    @property
    def normalizer_version(self) -> str:
        return "1.0"

    def supports(
        self,
        content_media_type: str,
    ) -> bool:
        return True


class MissingSupportsNormalizer(ContentNormalizer):
    """Invalid normalizer missing compatibility behavior."""

    @property
    def normalizer_ref(self) -> str:
        return "missing-supports"

    @property
    def normalizer_version(self) -> str:
        return "1.0"

    def normalize(
        self,
        resource: ParsedResource,
    ) -> CanonicalContent:
        raise NotImplementedError


def _parsed_resource() -> ParsedResource:
    return ParsedResource(
        identity=ResourceIdentity(
            knowledge_scope_ref="scope-001",
            source_ref="source-001",
            logical_resource_id="resource-001",
            revision_id="revision-001",
        ),
        content=b"enterprise knowledge",
        content_media_type="text/plain",
        source_media_type="application/pdf",
        parser_ref="pdf-parser",
        parser_version="1.0",
    )


def test_content_normalizer_is_abstract() -> None:
    with pytest.raises(TypeError):
        ContentNormalizer()


def test_missing_normalize_prevents_instantiation() -> None:
    with pytest.raises(TypeError):
        MissingNormalizeNormalizer()


def test_missing_supports_prevents_instantiation() -> None:
    with pytest.raises(TypeError):
        MissingSupportsNormalizer()


def test_concrete_normalizer_can_be_instantiated() -> None:
    normalizer = StubContentNormalizer()

    assert isinstance(
        normalizer,
        ContentNormalizer,
    )


def test_normalizer_exposes_stable_reference() -> None:
    normalizer = StubContentNormalizer()

    assert normalizer.normalizer_ref == "text-normalizer"


def test_normalizer_exposes_stable_version() -> None:
    normalizer = StubContentNormalizer()

    assert normalizer.normalizer_version == "1.0"


def test_normalizer_supports_parsed_text_semantics() -> None:
    normalizer = StubContentNormalizer()

    assert normalizer.supports("text/plain") is True


def test_normalizer_rejects_unsupported_semantics() -> None:
    normalizer = StubContentNormalizer()

    assert normalizer.supports("application/json") is False


def test_normalize_returns_canonical_content() -> None:
    normalizer = StubContentNormalizer()

    canonical = normalizer.normalize(
        _parsed_resource()
    )

    assert isinstance(
        canonical,
        CanonicalContent,
    )


def test_normalize_preserves_resource_identity() -> None:
    normalizer = StubContentNormalizer()
    parsed = _parsed_resource()

    canonical = normalizer.normalize(
        parsed
    )

    assert canonical.identity is parsed.identity
    assert canonical.resource_ref == "resource-001"
    assert canonical.revision_ref == "revision-001"


def test_normalize_preserves_knowledge_scope() -> None:
    canonical = StubContentNormalizer().normalize(
        _parsed_resource()
    )

    assert canonical.knowledge_scope_ref == "scope-001"


def test_normalize_produces_canonical_text_semantics() -> None:
    canonical = StubContentNormalizer().normalize(
        _parsed_resource()
    )

    assert canonical.content_kind == CanonicalContentKind.TEXT
    assert canonical.media_type == "text/plain"
    assert canonical.content == b"enterprise knowledge"


def test_normalize_records_reproducibility_identity() -> None:
    normalizer = StubContentNormalizer()

    canonical = normalizer.normalize(
        _parsed_resource()
    )

    assert canonical.normalizer_ref == "text-normalizer"
    assert canonical.normalizer_version == "1.0"


def test_normalize_preserves_parsed_artifact_provenance() -> None:
    canonical = StubContentNormalizer().normalize(
        _parsed_resource()
    )

    assert (
        canonical.parsed_artifact_ref
        == "resource-001:revision-001"
    )
