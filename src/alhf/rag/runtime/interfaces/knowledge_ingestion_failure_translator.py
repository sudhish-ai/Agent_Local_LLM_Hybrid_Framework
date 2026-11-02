# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the stable failure-translation boundary used by the ALHF
# Knowledge Foundation production ingestion runtime.
#
# Problem Solved:
# Stage exceptions must not become governed ingestion failure facts
# through message matching, generic exception assumptions, or policy
# logic embedded inside production ingestion orchestration.
#
# Responsibilities:
# - Accept a failure raised while processing one acquired resource.
# - Accept the ingestion stage at which the failure was observed.
# - Accept the governed ResourceIdentity of the affected resource.
# - Translate only failures whose semantics are reliably understood.
# - Return a validated KnowledgeIngestionFailure when translation exists.
# - Explicitly represent absence of trustworthy translation.
#
# Must Not:
# - Decide whether ingestion continues, stops, retries, or escalates.
# - Execute retry, recovery, quarantine, or remediation.
# - Infer semantics from exception messages.
# - Swallow or re-raise execution failures.
# - Emit or persist Operational Evidence.
# - Perform root-cause analysis.
# - Modify exceptions, resource identity, or frozen stage contracts.
#
# Architectural Position:
# - Stable translation boundary between stage failures and governed
#   Knowledge ingestion failure facts.
# - Sits before ingestion execution-policy evaluation.
# - Keeps exception interpretation outside KnowledgeIngestionService.
#
# Future Extensibility:
# - Structured ALHF failures can be translated by future implementations.
# - Provider-specific translators can compose behind this boundary.
# - Failure classification can evolve without changing orchestration.
# - Distributed execution can reuse the same governed failure contract.

from __future__ import annotations

from abc import ABC, abstractmethod

from alhf.rag.ingestion.contracts.resource_identity import (
    ResourceIdentity,
)
from alhf.rag.runtime.contracts.knowledge_ingestion_failure import (
    KnowledgeIngestionFailure,
    KnowledgeIngestionStage,
)


class KnowledgeIngestionFailureTranslator(ABC):
    """Stable boundary for trustworthy ingestion failure translation."""

    @abstractmethod
    def translate(
        self,
        *,
        error: Exception,
        stage: KnowledgeIngestionStage,
        identity: ResourceIdentity,
    ) -> KnowledgeIngestionFailure | None:
        """
        Translate one understood stage failure into a governed failure fact.

        None means the failure cannot be translated reliably and must not
        be treated as a known operational resource failure.
        """

        raise NotImplementedError
