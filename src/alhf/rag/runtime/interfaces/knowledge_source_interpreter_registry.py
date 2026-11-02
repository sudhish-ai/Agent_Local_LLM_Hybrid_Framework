# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the stable registry boundary for ALHF Knowledge source
# interpreters used by the production Knowledge Foundation runtime.
#
# Problem Solved:
# Runtime source interpretation must resolve compatible interpreters
# without hard-coding local files, cloud storage, databases, APIs,
# repositories, collaboration systems, or future source technologies.
#
# Responsibilities:
# - Register configured KnowledgeSourceInterpreter implementations.
# - Resolve a compatible interpreter for KnowledgeSourceInput.
# - Report whether compatible interpretation capability is available.
# - Keep interpreter selection behind a stable runtime boundary.
# - Preserve source-only customer interaction.
#
# Must Not:
# - Interpret customer sources directly.
# - Acquire or read Knowledge content.
# - Contain source-technology-specific branching.
# - Select parsers, derivation strategies, representations, or indexes.
# - Perform retrieval or Knowledge query execution.
# - Contain Standard RAG, GraphRAG, or Agentic RAG behavior.
# - Require technical source configuration from normal consumers.
#
# Architectural Position:
# - Runtime capability-resolution boundary for source interpretation.
# - Sits between KnowledgeSourceInput and source interpreters.
# - Keeps KnowledgeFoundationRuntime independent from source technology.
#
# Future Extensibility:
# - Additional source interpreters can register independently.
# - Profile and Capability Intelligence can evolve above this boundary.
# - Plugin-backed registries can implement this interface separately.
# - Selection policy can evolve without changing runtime consumers.

from __future__ import annotations

from abc import ABC, abstractmethod

from alhf.rag.runtime.contracts.knowledge_source_input import (
    KnowledgeSourceInput,
)
from alhf.rag.runtime.interfaces.knowledge_source_interpreter import (
    KnowledgeSourceInterpreter,
)


class KnowledgeSourceInterpreterRegistry(ABC):
    """
    Stable capability registry for Knowledge source interpretation.

    The runtime resolves interpretation capability through this boundary
    instead of containing source-specific selection logic.
    """

    @abstractmethod
    def register(
        self,
        interpreter: KnowledgeSourceInterpreter,
    ) -> None:
        """Register one configured source interpreter."""

        raise NotImplementedError

    @abstractmethod
    def resolve(
        self,
        source: KnowledgeSourceInput,
    ) -> KnowledgeSourceInterpreter:
        """Resolve a compatible interpreter for one source input."""

        raise NotImplementedError

    @abstractmethod
    def contains(
        self,
        source: KnowledgeSourceInput,
    ) -> bool:
        """Return whether compatible interpretation capability exists."""

        raise NotImplementedError
