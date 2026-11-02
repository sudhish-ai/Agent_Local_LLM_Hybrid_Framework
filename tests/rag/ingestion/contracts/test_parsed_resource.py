# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF ParsedResource contract.
#
# Responsibilities:
# - Validate parsed-resource construction.
# - Validate ResourceIdentity preservation.
# - Validate parsed binary representation preservation.
# - Validate source and parsed media-type semantics.
# - Validate parser identity and version preservation.
# - Validate metadata normalization.
# - Validate parsed representation size reporting.
# - Validate contract immutability.
#
# Must Not:
# - Test concrete parsers.
# - Test physical source acquisition.
# - Test content normalization.
# - Test chunking, embedding, indexing, or retrieval.
# - Test concurrency or NFT behavior.
# - Test source-specific or retrieval-strategy-specific behavior.

from dataclasses import FrozenInstanceError

import pytest

from alhf.rag.ingestion.contracts.parsed_resource import (
    ParsedResource,
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


def _parsed_resource() -> ParsedResource:
    return ParsedResource(
        identity=_identity(),
        content=b"parsed knowledge",
        content_media_type="text/plain",
        source_media_type="application/pdf",
        parser_ref="pdf-parser",
        parser_version="1.0",
    )


def test_create_parsed_resource() -> None:
    resource = _parsed_resource()

    assert resource.content == b"parsed knowledge"
    assert resource.content_media_type == "text/plain"
    assert resource.source_media_type == "application/pdf"
    assert resource.parser_ref == "pdf-parser"
    assert resource.parser_version == "1.0"


def test_resource_identity_is_preserved() -> None:
    identity = _identity()

    resource = ParsedResource(
        identity=identity,
        content=b"parsed knowledge",
        content_media_type="text/plain",
        source_media_type="application/pdf",
        parser_ref="pdf-parser",
        parser_version="1.0",
    )

    assert resource.identity is identity


def test_resource_ref_is_preserved() -> None:
    resource = _parsed_resource()

    assert resource.resource_ref == "resource-001"


def test_revision_ref_is_preserved() -> None:
    resource = _parsed_resource()

    assert resource.revision_ref == "revision-001"


def test_size_bytes_returns_parsed_content_size() -> None:
    resource = _parsed_resource()

    assert resource.size_bytes == len(b"parsed knowledge")


def test_empty_parsed_content_is_supported() -> None:
    resource = ParsedResource(
        identity=_identity(),
        content=b"",
        content_media_type="text/plain",
        source_media_type="text/plain",
        parser_ref="text-parser",
        parser_version="1.0",
    )

    assert resource.content == b""
    assert resource.size_bytes == 0


def test_metadata_values_are_normalized() -> None:
    resource = ParsedResource(
        identity=_identity(),
        content=b"content",
        content_media_type="  text/plain  ",
        source_media_type="  application/pdf  ",
        parser_ref="  pdf-parser  ",
        parser_version="  1.0  ",
    )

    assert resource.content_media_type == "text/plain"
    assert resource.source_media_type == "application/pdf"
    assert resource.parser_ref == "pdf-parser"
    assert resource.parser_version == "1.0"


def test_invalid_identity_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match="identity must be an instance of ResourceIdentity",
    ):
        ParsedResource(
            identity="invalid-identity",
            content=b"content",
            content_media_type="text/plain",
            source_media_type="application/pdf",
            parser_ref="pdf-parser",
            parser_version="1.0",
        )


def test_non_bytes_content_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match="content must be bytes",
    ):
        ParsedResource(
            identity=_identity(),
            content="parsed content",
            content_media_type="text/plain",
            source_media_type="application/pdf",
            parser_ref="pdf-parser",
            parser_version="1.0",
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "content_media_type",
        "source_media_type",
        "parser_ref",
        "parser_version",
    ),
)
def test_required_metadata_rejects_empty_value(
    field_name: str,
) -> None:
    values = {
        "identity": _identity(),
        "content": b"content",
        "content_media_type": "text/plain",
        "source_media_type": "application/pdf",
        "parser_ref": "pdf-parser",
        "parser_version": "1.0",
    }
    values[field_name] = "   "

    with pytest.raises(
        ValueError,
        match=f"{field_name} cannot be empty",
    ):
        ParsedResource(**values)


@pytest.mark.parametrize(
    "field_name",
    (
        "content_media_type",
        "source_media_type",
        "parser_ref",
        "parser_version",
    ),
)
def test_required_metadata_rejects_non_string(
    field_name: str,
) -> None:
    values = {
        "identity": _identity(),
        "content": b"content",
        "content_media_type": "text/plain",
        "source_media_type": "application/pdf",
        "parser_ref": "pdf-parser",
        "parser_version": "1.0",
    }
    values[field_name] = 123

    with pytest.raises(
        TypeError,
        match=f"{field_name} must be a string",
    ):
        ParsedResource(**values)


def test_parsed_resource_is_immutable() -> None:
    resource = _parsed_resource()

    with pytest.raises(FrozenInstanceError):
        resource.parser_version = "2.0"
