# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the universal acquisition-adapter boundary used by the
# ALHF Knowledge Foundation ingestion plane.
#
# Problem Solved:
# ALHF must acquire Knowledge resources from many physical source
# technologies without coupling the common ingestion pipeline to local
# files, object storage, databases, APIs, collaboration systems, or
# future source technologies.
#
# Responsibilities:
# - Define provider-neutral acquisition behavior for one Knowledge source.
# - Accept a validated logical KnowledgeSource.
# - Produce acquired resources incrementally.
# - Preserve bounded processing through iterator-based acquisition.
# - Keep physical source behavior behind adapter implementations.
#
# Must Not:
# - Define physical provider configuration.
# - Store credentials, secrets, or connection information.
# - Materialize an entire source into an in-memory collection.
# - Parse or normalize acquired content.
# - Perform chunking, embedding, indexing, or retrieval.
# - Generate KnowledgeSource identity.
# - Perform synchronization orchestration.
# - Contain Standard, Graph, or Agentic RAG behavior.
# - Depend on a concrete local or cloud provider.
#
# Architectural Position:
# - Universal Knowledge Foundation acquisition interface.
# - Boundary between logical sources and concrete source adapters.
# - Concrete adapters implement physical acquisition behind this contract.
#
# Future Extensibility:
# - Local-file, object-storage, database, API, collaboration, and future
#   adapters can implement the same acquisition boundary.
# - Source synchronization can orchestrate this interface independently.
# - Adapter capability discovery remains a separate responsibility.
# - Streaming implementations can preserve bounded acquisition semantics.

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator

from alhf.rag.ingestion.contracts.acquired_resource import (
    AcquiredResource,
)
from alhf.rag.ingestion.contracts.knowledge_source import (
    KnowledgeSource,
)


class KnowledgeSourceAdapter(ABC):
    """
    Universal acquisition adapter for ALHF Knowledge sources.

    Implementations translate one logical KnowledgeSource into a bounded
    stream of AcquiredResource instances.

    The iterator boundary deliberately prevents the common ingestion
    contract from requiring an entire source to be loaded into memory.
    """

    @abstractmethod
    def acquire(
        self,
        source: KnowledgeSource,
    ) -> Iterator[AcquiredResource]:
        """
        Acquire resources from one logical Knowledge source.

        Args:
            source:
                Validated logical Knowledge source to acquire.

        Returns:
            Iterator yielding acquired resource revisions incrementally.
        """

        raise NotImplementedError
