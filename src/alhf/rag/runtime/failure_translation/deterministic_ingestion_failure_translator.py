# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides the conservative deterministic failure translator used by the
# ALHF Knowledge Foundation production ingestion runtime.
#
# Problem Solved:
# Existing ingestion stages expose failures through general exception
# types that do not reliably establish machine-readable operational
# semantics. The runtime must not manufacture governed failure facts
# from exception types or human-readable messages.
#
# Responsibilities:
# - Validate failure-translation inputs.
# - Preserve fail-closed translation behavior for unclassified failures.
# - Decline translation when trustworthy failure semantics are unavailable.
# - Keep exception interpretation outside ingestion orchestration.
# - Implement the stable KnowledgeIngestionFailureTranslator boundary.
#
# Must Not:
# - Match or classify failures by exception message.
# - Treat generic exception types as operational classifications.
# - Manufacture error codes or retryability.
# - Decide whether ingestion continues, stops, retries, or escalates.
# - Swallow or re-raise execution failures.
# - Emit or persist Operational Evidence.
# - Modify frozen ingestion-stage implementations or contracts.
#
# Architectural Position:
# - Conservative deterministic implementation of failure translation.
# - Sits between resource-stage exceptions and ingestion execution policy.
# - Prevents unclassified exceptions from masquerading as governed facts.
#
# Future Extensibility:
# - Structured translators can replace or compose with this implementation.
# - Provider-specific translation can evolve behind the stable interface.
# - Machine-readable classification can enable governed failure facts.
# - Ingestion orchestration remains unchanged as translation evolves.

from __future__ import annotations

from alhf.rag.ingestion.contracts.resource_identity import (
    ResourceIdentity,
)
from alhf.rag.runtime.contracts.knowledge_ingestion_failure import (
    KnowledgeIngestionFailure,
    KnowledgeIngestionStage,
)
from alhf.rag.runtime.interfaces.knowledge_ingestion_failure_translator import (
    KnowledgeIngestionFailureTranslator,
)


class DeterministicIngestionFailureTranslator(
    KnowledgeIngestionFailureTranslator,
):
    """Decline translation when failure semantics are not trustworthy."""

    def translate(
        self,
        *,
        error: Exception,
        stage: KnowledgeIngestionStage,
        identity: ResourceIdentity,
    ) -> KnowledgeIngestionFailure | None:
        """Validate inputs and decline unclassified failure translation."""

        if not isinstance(
            error,
            Exception,
        ):
            raise TypeError(
                "error must be an instance of Exception"
            )

        if not isinstance(
            stage,
            KnowledgeIngestionStage,
        ):
            raise TypeError(
                "stage must be an instance of KnowledgeIngestionStage"
            )

        if not isinstance(
            identity,
            ResourceIdentity,
        ):
            raise TypeError(
                "identity must be an instance of ResourceIdentity"
            )

        return None
