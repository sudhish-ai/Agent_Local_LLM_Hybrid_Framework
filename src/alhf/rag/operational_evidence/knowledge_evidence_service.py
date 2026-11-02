# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides the application-facing Operational Evidence service used by
# ALHF Knowledge Foundation operations.
#
# Responsibilities:
# - Accept Knowledge operation evidence inputs.
# - Create validated KnowledgeOperationEvidence through the factory.
# - Publish created evidence through the configured publisher.
# - Return the provider-neutral PersistenceResult.
# - Keep Knowledge stages independent from evidence construction details.
# - Keep Knowledge stages independent from persistence technology.
#
# Must Not:
# - Construct OperationalEvidenceRecord directly.
# - Persist evidence directly.
# - Perform JSON or JSONL serialization.
# - Depend on concrete persistence providers.
# - Generate execution or operation identities.
# - Perform retry, buffering, batching, or backpressure.
# - Perform failure analysis or root-cause analysis.
# - Infer causality.
# - Contain Knowledge content, prompts, embeddings, or retrieved text.
#
# Architectural Position:
# - Knowledge Foundation Operational Evidence application service.
# - Composes KnowledgeEvidenceFactory and KnowledgeEvidencePublisher.
# - Provides the boundary used by future Knowledge pipeline stages.
#
# Future Extensibility:
# - Publication policies can evolve behind the publisher boundary.
# - Evidence construction policies can evolve behind the factory.
# - Concrete persistence providers remain independently replaceable.

from __future__ import annotations

from datetime import datetime

from alhf.core.operational_evidence.contracts.execution_identity import (
    ExecutionIdentity,
)
from alhf.core.operational_evidence.contracts.measurement import (
    OperationalMeasurement,
)
from alhf.core.operational_evidence.contracts.outcome import (
    OperationalOutcome,
)
from alhf.core.operational_evidence.contracts.persistence_result import (
    PersistenceResult,
)
from alhf.core.operational_evidence.contracts.relationship import (
    OperationalRelationship,
)
from alhf.rag.operational_evidence.contracts.knowledge_event_type import (
    KnowledgeEventType,
)
from alhf.rag.operational_evidence.contracts.knowledge_evidence_context import (
    KnowledgeEvidenceContext,
)
from alhf.rag.operational_evidence.knowledge_evidence_factory import (
    KnowledgeEvidenceFactory,
)
from alhf.rag.operational_evidence.knowledge_evidence_publisher import (
    KnowledgeEvidencePublisher,
)


class KnowledgeEvidenceService:
    """
    Application-facing service for Knowledge Operational Evidence.

    Knowledge Foundation stages use this service to create and publish
    evidence without depending on universal record construction,
    serialization, or physical persistence.
    """

    def __init__(
        self,
        *,
        factory: KnowledgeEvidenceFactory,
        publisher: KnowledgeEvidencePublisher,
    ) -> None:
        if not isinstance(
            factory,
            KnowledgeEvidenceFactory,
        ):
            raise TypeError(
                "factory must be an instance of "
                "KnowledgeEvidenceFactory"
            )

        if not isinstance(
            publisher,
            KnowledgeEvidencePublisher,
        ):
            raise TypeError(
                "publisher must be an instance of "
                "KnowledgeEvidencePublisher"
            )

        self._factory = factory
        self._publisher = publisher

    def record(
        self,
        *,
        execution: ExecutionIdentity,
        event_type: KnowledgeEventType,
        context: KnowledgeEvidenceContext,
        outcome: OperationalOutcome | None = None,
        measurements: tuple[OperationalMeasurement, ...] = (),
        relationships: tuple[OperationalRelationship, ...] = (),
        observed_at: datetime | None = None,
    ) -> PersistenceResult:
        """
        Create and publish one Knowledge Operational Evidence record.

        Construction is delegated to KnowledgeEvidenceFactory.
        Persistence is delegated to KnowledgeEvidencePublisher.
        """

        evidence = self._factory.create(
            execution=execution,
            event_type=event_type,
            context=context,
            outcome=outcome,
            measurements=measurements,
            relationships=relationships,
            observed_at=observed_at,
        )

        return self._publisher.publish(
            evidence,
        )
