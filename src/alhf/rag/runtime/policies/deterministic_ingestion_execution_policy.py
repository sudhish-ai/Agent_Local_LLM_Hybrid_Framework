# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides the deterministic fail-closed ingestion execution policy used
# by the ALHF Knowledge Foundation production runtime.
#
# Problem Solved:
# Resource-processing failures require an explicit execution decision,
# but ingestion orchestration must not embed continuation policy or infer
# safe isolation from exception types, messages, stages, or retryability.
#
# Responsibilities:
# - Evaluate one validated KnowledgeIngestionFailure.
# - Produce one deterministic KnowledgeIngestionDecision.
# - Default unclassified resource failures to STOP.
# - Preserve explainable fail-closed V1 execution semantics.
# - Keep deterministic policy replaceable behind the stable interface.
#
# Must Not:
# - Execute ingestion continuation or termination.
# - Infer resource isolation from stage, exception text, or retryability.
# - Execute retry, recovery, quarantine, or remediation.
# - Emit or persist Operational Evidence.
# - Perform failure analysis or root-cause analysis.
# - Contain source-specific or provider-specific behavior.
# - Depend on Multi-Agent execution-governor contracts.
#
# Architectural Position:
# - Deterministic production implementation of ingestion execution policy.
# - Sits between resource-level failure facts and ingestion orchestration.
# - Keeps V1 decision behavior outside KnowledgeIngestionService.
#
# Future Extensibility:
# - Classified deterministic policies can implement the same interface.
# - Profile and governance policy can replace this implementation.
# - Knowledge Intelligence can participate behind the stable boundary.
# - Richer execution mechanisms can evolve without moving policy into
#   ingestion orchestration.

from __future__ import annotations

from alhf.rag.runtime.contracts.knowledge_ingestion_decision import (
    KnowledgeIngestionAction,
    KnowledgeIngestionDecision,
)
from alhf.rag.runtime.contracts.knowledge_ingestion_failure import (
    KnowledgeIngestionFailure,
)
from alhf.rag.runtime.interfaces.knowledge_ingestion_execution_policy import (
    KnowledgeIngestionExecutionPolicy,
)


class DeterministicIngestionExecutionPolicy(
    KnowledgeIngestionExecutionPolicy,
):
    """Fail-closed execution policy for unclassified ingestion failures."""

    _STOP_REASON = (
        "resource failure is not explicitly classified as safely isolatable"
    )

    def decide(
        self,
        failure: KnowledgeIngestionFailure,
    ) -> KnowledgeIngestionDecision:
        """Return a deterministic fail-closed decision."""

        if not isinstance(
            failure,
            KnowledgeIngestionFailure,
        ):
            raise TypeError(
                "failure must be an instance of KnowledgeIngestionFailure"
            )

        return KnowledgeIngestionDecision(
            action=KnowledgeIngestionAction.STOP,
            reason=self._STOP_REASON,
        )
