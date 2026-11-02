# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the stable index-execution fan-out boundary used by the ALHF
# Knowledge Foundation production ingestion runtime.
#
# Problem Solved:
# Ingestion must not permanently assume one Knowledge representation is
# written to exactly one logical index. Runtime composition must govern
# indexing fan-out without changing ingestion orchestration.
#
# Responsibilities:
# - Accept one provider-neutral KnowledgeRepresentation.
# - Execute governed indexing for that representation.
# - Return the number of successful logical index writes.
# - Hide index topology and destination selection from ingestion.
#
# Must Not:
# - Generate or modify Knowledge representations.
# - Implement physical index-provider behavior.
# - Perform retrieval, reranking, Evidence, or Context construction.
# - Contain source-specific or file-format-specific behavior.
# - Assume dense-vector indexing or one physical index technology.
#
# Architectural Position:
# - Runtime boundary between representation and governed indexing fan-out.
# - Consumed by production ingestion orchestration.
# - Implemented by deterministic V1 and future governed index plans.
#
# Future Extensibility:
# - One representation may target multiple governed logical indexes.
# - Candidate, active, migration, graph, and hybrid indexes can evolve
#   behind this boundary without changing KnowledgeIngestionService.

from __future__ import annotations

from abc import ABC, abstractmethod

from alhf.rag.representation.contracts.knowledge_representation import (
    KnowledgeRepresentation,
)


class KnowledgeIndexExecutionPlan(ABC):
    """Stable runtime boundary for governed indexing fan-out."""

    @abstractmethod
    def execute(
        self,
        representation: KnowledgeRepresentation,
    ) -> int:
        """Index one representation and return successful write count."""

        raise NotImplementedError
