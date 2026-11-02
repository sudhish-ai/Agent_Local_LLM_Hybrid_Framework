# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Publishes Knowledge-specific Operational Evidence through the
# universal ALHF Operational Evidence persistence boundary.
#
# Responsibilities:
# - Accept validated KnowledgeOperationEvidence.
# - Persist its universal OperationalEvidenceRecord through EvidenceSink.
# - Return the provider-neutral PersistenceResult unchanged.
# - Keep Knowledge producers independent from persistence technology.
#
# Must Not:
# - Create Operational Evidence records.
# - Modify KnowledgeOperationEvidence.
# - Perform JSON or JSONL serialization.
# - Depend on a concrete persistence provider.
# - Implement retry, buffering, batching, or backpressure.
# - Perform failure analysis or root-cause analysis.
# - Infer persistence success from exceptions or side effects.
# - Contain Knowledge content, prompts, embeddings, or retrieved text.
#
# Architectural Position:
# - Knowledge-specific publishing boundary.
# - Connects Knowledge Operational Evidence to the universal EvidenceSink.
# - Keeps Knowledge producers independent from JSONL and future storage.
#
# Future Extensibility:
# - Different EvidenceSink implementations can be supplied without
#   changing Knowledge evidence producers.
# - Retry and delivery policies can be composed outside this publisher.
# - Asynchronous publication can evolve behind a separate abstraction.

from __future__ import annotations

from alhf.core.operational_evidence.contracts.persistence_result import (
    PersistenceResult,
)
from alhf.core.operational_evidence.interfaces.evidence_sink import (
    EvidenceSink,
)
from alhf.rag.operational_evidence.contracts.knowledge_operation_evidence import (
    KnowledgeOperationEvidence,
)


class KnowledgeEvidencePublisher:
    """Publish validated Knowledge Operational Evidence."""

    def __init__(
        self,
        *,
        sink: EvidenceSink,
    ) -> None:
        if not isinstance(
            sink,
            EvidenceSink,
        ):
            raise TypeError(
                "sink must be an instance of EvidenceSink"
            )

        self._sink = sink

    def publish(
        self,
        evidence: KnowledgeOperationEvidence,
    ) -> PersistenceResult:
        """
        Persist one Knowledge Operational Evidence record.

        The provider-neutral PersistenceResult produced by the configured
        EvidenceSink is returned unchanged.
        """

        if not isinstance(
            evidence,
            KnowledgeOperationEvidence,
        ):
            raise TypeError(
                "evidence must be an instance of "
                "KnowledgeOperationEvidence"
            )

        result = self._sink.persist(
            evidence.record,
        )

        if not isinstance(
            result,
            PersistenceResult,
        ):
            raise TypeError(
                "EvidenceSink.persist must return PersistenceResult"
            )

        if result.record_id != evidence.record_id:
            raise ValueError(
                "persistence result record_id must match evidence record_id"
            )

        return result
