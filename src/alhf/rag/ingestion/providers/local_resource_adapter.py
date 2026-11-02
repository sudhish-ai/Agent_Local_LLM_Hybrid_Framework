# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides exact-resource local acquisition for the ALHF Knowledge
# Foundation ingestion plane.
#
# Problem Solved:
# A customer may supply one local file as a Knowledge source. ALHF must
# acquire exactly that resource without expanding acquisition to sibling
# files or changing the frozen directory-oriented LocalFileAdapter.
#
# Responsibilities:
# - Acquire exactly one configured local file.
# - Enforce the configured per-resource size bound.
# - Preserve governed Knowledge scope and source identity.
# - Generate content-derived revision identity and fingerprint.
# - Detect media type without parsing resource content.
# - Produce one provider-neutral AcquiredResource incrementally.
#
# Must Not:
# - Discover or acquire sibling resources.
# - Acquire directories or recursively enumerate filesystem state.
# - Modify directory-oriented LocalFileAdapter behavior.
# - Parse, normalize, derive, represent, index, or retrieve Knowledge.
# - Perform synchronization or continuation orchestration.
# - Implement execution policy.
# - Contain downstream RAG-mode behavior.
#
# Architectural Position:
# - Concrete KnowledgeSourceAdapter for one exact local resource.
# - Complements collection-oriented local acquisition.
# - Converges immediately into the universal AcquiredResource boundary.
#
# Future Extensibility:
# - Source binding can choose exact-resource or collection acquisition.
# - Other source technologies can provide their own physical adapters.
# - Downstream Knowledge processing remains independent from source scope.

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


class LocalResourceAdapter(KnowledgeSourceAdapter):
    """Acquire exactly one configured local filesystem resource."""

    def __init__(
        self,
        *,
        resource_path: str | Path,
        max_resource_bytes: int,
    ) -> None:
        self._resource_path = self._validate_resource_path(
            resource_path,
        )
        self._max_resource_bytes = self._positive_int(
            max_resource_bytes,
        )

    def acquire(
        self,
        source: KnowledgeSource,
    ) -> Iterator[AcquiredResource]:
        """Yield exactly one configured local resource."""

        self._validate_source(
            source,
        )

        size_bytes = self._resource_path.stat().st_size

        if size_bytes > self._max_resource_bytes:
            raise ValueError(
                "local resource exceeds max_resource_bytes"
            )

        content = self._resource_path.read_bytes()
        fingerprint = hashlib.sha256(
            content,
        ).hexdigest()

        yield AcquiredResource(
            identity=ResourceIdentity(
                knowledge_scope_ref=source.knowledge_scope_ref,
                source_ref=source.source_id,
                logical_resource_id=self._resource_path.name,
                revision_id=f"sha256:{fingerprint}",
            ),
            content=content,
            media_type=self._media_type(
                self._resource_path,
            ),
            content_fingerprint=f"sha256:{fingerprint}",
        )

    @staticmethod
    def _validate_source(
        source: KnowledgeSource,
    ) -> None:
        """Validate logical-source compatibility."""

        if not isinstance(
            source,
            KnowledgeSource,
        ):
            raise TypeError(
                "source must be an instance of KnowledgeSource"
            )

        if source.source_kind != KnowledgeSourceKind.FILE:
            raise ValueError(
                "LocalResourceAdapter requires FILE source kind"
            )

    @staticmethod
    def _validate_resource_path(
        resource_path: str | Path,
    ) -> Path:
        """Validate and resolve one exact local resource."""

        if isinstance(
            resource_path,
            str,
        ):
            if not resource_path.strip():
                raise ValueError(
                    "resource_path cannot be empty"
                )

            path = Path(
                resource_path.strip(),
            )
        elif isinstance(
            resource_path,
            Path,
        ):
            path = resource_path
        else:
            raise TypeError(
                "resource_path must be a string or Path"
            )

        if not path.exists():
            raise FileNotFoundError(
                "resource_path does not exist"
            )

        if not path.is_file():
            raise IsADirectoryError(
                "resource_path must identify a file"
            )

        return path.resolve()

    @staticmethod
    def _media_type(
        path: Path,
    ) -> str:
        """Return the media type of one local resource."""

        return (
            mimetypes.guess_type(
                path.name,
            )[0]
            or "application/octet-stream"
        )

    @staticmethod
    def _positive_int(
        value: int,
    ) -> int:
        """Validate a positive per-resource byte bound."""

        if isinstance(
            value,
            bool,
        ) or not isinstance(
            value,
            int,
        ):
            raise TypeError(
                "max_resource_bytes must be an int"
            )

        if value <= 0:
            raise ValueError(
                "max_resource_bytes must be greater than zero"
            )

        return value
