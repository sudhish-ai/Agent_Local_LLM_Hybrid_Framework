# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the stable source-binding boundary used by the ALHF Knowledge
# Foundation production runtime after source interpretation.
#
# Problem Solved:
# An interpreted logical source plan must become runtime-ready acquisition
# composition without exposing physical provider configuration to ingestion
# execution or requiring technical configuration from runtime consumers.
#
# Responsibilities:
# - Accept the original minimal KnowledgeSourceInput.
# - Accept its governed KnowledgeSourcePlan.
# - Produce one provider-neutral KnowledgeSourceBinding.
# - Keep physical source composition behind a stable runtime boundary.
# - Preserve separation between interpretation and ingestion execution.
#
# Must Not:
# - Execute Knowledge acquisition.
# - Parse, normalize, derive, represent, index, or retrieve Knowledge.
# - Expose concrete adapters, registries, or provider configuration.
# - Embed source-technology branching in runtime consumers.
# - Select retrieval strategies or Knowledge query behavior.
# - Contain Standard RAG, GraphRAG, or Agentic RAG behavior.
#
# Architectural Position:
# - Stable composition boundary after source interpretation.
# - Connects source input and governed plan to runtime-ready acquisition.
# - Keeps KnowledgeIngestionService independent from physical sources.
#
# Future Extensibility:
# - Local, cloud, database, API, and collaboration binders can implement
#   this boundary independently.
# - Authorization-aware binding can evolve behind this interface.
# - Profile and capability intelligence can select binding behavior.
# - Distributed acquisition composition requires no ingestion redesign.

from __future__ import annotations

from abc import ABC, abstractmethod

from alhf.rag.runtime.contracts.knowledge_source_binding import (
    KnowledgeSourceBinding,
)
from alhf.rag.runtime.contracts.knowledge_source_input import (
    KnowledgeSourceInput,
)
from alhf.rag.runtime.contracts.knowledge_source_plan import (
    KnowledgeSourcePlan,
)


class KnowledgeSourceBinder(ABC):
    """Stable composition boundary for runtime-ready source binding."""

    @abstractmethod
    def bind(
        self,
        *,
        source: KnowledgeSourceInput,
        plan: KnowledgeSourcePlan,
    ) -> KnowledgeSourceBinding:
        """Bind interpreted source input to runtime-ready acquisition."""

        raise NotImplementedError
