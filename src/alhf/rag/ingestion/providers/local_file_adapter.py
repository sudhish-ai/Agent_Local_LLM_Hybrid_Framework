# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides the local-filesystem Knowledge source adapter used by the
# ALHF Knowledge Foundation V1 acquisition plane.
#
# Problem Solved:
# Local execution requires a concrete adapter capable of acquiring files
# without leaking filesystem behavior into provider-neutral ingestion
# contracts or downstream Knowledge processing stages.
#
# Responsibilities:
# - Acquire files beneath one configured local root directory.
# - Yield AcquiredResource instances incrementally.
# - Produce deterministic logical resource identities.
# - Produce content-derived revision identities and fingerprints.
# - Detect media types without parsing file content.
# - Enforce a configurable per-resource size bound.
# - Preserve Knowledge scope and source identity.
#
# Must Not:
# - Materialize the complete source in memory.
# - Parse, normalize, chunk, embed, index, or retrieve content.
# - Perform synchronization orchestration.
# - Persist checkpoints or continuation state.
# - Follow filesystem entries outside the configured root.
# - Store credentials or secrets.
# - Contain Standard RAG, GraphRAG, or Agentic RAG behavior.
# - Implement threading, multiprocessing, or async execution policy.
#
# Architectural Position:
# - Concrete KnowledgeSourceAdapter for local filesystem acquisition.
# - First physical V1 adapter behind the universal acquisition boundary.
# - Produces provider-neutral AcquiredResource contracts.
#
# Reuse Value:
# - Local development.
# - Local production deployments.
# - Deterministic E2E RAG testing.
# - Offline and air-gapped Knowledge ingestion.
#
# Future Extensibility:
# - Parallel filesystem reading can evolve behind this adapter boundary.
# - File discovery can later become independently partitioned.
# - Synchronization and deletion detection remain separate concerns.
# - Other source technologies require separate adapters, not core changes.

from __future__ import annotations

import hashlib
import mimetypes
from collections.abc import Iterator
from pathlib import Path

from alhf.rag.ingestion.contracts.acquired_resource import (
    AcquiredResource,
)
from alhf.rag.ingestion.contracts.knowledge_source import (
    KnowledgeSource,
    KnowledgeSourceKind,
)
from alhf.rag.ingestion.contracts.resource_identity import (
    ResourceIdentity,
)
from alhf.rag.ingestion.interfaces.knowledge_source_adapter import (
    KnowledgeSourceAdapter,
)


class LocalFileAdapter(KnowledgeSourceAdapter):
    """Incrementally acquire files from one configured local root."""

    def __init__(
        self,
        *,
        root_directory: str | Path,
        max_resource_bytes: int,
        recursive: bool = True,
    ) -> None:
        self._root_directory = self._validate_root(
            root_directory,
        )
        self._max_resource_bytes = self._positive_int(
            max_resource_bytes,
        )

        if not isinstance(recursive, bool):
            raise TypeError(
                "recursive must be a bool"
            )

        self._recursive = recursive

    def acquire(
        self,
        source: KnowledgeSource,
    ) -> Iterator[AcquiredResource]:
        """Yield acquired local files incrementally."""

        self._validate_source(source)

        for path in self._iter_files():
            size_bytes = path.stat().st_size

            if size_bytes > self._max_resource_bytes:
                raise ValueError(
                    "local resource exceeds max_resource_bytes"
                )

            content = path.read_bytes()
            fingerprint = hashlib.sha256(
                content
            ).hexdigest()

            logical_resource_id = path.relative_to(
                self._root_directory
            ).as_posix()

            media_type = (
                mimetypes.guess_type(path.name)[0]
                or "application/octet-stream"
            )

            yield AcquiredResource(
                identity=ResourceIdentity(
                    knowledge_scope_ref=source.knowledge_scope_ref,
                    source_ref=source.source_id,
                    logical_resource_id=logical_resource_id,
                    revision_id=f"sha256:{fingerprint}",
                ),
                content=content,
                media_type=media_type,
                content_fingerprint=f"sha256:{fingerprint}",
            )

    def _iter_files(self) -> Iterator[Path]:
        """Yield regular files in deterministic path order."""

        pattern = "**/*" if self._recursive else "*"

        paths = (
            path
            for path in self._root_directory.glob(pattern)
            if path.is_file()
        )

        yield from sorted(
            paths,
            key=lambda path: path.as_posix(),
        )

    @staticmethod
    def _validate_source(
        source: KnowledgeSource,
    ) -> None:
        """Validate source compatibility with this adapter."""

        if not isinstance(source, KnowledgeSource):
            raise TypeError(
                "source must be an instance of KnowledgeSource"
            )

        if source.source_kind != KnowledgeSourceKind.FILE:
            raise ValueError(
                "LocalFileAdapter requires FILE source kind"
            )

    @staticmethod
    def _validate_root(
        root_directory: str | Path,
    ) -> Path:
        """Validate the configured local source root."""

        if isinstance(root_directory, str):
            if not root_directory.strip():
                raise ValueError(
                    "root_directory cannot be empty"
                )
            path = Path(root_directory.strip())
        elif isinstance(root_directory, Path):
            path = root_directory
        else:
            raise TypeError(
                "root_directory must be a string or Path"
            )

        if not path.exists():
            raise FileNotFoundError(
                "root_directory does not exist"
            )

        if not path.is_dir():
            raise NotADirectoryError(
                "root_directory must be a directory"
            )

        return path.resolve()

    @staticmethod
    def _positive_int(
        value: int,
    ) -> int:
        """Validate a positive per-resource byte bound."""

        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(
                "max_resource_bytes must be an int"
            )

        if value <= 0:
            raise ValueError(
                "max_resource_bytes must be greater than zero"
            )

        return value
