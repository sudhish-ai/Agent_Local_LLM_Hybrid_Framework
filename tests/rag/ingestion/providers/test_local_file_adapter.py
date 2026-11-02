# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF LocalFileAdapter.
#
# Responsibilities:
# - Validate local file acquisition.
# - Validate recursive and non-recursive discovery.
# - Validate deterministic resource ordering.
# - Validate resource and revision identity.
# - Validate content fingerprints and media types.
# - Validate per-resource size enforcement.
# - Validate Knowledge source compatibility.
# - Validate local root configuration.
#
# Must Not:
# - Test parsing or normalization.
# - Test chunking, embedding, indexing, or retrieval.
# - Test synchronization orchestration.
# - Test concurrency or NFT behavior.
# - Test cloud source providers.
# - Test Standard RAG, GraphRAG, or Agentic RAG behavior.

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
from alhf.rag.ingestion.providers.local_file_adapter import (
    LocalFileAdapter,
)


def _source() -> KnowledgeSource:
    return KnowledgeSource(
        source_id="source-001",
        knowledge_scope_ref="scope-001",
        source_kind=KnowledgeSourceKind.FILE,
        adapter_ref="local-file-adapter",
    )


def _adapter(
    root: Path,
    *,
    max_resource_bytes: int = 1024,
    recursive: bool = True,
) -> LocalFileAdapter:
    return LocalFileAdapter(
        root_directory=root,
        max_resource_bytes=max_resource_bytes,
        recursive=recursive,
    )


def test_acquire_single_file(
    tmp_path: Path,
) -> None:
    path = tmp_path / "document.txt"
    path.write_bytes(b"hello knowledge")

    resources = tuple(
        _adapter(tmp_path).acquire(_source())
    )

    assert len(resources) == 1
    assert isinstance(resources[0], AcquiredResource)
    assert resources[0].content == b"hello knowledge"


def test_acquire_preserves_source_and_scope(
    tmp_path: Path,
) -> None:
    (tmp_path / "document.txt").write_bytes(b"content")

    resource = next(
        _adapter(tmp_path).acquire(_source())
    )

    assert resource.identity.source_ref == "source-001"
    assert resource.identity.knowledge_scope_ref == "scope-001"


def test_logical_resource_id_is_relative_path(
    tmp_path: Path,
) -> None:
    directory = tmp_path / "policies"
    directory.mkdir()
    (directory / "security.txt").write_bytes(b"policy")

    resource = next(
        _adapter(tmp_path).acquire(_source())
    )

    assert resource.resource_ref == "policies/security.txt"


def test_revision_identity_uses_content_hash(
    tmp_path: Path,
) -> None:
    content = b"enterprise knowledge"
    (tmp_path / "document.txt").write_bytes(content)

    resource = next(
        _adapter(tmp_path).acquire(_source())
    )
    expected = hashlib.sha256(content).hexdigest()

    assert resource.revision_ref == f"sha256:{expected}"
    assert resource.content_fingerprint == f"sha256:{expected}"


def test_text_media_type_is_detected(
    tmp_path: Path,
) -> None:
    (tmp_path / "document.txt").write_bytes(b"content")

    resource = next(
        _adapter(tmp_path).acquire(_source())
    )

    assert resource.media_type == "text/plain"


def test_unknown_media_type_uses_binary_default(
    tmp_path: Path,
) -> None:
    (tmp_path / "document.unknownext").write_bytes(b"content")

    resource = next(
        _adapter(tmp_path).acquire(_source())
    )

    assert resource.media_type == "application/octet-stream"


def test_recursive_acquisition_reads_nested_file(
    tmp_path: Path,
) -> None:
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "document.txt").write_bytes(b"content")

    resources = tuple(
        _adapter(
            tmp_path,
            recursive=True,
        ).acquire(_source())
    )

    assert len(resources) == 1
    assert resources[0].resource_ref == "nested/document.txt"


def test_non_recursive_acquisition_ignores_nested_file(
    tmp_path: Path,
) -> None:
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "nested.txt").write_bytes(b"nested")
    (tmp_path / "root.txt").write_bytes(b"root")

    resources = tuple(
        _adapter(
            tmp_path,
            recursive=False,
        ).acquire(_source())
    )

    assert len(resources) == 1
    assert resources[0].resource_ref == "root.txt"


def test_files_are_acquired_in_deterministic_order(
    tmp_path: Path,
) -> None:
    (tmp_path / "c.txt").write_bytes(b"c")
    (tmp_path / "a.txt").write_bytes(b"a")
    (tmp_path / "b.txt").write_bytes(b"b")

    resources = tuple(
        _adapter(tmp_path).acquire(_source())
    )

    assert tuple(
        resource.resource_ref for resource in resources
    ) == (
        "a.txt",
        "b.txt",
        "c.txt",
    )


def test_resource_exceeding_size_limit_is_rejected(
    tmp_path: Path,
) -> None:
    (tmp_path / "large.bin").write_bytes(b"x" * 11)

    adapter = _adapter(
        tmp_path,
        max_resource_bytes=10,
    )

    with pytest.raises(
        ValueError,
        match="local resource exceeds max_resource_bytes",
    ):
        tuple(adapter.acquire(_source()))


def test_non_file_source_kind_is_rejected(
    tmp_path: Path,
) -> None:
    source = KnowledgeSource(
        source_id="source-001",
        knowledge_scope_ref="scope-001",
        source_kind=KnowledgeSourceKind.API,
        adapter_ref="local-file-adapter",
    )

    with pytest.raises(
        ValueError,
        match="LocalFileAdapter requires FILE source kind",
    ):
        tuple(_adapter(tmp_path).acquire(source))


def test_missing_root_directory_is_rejected(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        FileNotFoundError,
        match="root_directory does not exist",
    ):
        _adapter(tmp_path / "missing")


def test_file_cannot_be_used_as_root_directory(
    tmp_path: Path,
) -> None:
    path = tmp_path / "document.txt"
    path.write_bytes(b"content")

    with pytest.raises(
        NotADirectoryError,
        match="root_directory must be a directory",
    ):
        _adapter(path)


@pytest.mark.parametrize(
    "max_resource_bytes",
    (0, -1),
)
def test_resource_size_bound_must_be_positive(
    tmp_path: Path,
    max_resource_bytes: int,
) -> None:
    with pytest.raises(
        ValueError,
        match="max_resource_bytes must be greater than zero",
    ):
        _adapter(
            tmp_path,
            max_resource_bytes=max_resource_bytes,
        )


def test_empty_root_directory_produces_no_resources(
    tmp_path: Path,
) -> None:
    resources = tuple(
        _adapter(tmp_path).acquire(_source())
    )

    assert resources == ()
