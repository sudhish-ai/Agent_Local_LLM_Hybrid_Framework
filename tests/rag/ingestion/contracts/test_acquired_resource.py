# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF AcquiredResource contract.
#
# Responsibilities:
# - Validate acquired resource composition.
# - Validate stable resource and revision identity preservation.
# - Validate provider-neutral binary content preservation.
# - Validate media-type semantics.
# - Validate optional content fingerprints.
# - Validate resource-size reporting.
# - Validate input normalization and rejection.
# - Validate immutability.
#
# Must Not:
# - Test physical source acquisition.
# - Test parsing or normalization.
# - Test content fingerprint generation.
# - Test synchronization or change detection.
# - Test chunking, embedding, indexing, or retrieval.
# - Test provider-specific behavior.

from dataclasses import FrozenInstanceError

import pytest

from alhf.rag.ingestion.contracts.acquired_resource import (
    AcquiredResource,
)
from alhf.rag.ingestion.contracts.resource_identity import (
    ResourceIdentity,
)


def _identity() -> ResourceIdentity:
    return ResourceIdentity(
        knowledge_scope_ref="scope-001",
        source_ref="source-001",
        logical_resource_id="resource-001",
        revision_id="revision-001",
    )


def test_create_minimal_acquired_resource() -> None:
    identity = _identity()

    resource = AcquiredResource(
        identity=identity,
        content=b"knowledge content",
        media_type="text/plain",
    )

    assert resource.identity is identity
    assert resource.content == b"knowledge content"
    assert resource.media_type == "text/plain"
    assert resource.content_fingerprint is None


def test_create_resource_with_fingerprint() -> None:
    resource = AcquiredResource(
        identity=_identity(),
        content=b"knowledge content",
        media_type="application/pdf",
        content_fingerprint="sha256:abc123",
    )

    assert resource.content_fingerprint == "sha256:abc123"


def test_media_type_is_whitespace_normalized() -> None:
    resource = AcquiredResource(
        identity=_identity(),
        content=b"content",
        media_type="  application/pdf  ",
    )

    assert resource.media_type == "application/pdf"


def test_content_fingerprint_is_whitespace_normalized() -> None:
    resource = AcquiredResource(
        identity=_identity(),
        content=b"content",
        media_type="text/plain",
        content_fingerprint="  sha256:abc123  ",
    )

    assert resource.content_fingerprint == "sha256:abc123"


def test_resource_ref_returns_logical_resource_identity() -> None:
    resource = AcquiredResource(
        identity=_identity(),
        content=b"content",
        media_type="text/plain",
    )

    assert resource.resource_ref == "resource-001"


def test_revision_ref_returns_exact_revision_identity() -> None:
    resource = AcquiredResource(
        identity=_identity(),
        content=b"content",
        media_type="text/plain",
    )

    assert resource.revision_ref == "revision-001"


def test_size_bytes_returns_content_size() -> None:
    content = b"1234567890"

    resource = AcquiredResource(
        identity=_identity(),
        content=content,
        media_type="application/octet-stream",
    )

    assert resource.size_bytes == len(content)
    assert resource.size_bytes == 10


def test_empty_binary_content_is_supported() -> None:
    resource = AcquiredResource(
        identity=_identity(),
        content=b"",
        media_type="application/octet-stream",
    )

    assert resource.content == b""
    assert resource.size_bytes == 0


def test_identity_rejects_invalid_contract() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "identity must be an instance of ResourceIdentity"
        ),
    ):
        AcquiredResource(
            identity="invalid-identity",
            content=b"content",
            media_type="text/plain",
        )


def test_content_rejects_string_value() -> None:
    with pytest.raises(
        TypeError,
        match="content must be bytes",
    ):
        AcquiredResource(
            identity=_identity(),
            content="content",
            media_type="text/plain",
        )


def test_content_rejects_bytearray_value() -> None:
    with pytest.raises(
        TypeError,
        match="content must be bytes",
    ):
        AcquiredResource(
            identity=_identity(),
            content=bytearray(b"content"),
            media_type="text/plain",
        )


@pytest.mark.parametrize(
    "media_type",
    (
        "",
        "   ",
    ),
)
def test_media_type_rejects_empty_value(
    media_type: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="media_type cannot be empty",
    ):
        AcquiredResource(
            identity=_identity(),
            content=b"content",
            media_type=media_type,
        )


def test_media_type_rejects_non_string_value() -> None:
    with pytest.raises(
        TypeError,
        match="media_type must be a string",
    ):
        AcquiredResource(
            identity=_identity(),
            content=b"content",
            media_type=123,
        )


@pytest.mark.parametrize(
    "content_fingerprint",
    (
        "",
        "   ",
    ),
)
def test_fingerprint_rejects_empty_value_when_provided(
    content_fingerprint: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "content_fingerprint cannot be empty when provided"
        ),
    ):
        AcquiredResource(
            identity=_identity(),
            content=b"content",
            media_type="text/plain",
            content_fingerprint=content_fingerprint,
        )


def test_fingerprint_rejects_non_string_value() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "content_fingerprint must be a string or None"
        ),
    ):
        AcquiredResource(
            identity=_identity(),
            content=b"content",
            media_type="text/plain",
            content_fingerprint=123,
        )


def test_resource_preserves_identity_without_duplication() -> None:
    identity = _identity()

    resource = AcquiredResource(
        identity=identity,
        content=b"content",
        media_type="text/plain",
    )

    assert resource.identity is identity
    assert resource.resource_ref == identity.resource_ref
    assert resource.revision_ref == identity.revision_ref


def test_acquired_resource_is_immutable() -> None:
    resource = AcquiredResource(
        identity=_identity(),
        content=b"content",
        media_type="text/plain",
    )

    with pytest.raises(FrozenInstanceError):
        resource.media_type = "application/pdf"
