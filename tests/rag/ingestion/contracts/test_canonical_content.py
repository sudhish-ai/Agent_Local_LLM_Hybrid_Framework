# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF CanonicalContent contract.
#
# Responsibilities:
# - Validate canonical Knowledge content construction.
# - Validate ResourceIdentity preservation.
# - Validate universal canonical content kinds.
# - Validate canonical media-type semantics.
# - Validate parsed-artifact provenance.
# - Validate normalizer identity and version.
# - Validate canonical-content size reporting.
# - Validate normalization of required reference values.
# - Validate contract immutability.
#
# Must Not:
# - Test physical source acquisition.
# - Test format-specific parsing.
# - Test normalization execution.
# - Test derivation or chunking.
# - Test embedding, indexing, or retrieval.
# - Test concurrency or NFT execution strategies.
# - Test source-specific or file-format-specific behavior.

from dataclasses import FrozenInstanceError

import pytest

from alhf.rag.ingestion.contracts.canonical_content import (
    CanonicalContent,
    CanonicalContentKind,
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


def _content() -> CanonicalContent:
    return CanonicalContent(
        identity=_identity(),
        content=b"canonical enterprise knowledge",
        content_kind=CanonicalContentKind.TEXT,
        media_type="text/plain",
        parsed_artifact_ref="parsed-artifact-001",
        normalizer_ref="text-normalizer",
        normalizer_version="1.0",
    )


def test_create_canonical_content() -> None:
    content = _content()

    assert content.content == b"canonical enterprise knowledge"
    assert content.content_kind == CanonicalContentKind.TEXT
    assert content.media_type == "text/plain"
    assert content.parsed_artifact_ref == "parsed-artifact-001"
    assert content.normalizer_ref == "text-normalizer"
    assert content.normalizer_version == "1.0"


def test_resource_identity_is_preserved() -> None:
    identity = _identity()

    content = CanonicalContent(
        identity=identity,
        content=b"knowledge",
        content_kind=CanonicalContentKind.TEXT,
        media_type="text/plain",
        parsed_artifact_ref="parsed-001",
        normalizer_ref="normalizer",
        normalizer_version="1.0",
    )

    assert content.identity is identity


def test_identity_properties_are_exposed() -> None:
    content = _content()

    assert content.resource_ref == "resource-001"
    assert content.revision_ref == "revision-001"
    assert content.knowledge_scope_ref == "scope-001"


def test_size_bytes_reports_content_size() -> None:
    content = _content()

    assert content.size_bytes == len(
        b"canonical enterprise knowledge"
    )


def test_empty_canonical_content_is_supported() -> None:
    content = CanonicalContent(
        identity=_identity(),
        content=b"",
        content_kind=CanonicalContentKind.TEXT,
        media_type="text/plain",
        parsed_artifact_ref="parsed-001",
        normalizer_ref="normalizer",
        normalizer_version="1.0",
    )

    assert content.content == b""
    assert content.size_bytes == 0


@pytest.mark.parametrize(
    "content_kind",
    tuple(CanonicalContentKind),
)
def test_all_canonical_content_kinds_are_supported(
    content_kind: CanonicalContentKind,
) -> None:
    content = CanonicalContent(
        identity=_identity(),
        content=b"canonical content",
        content_kind=content_kind,
        media_type="application/octet-stream",
        parsed_artifact_ref="parsed-001",
        normalizer_ref="normalizer",
        normalizer_version="1.0",
    )

    assert content.content_kind == content_kind


def test_required_text_values_are_normalized() -> None:
    content = CanonicalContent(
        identity=_identity(),
        content=b"knowledge",
        content_kind=CanonicalContentKind.TEXT,
        media_type="  text/plain  ",
        parsed_artifact_ref="  parsed-001  ",
        normalizer_ref="  normalizer  ",
        normalizer_version="  1.0  ",
    )

    assert content.media_type == "text/plain"
    assert content.parsed_artifact_ref == "parsed-001"
    assert content.normalizer_ref == "normalizer"
    assert content.normalizer_version == "1.0"


def test_invalid_identity_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match="identity must be an instance of ResourceIdentity",
    ):
        CanonicalContent(
            identity="invalid-identity",
            content=b"knowledge",
            content_kind=CanonicalContentKind.TEXT,
            media_type="text/plain",
            parsed_artifact_ref="parsed-001",
            normalizer_ref="normalizer",
            normalizer_version="1.0",
        )


def test_non_bytes_content_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match="content must be bytes",
    ):
        CanonicalContent(
            identity=_identity(),
            content="knowledge",
            content_kind=CanonicalContentKind.TEXT,
            media_type="text/plain",
            parsed_artifact_ref="parsed-001",
            normalizer_ref="normalizer",
            normalizer_version="1.0",
        )


def test_invalid_content_kind_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "content_kind must be an instance of "
            "CanonicalContentKind"
        ),
    ):
        CanonicalContent(
            identity=_identity(),
            content=b"knowledge",
            content_kind="TEXT",
            media_type="text/plain",
            parsed_artifact_ref="parsed-001",
            normalizer_ref="normalizer",
            normalizer_version="1.0",
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "media_type",
        "parsed_artifact_ref",
        "normalizer_ref",
        "normalizer_version",
    ),
)
def test_required_text_rejects_empty_value(
    field_name: str,
) -> None:
    values = {
        "identity": _identity(),
        "content": b"knowledge",
        "content_kind": CanonicalContentKind.TEXT,
        "media_type": "text/plain",
        "parsed_artifact_ref": "parsed-001",
        "normalizer_ref": "normalizer",
        "normalizer_version": "1.0",
    }
    values[field_name] = "   "

    with pytest.raises(
        ValueError,
        match=f"{field_name} cannot be empty",
    ):
        CanonicalContent(**values)


@pytest.mark.parametrize(
    "field_name",
    (
        "media_type",
        "parsed_artifact_ref",
        "normalizer_ref",
        "normalizer_version",
    ),
)
def test_required_text_rejects_non_string(
    field_name: str,
) -> None:
    values = {
        "identity": _identity(),
        "content": b"knowledge",
        "content_kind": CanonicalContentKind.TEXT,
        "media_type": "text/plain",
        "parsed_artifact_ref": "parsed-001",
        "normalizer_ref": "normalizer",
        "normalizer_version": "1.0",
    }
    values[field_name] = 123

    with pytest.raises(
        TypeError,
        match=f"{field_name} must be a string",
    ):
        CanonicalContent(**values)


def test_canonical_content_is_immutable() -> None:
    content = _content()

    with pytest.raises(FrozenInstanceError):
        content.normalizer_version = "2.0"
