# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the stable execution-policy boundary used when resource-level
# failures occur during ALHF Knowledge Foundation ingestion.
#
# Problem Solved:
# Production ingestion must not embed continuation or termination policy
# inside orchestration. Failure handling decisions must remain replaceable
# as profiles, governance, and Knowledge Intelligence evolve.
#
# Responsibilities:
# - Accept one validated Knowledge ingestion failure fact.
# - Produce one governed Knowledge ingestion execution decision.
# - Keep failure evaluation separate from ingestion orchestration.
# - Provide a stable boundary for evolving execution policy.
#
# Must Not:
# - Execute Knowledge ingestion stages.
# - Continue or terminate ingestion directly.
# - Execute retry, recovery, quarantine, or remediation.
# - Emit or persist Operational Evidence.
# - Perform root-cause analysis.
# - Contain source-specific or provider-specific behavior.
# - Depend on Multi-Agent execution-governor contracts.
#
# Architectural Position:
# - Stable policy boundary between resource failure facts and ingestion
#   orchestration decisions.
# - Consumed by Knowledge ingestion execution after a resource failure.
# - Keeps deterministic and future intelligent policy implementations
#   outside the production ingestion orchestrator.
#
# Future Extensibility:
# - V1 can provide deterministic failure policy.
# - Profiles can provide governed policy implementations.
# - Knowledge Intelligence can participate behind this boundary.
# - Governance and budget-aware policy can evolve without changing
#   ingestion orchestration.

from __future__ import annotations

from abc import ABC, abstractmethod

from alhf.rag.runtime.contracts.knowledge_ingestion_decision import (
    KnowledgeIngestionDecision,
)
from alhf.rag.runtime.contracts.knowledge_ingestion_failure import (
    KnowledgeIngestionFailure,
)


class KnowledgeIngestionExecutionPolicy(ABC):
    """Stable policy boundary for resource-level ingestion failures."""

    @abstractmethod
    def decide(
        self,
        failure: KnowledgeIngestionFailure,
    ) -> KnowledgeIngestionDecision:
        """Return the execution decision for one ingestion failure."""

        raise NotImplementedError
