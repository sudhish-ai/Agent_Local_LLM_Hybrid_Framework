# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the provider-neutral acquisition-service boundary used by the
# ALHF Knowledge Foundation ingestion plane.
#
# Problem Solved:
# Acquisition callers require a stable boundary that accepts bounded
# acquisition requests without depending on concrete source adapters,
# provider configuration, or physical source technology.
#
# Responsibilities:
# - Accept one validated bounded AcquisitionRequest.
# - Yield acquired resources incrementally.
# - Return provider-neutral acquisition completion state separately.
# - Preserve bounded, streaming-oriented acquisition semantics.
# - Keep acquisition callers independent from concrete source adapters.
#
# Must Not:
# - Materialize an entire source in memory.
# - Store credentials, secrets, paths, URLs, or connection details.
# - Select concrete providers through hard-coded conditionals.
# - Parse or normalize acquired content.
# - Perform chunking, embedding, indexing, or retrieval.
# - Generate source, resource, or revision identities.
# - Define synchronization implementation.
# - Contain Standard, Graph, or Agentic RAG behavior.
#
# Architectural Position:
# - Stable application boundary for the Knowledge acquisition plane.
# - Sits above concrete KnowledgeSourceAdapter implementations.
# - Separates acquisition orchestration from physical source access.
#
# Future Extensibility:
# - Adapter routing can evolve independently behind implementations.
# - Synchronization can orchestrate this boundary using checkpoints.
# - Capability-aware provider selection can evolve without changing
#   acquisition callers.
# - Local, cloud, and hybrid deployments can implement the same boundary.

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator

from alhf.rag.ingestion.contracts.acquired_resource import (
    AcquiredResource,
)
from alhf.rag.ingestion.contracts.acquisition_request import (
    AcquisitionRequest,
)
from alhf.rag.ingestion.contracts.acquisition_result import (
    AcquisitionResult,
)


class AcquisitionSession(ABC):
    """
    Bounded acquisition session.

    Resources are consumed incrementally through iteration. Completion
    state is available only after the bounded acquisition has finished.
    """

    @abstractmethod
    def resources(
        self,
    ) -> Iterator:
        """Yield acquired resources incrementally."""

        raise NotImplementedError

    @abstractmethod
    def result(
        self,
    ) -> AcquisitionResult:
        """
        Return the completed bounded acquisition result.

        Implementations must reject result access before acquisition has
        reached its terminal state.
        """

        raise NotImplementedError


class AcquisitionService(ABC):
    """
    Universal application boundary for bounded Knowledge acquisition.

    Implementations coordinate source adapters while callers remain
    independent from physical source technologies.
    """

    @abstractmethod
    def acquire(
        self,
        request: AcquisitionRequest,
    ) -> AcquisitionSession:
        """
        Start one bounded Knowledge acquisition operation.

        Args:
            request:
                Validated bounded acquisition request.

        Returns:
            Acquisition session exposing incremental resources and the
            eventual provider-neutral acquisition result.
        """

        raise NotImplementedError
