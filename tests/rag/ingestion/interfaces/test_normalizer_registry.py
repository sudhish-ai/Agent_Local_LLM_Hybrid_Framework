# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF NormalizerRegistry interface.
#
# Responsibilities:
# - Validate the abstract normalizer-registry boundary.
# - Validate normalizer resolution by parsed content semantics.
# - Validate normalizer-availability checks.
# - Validate unsupported content-media-type behavior.
# - Protect dynamic normalizer-selection semantics.
# - Protect source and file-format isolation from downstream layers.
#
# Must Not:
# - Test concrete normalization implementations.
# - Test physical source acquisition.
# - Test format-specific parsing.
# - Test normalizer plugin loading.
# - Test derivation or chunking.
# - Test embedding, indexing, retrieval, or reranking.
# - Test concurrency or NFT execution strategies.
# - Test Standard RAG, GraphRAG, or Agentic RAG behavior.

import pytest

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


class StubContentNormalizer(ContentNormalizer):
    """Minimal normalizer used to validate registry resolution."""

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
        raise NotImplementedError


class StubNormalizerRegistry(NormalizerRegistry):
    """Minimal registry used to validate the interface contract."""

    def __init__(
        self,
        normalizer: ContentNormalizer,
    ) -> None:
        self._normalizer = normalizer

    def resolve(
        self,
        content_media_type: str,
    ) -> ContentNormalizer:
        if not self._normalizer.supports(
            content_media_type
        ):
            raise LookupError(
                "normalizer not found for content media type: "
                f"{content_media_type}"
            )

        return self._normalizer

    def contains(
        self,
        content_media_type: str,
    ) -> bool:
        return self._normalizer.supports(
            content_media_type
        )


class MissingResolveRegistry(NormalizerRegistry):
    """Invalid registry missing normalizer resolution."""

    def contains(
        self,
        content_media_type: str,
    ) -> bool:
        return False


class MissingContainsRegistry(NormalizerRegistry):
    """Invalid registry missing availability behavior."""

    def resolve(
        self,
        content_media_type: str,
    ) -> ContentNormalizer:
        return StubContentNormalizer()


def _registry() -> StubNormalizerRegistry:
    return StubNormalizerRegistry(
        StubContentNormalizer()
    )


def test_normalizer_registry_is_abstract() -> None:
    with pytest.raises(TypeError):
        NormalizerRegistry()


def test_missing_resolve_prevents_instantiation() -> None:
    with pytest.raises(TypeError):
        MissingResolveRegistry()


def test_missing_contains_prevents_instantiation() -> None:
    with pytest.raises(TypeError):
        MissingContainsRegistry()


def test_concrete_registry_can_be_instantiated() -> None:
    registry = _registry()

    assert isinstance(
        registry,
        NormalizerRegistry,
    )


def test_resolve_returns_content_normalizer() -> None:
    registry = _registry()

    normalizer = registry.resolve(
        "text/plain"
    )

    assert isinstance(
        normalizer,
        ContentNormalizer,
    )


def test_resolve_returns_configured_normalizer() -> None:
    normalizer = StubContentNormalizer()
    registry = StubNormalizerRegistry(
        normalizer
    )

    resolved = registry.resolve(
        "text/plain"
    )

    assert resolved is normalizer


def test_contains_returns_true_for_supported_content() -> None:
    registry = _registry()

    assert registry.contains(
        "text/plain"
    ) is True


def test_contains_returns_false_for_unsupported_content() -> None:
    registry = _registry()

    assert registry.contains(
        "application/json"
    ) is False


def test_unknown_content_type_raises_lookup_error() -> None:
    registry = _registry()

    with pytest.raises(
        LookupError,
        match=(
            "normalizer not found for content media type: "
            "application/json"
        ),
    ):
        registry.resolve(
            "application/json"
        )


def test_registry_preserves_normalizer_identity() -> None:
    registry = _registry()

    normalizer = registry.resolve(
        "text/plain"
    )

    assert normalizer.normalizer_ref == "text-normalizer"
    assert normalizer.normalizer_version == "1.0"
