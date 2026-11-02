# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the stable representation-execution fan-out boundary used by
# the ALHF Knowledge Foundation production ingestion runtime.
#
# Problem Solved:
# Ingestion must not permanently assume one Knowledge Unit produces one
# retrieval representation. Runtime composition must support one or more
# governed representation executions without changing ingestion orchestration.
#
# Responsibilities:
# - Accept one provider-neutral KnowledgeUnit.
# - Yield KnowledgeRepresentation artifacts incrementally.
# - Hide representation fan-out and provider composition from ingestion.
# - Preserve bounded streaming-oriented execution semantics.
# - Provide a stable boundary for evolving representation topology.
#
# Must Not:
# - Define representation algorithms or payload formats.
# - Perform indexing, retrieval, Evidence, or Context construction.
# - Select physical indexes or retrieval strategies.
# - Contain source-specific or file-format-specific behavior.
# - Materialize representation collections as part of the interface.
# - Contain Standard RAG, GraphRAG, or Agentic RAG orchestration.
#
# Architectural Position:
# - Runtime boundary between Knowledge derivation and representation fan-out.
# - Consumed by production ingestion orchestration.
# - Implemented by deterministic V1 and future governed execution plans.
#
# Future Extensibility:
# - Lexical, dense, sparse, graph, structured, and multimodal providers can
#   participate without changing KnowledgeIngestionService.
# - Multiple representation versions and providers can coexist.
# - Representation Intelligence can evolve behind this stable boundary.

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator

from alhf.rag.chunking.contracts.knowledge_unit import KnowledgeUnit
from alhf.rag.representation.contracts.knowledge_representation import (
    KnowledgeRepresentation,
)


class KnowledgeRepresentationExecutionPlan(ABC):
    """Stable runtime boundary for representation execution fan-out."""

    @abstractmethod
    def execute(
        self,
        unit: KnowledgeUnit,
    ) -> Iterator[KnowledgeRepresentation]:
        """Yield governed representations for one Knowledge Unit."""

        raise NotImplementedError
