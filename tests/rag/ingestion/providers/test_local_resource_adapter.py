# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Verifies exact-resource local acquisition for the ALHF Knowledge
# Foundation ingestion plane.
#
# Problem Solved:
# A single local file supplied as a Knowledge source must be acquired
# exactly, without sibling discovery or changes to directory acquisition.
#
# Responsibilities:
# - Verify exactly one configured file is acquired.
# - Verify sibling resources are never acquired.
# - Verify source, scope, resource, and revision identity.
# - Verify content fingerprint and media-type detection.
# - Verify per-resource size enforcement.
# - Verify source compatibility and path validation.
#
# Must Not:
# - Test directory-oriented LocalFileAdapter behavior.
# - Test parsing, normalization, derivation, or indexing.
# - Test runtime source binding.
# - Test synchronization or execution policy.
# - Test downstream RAG behavior.

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from alhf.rag.ingestion.contracts.acquired_resource import (
    AcquiredResource,
)
from alhf.rag.ingestion.contracts.knowledge_source import (
    KnowledgeSource,
    KnowledgeSourceKind,
)
from alhf.rag.ingestion.providers.local_resource_adapter import (
    LocalResourceAdapter,
)


def _source() -> KnowledgeSource:
    return KnowledgeSource(
        source_id="source-001",
        knowledge_scope_ref="scope-001",
        source_kind=KnowledgeSourceKind.FILE,
        adapter_ref="local-file",
    )


def _adapter(
    path: Path,
    *,
    max_resource_bytes: int = 1024,
) -> LocalResourceAdapter:
    return LocalResourceAdapter(
        resource_path=path,
        max_resource_bytes=max_resource_bytes,
    )


def test_acquires_exact_configured_resource(
    tmp_path: Path,
) -> None:
    path = tmp_path / "document.txt"
    path.write_bytes(b"hello knowledge")

    resources = tuple(
        _adapter(path).acquire(_source())
    )

    assert len(resources) == 1
    assert isinstance(resources[0], AcquiredResource)
    assert resources[0].content == b"hello knowledge"
    assert resources[0].resource_ref == "document.txt"


def test_does_not_acquire_sibling_resources(
    tmp_path: Path,
) -> None:
    target = tmp_path / "target.txt"
    target.write_bytes(b"target")
    (tmp_path / "sibling.txt").write_bytes(b"sibling")

    resources = tuple(
        _adapter(target).acquire(_source())
    )

    assert len(resources) == 1
    assert resources[0].resource_ref == "target.txt"
    assert resources[0].content == b"target"


def test_preserves_source_and_scope(
    tmp_path: Path,
) -> None:
    path = tmp_path / "document.txt"
    path.write_bytes(b"content")

    resource = next(
        _adapter(path).acquire(_source())
    )

    assert resource.identity.source_ref == "source-001"
    assert resource.identity.knowledge_scope_ref == "scope-001"


def test_revision_identity_uses_content_hash(
    tmp_path: Path,
) -> None:
    content = b"enterprise knowledge"
    path = tmp_path / "document.txt"
    path.write_bytes(content)

    resource = next(
        _adapter(path).acquire(_source())
    )
    expected = hashlib.sha256(content).hexdigest()

    assert resource.revision_ref == f"sha256:{expected}"
    assert resource.content_fingerprint == f"sha256:{expected}"


def test_text_media_type_is_detected(
    tmp_path: Path,
) -> None:
    path = tmp_path / "document.txt"
    path.write_bytes(b"content")

    resource = next(
        _adapter(path).acquire(_source())
    )

    assert resource.media_type == "text/plain"


def test_unknown_media_type_uses_binary_default(
    tmp_path: Path,
) -> None:
    path = tmp_path / "document.unknownext"
    path.write_bytes(b"content")

    resource = next(
        _adapter(path).acquire(_source())
    )

    assert resource.media_type == "application/octet-stream"


def test_resource_exceeding_size_limit_is_rejected(
    tmp_path: Path,
) -> None:
    path = tmp_path / "large.bin"
    path.write_bytes(b"x" * 11)

    with pytest.raises(
        ValueError,
        match="local resource exceeds max_resource_bytes",
    ):
        tuple(
            _adapter(
                path,
                max_resource_bytes=10,
            ).acquire(_source())
        )


def test_non_file_source_kind_is_rejected(
    tmp_path: Path,
) -> None:
    path = tmp_path / "document.txt"
    path.write_bytes(b"content")

    source = KnowledgeSource(
        source_id="source-001",
        knowledge_scope_ref="scope-001",
        source_kind=KnowledgeSourceKind.API,
        adapter_ref="local-file",
    )

    with pytest.raises(
        ValueError,
        match="LocalResourceAdapter requires FILE source kind",
    ):
        tuple(
            _adapter(path).acquire(source)
        )


def test_missing_resource_is_rejected(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        FileNotFoundError,
        match="resource_path does not exist",
    ):
        _adapter(tmp_path / "missing.txt")


def test_directory_cannot_be_used_as_exact_resource(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        IsADirectoryError,
        match="resource_path must identify a file",
    ):
        _adapter(tmp_path)


@pytest.mark.parametrize(
    "max_resource_bytes",
    (0, -1),
)
def test_resource_size_bound_must_be_positive(
    tmp_path: Path,
    max_resource_bytes: int,
) -> None:
    path = tmp_path / "document.txt"
    path.write_bytes(b"content")

    with pytest.raises(
        ValueError,
        match="max_resource_bytes must be greater than zero",
    ):
        _adapter(
            path,
            max_resource_bytes=max_resource_bytes,
        )


def test_revision_changes_when_content_changes(
    tmp_path: Path,
) -> None:
    path = tmp_path / "document.txt"
    path.write_bytes(b"version one")
    first = next(
        _adapter(path).acquire(_source())
    )

    path.write_bytes(b"version two")
    second = next(
        _adapter(path).acquire(_source())
    )

    assert first.resource_ref == second.resource_ref
    assert first.revision_ref != second.revision_ref
