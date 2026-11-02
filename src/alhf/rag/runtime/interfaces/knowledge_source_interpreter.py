# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the stable ALHF runtime boundary for interpreting minimal
# customer Knowledge source input into a governed internal source plan.
#
# Problem Solved:
# Customers must not understand acquisition adapters, source kinds,
# configuration references, provider details, or other Knowledge
# Foundation machinery merely to supply Knowledge to ALHF.
#
# Responsibilities:
# - Accept one minimal KnowledgeSourceInput.
# - Produce one governed KnowledgeSourcePlan.
# - Keep source interpretation replaceable behind a stable boundary.
# - Allow deterministic V1 and future intelligent interpretation.
# - Preserve separation between customer input and internal execution.
#
# Must Not:
# - Acquire source contents.
# - Parse or inspect acquired resource contents.
# - Execute Knowledge ingestion stages.
# - Select parsers, derivation strategies, representations, or indexes.
# - Perform retrieval, Evidence construction, or evaluation.
# - Contain Standard RAG, GraphRAG, or Agentic RAG behavior.
# - Require technical RAG configuration from normal runtime consumers.
#
# Architectural Position:
# - Stable source-interpretation boundary of the production runtime.
# - Connects customer-facing KnowledgeSourceInput to KnowledgeSourcePlan.
# - Keeps interpretation intelligence outside the runtime facade.
#
# Future Extensibility:
# - V1 can provide deterministic local-source interpretation.
# - Profiles can participate without changing this interface.
# - Capability Intelligence can evolve behind this boundary.
# - Cloud, repository, database, API, and future source interpretation
#   can coexist without changing runtime consumers.

from __future__ import annotations

from abc import ABC, abstractmethod

from alhf.rag.runtime.contracts.knowledge_source_input import (
    KnowledgeSourceInput,
)
from alhf.rag.runtime.contracts.knowledge_source_plan import (
    KnowledgeSourcePlan,
)


class KnowledgeSourceInterpreter(ABC):
    """
    Stable runtime boundary for ALHF-owned source interpretation.

    Normal consumers provide only KnowledgeSourceInput. Concrete
    implementations determine the governed internal source plan without
    exposing source technology or Knowledge Foundation configuration.
    """

    @property
    @abstractmethod
    def interpreter_ref(self) -> str:
        """Return the stable logical interpreter identifier."""

        raise NotImplementedError

    @property
    @abstractmethod
    def interpreter_version(self) -> str:
        """Return the stable interpreter behavior version."""

        raise NotImplementedError

    @abstractmethod
    def supports(
        self,
        source: KnowledgeSourceInput,
    ) -> bool:
        """
        Return whether this interpreter can safely interpret the source.

        Compatibility determination must not perform Knowledge ingestion
        or expose technical configuration requirements to the consumer.
        """

        raise NotImplementedError

    @abstractmethod
    def interpret(
        self,
        source: KnowledgeSourceInput,
    ) -> KnowledgeSourcePlan:
        """
        Interpret one customer source into a governed internal source plan.

        The resulting plan owns internal acquisition semantics while the
        original customer contract remains source-only.
        """

        raise NotImplementedError
