# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF InMemoryNormalizerRegistry provider.
#
# Responsibilities:
# - Validate normalizer registration.
# - Validate normalizer resolution by parsed content media type.
# - Validate normalizer availability checks.
# - Validate deterministic registration-order selection.
# - Validate duplicate normalizer-reference rejection.
# - Validate unsupported content-media-type behavior.
# - Validate registry membership and size semantics.
#
# Must Not:
# - Test concrete normalization algorithms.
# - Test physical source acquisition.
# - Test format-specific parsing.
# - Test plugin loading.
# - Test derivation, chunking, embedding, indexing, or retrieval.
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
from alhf.rag.ingestion.providers.in_memory_normalizer_registry import (
    InMemoryNormalizerRegistry,
)


class StubContentNormalizer(ContentNormalizer):
    """Configurable normalizer used for registry testing."""

    def __init__(
        self,
        *,
        normalizer_ref: str,
        content_media_type: str,
    ) -> None:
        self._normalizer_ref = normalizer_ref
        self._content_media_type = content_media_type

    @property
    def normalizer_ref(self) -> str:
        return self._normalizer_ref

    @property
    def normalizer_version(self) -> str:
        return "1.0"

    def supports(
        self,
        content_media_type: str,
    ) -> bool:
        return content_media_type == self._content_media_type

    def normalize(
        self,
        resource: ParsedResource,
    ) -> CanonicalContent:
        raise NotImplementedError


def _normalizer(
    normalizer_ref: str = "text-normalizer",
    content_media_type: str = "text/plain",
) -> StubContentNormalizer:
    return StubContentNormalizer(
        normalizer_ref=normalizer_ref,
        content_media_type=content_media_type,
    )


def test_create_empty_registry() -> None:
    registry = InMemoryNormalizerRegistry()

    assert len(registry) == 0


def test_register_normalizer() -> None:
    registry = InMemoryNormalizerRegistry()

    registry.register(
        _normalizer()
    )

    assert len(registry) == 1


def test_resolve_returns_registered_normalizer() -> None:
    registry = InMemoryNormalizerRegistry()
    normalizer = _normalizer()

    registry.register(
        normalizer
    )

    resolved = registry.resolve(
        "text/plain"
    )

    assert resolved is normalizer


def test_contains_supported_content_media_type() -> None:
    registry = InMemoryNormalizerRegistry()

    registry.register(
        _normalizer()
    )

    assert registry.contains(
        "text/plain"
    ) is True


def test_contains_unsupported_content_media_type() -> None:
    registry = InMemoryNormalizerRegistry()

    registry.register(
        _normalizer()
    )

    assert registry.contains(
        "application/json"
    ) is False


def test_unknown_content_media_type_raises_lookup_error() -> None:
    registry = InMemoryNormalizerRegistry()

    registry.register(
        _normalizer()
    )

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


def test_multiple_normalizers_are_resolved_independently() -> None:
    registry = InMemoryNormalizerRegistry()

    text = _normalizer(
        "text-normalizer",
        "text/plain",
    )
    structured = _normalizer(
        "structured-normalizer",
        "application/json",
    )

    registry.register(text)
    registry.register(structured)

    assert registry.resolve(
        "text/plain"
    ) is text

    assert registry.resolve(
        "application/json"
    ) is structured


def test_first_compatible_normalizer_is_selected() -> None:
    registry = InMemoryNormalizerRegistry()

    first = _normalizer(
        "first-text-normalizer",
        "text/plain",
    )
    second = _normalizer(
        "second-text-normalizer",
        "text/plain",
    )

    registry.register(first)
    registry.register(second)

    assert registry.resolve(
        "text/plain"
    ) is first


def test_duplicate_normalizer_reference_is_rejected() -> None:
    registry = InMemoryNormalizerRegistry()

    registry.register(
        _normalizer()
    )

    with pytest.raises(
        ValueError,
        match=(
            "normalizer already registered: "
            "text-normalizer"
        ),
    ):
        registry.register(
            _normalizer()
        )


def test_invalid_normalizer_is_rejected() -> None:
    registry = InMemoryNormalizerRegistry()

    with pytest.raises(
        TypeError,
        match=(
            "normalizer must be an instance of "
            "ContentNormalizer"
        ),
    ):
        registry.register(
            "invalid-normalizer"
        )


def test_registered_normalizer_supports_membership() -> None:
    registry = InMemoryNormalizerRegistry()

    registry.register(
        _normalizer()
    )

    assert "text-normalizer" in registry
    assert "  text-normalizer  " in registry


def test_unknown_normalizer_is_not_member() -> None:
    registry = InMemoryNormalizerRegistry()

    assert "missing-normalizer" not in registry


def test_invalid_membership_value_returns_false() -> None:
    registry = InMemoryNormalizerRegistry()

    assert 123 not in registry
    assert "   " not in registry


@pytest.mark.parametrize(
    "content_media_type",
    (
        "",
        "   ",
    ),
)
def test_resolve_rejects_empty_content_media_type(
    content_media_type: str,
) -> None:
    registry = InMemoryNormalizerRegistry()

    with pytest.raises(
        ValueError,
        match="content_media_type cannot be empty",
    ):
        registry.resolve(
            content_media_type
        )


def test_resolve_rejects_non_string_content_media_type() -> None:
    registry = InMemoryNormalizerRegistry()

    with pytest.raises(
        TypeError,
        match="content_media_type must be a string",
    ):
        registry.resolve(
            123
        )


def test_registry_size_tracks_multiple_normalizers() -> None:
    registry = InMemoryNormalizerRegistry()

    registry.register(
        _normalizer(
            "text-normalizer",
            "text/plain",
        )
    )
    registry.register(
        _normalizer(
            "structured-normalizer",
            "application/json",
        )
    )

    assert len(registry) == 2
