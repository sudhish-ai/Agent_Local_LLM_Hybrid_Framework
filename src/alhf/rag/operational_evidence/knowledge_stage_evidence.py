# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides stage-oriented Operational Evidence emission for the
# ALHF Knowledge Foundation.
#
# Responsibilities:
# - Bind a stable KnowledgeExecutionContext to evidence emission.
# - Delegate evidence creation and publication to KnowledgeEvidenceService.
# - Emit typed Knowledge Foundation events.
# - Preserve optional outcomes, measurements, and relationships.
# - Preserve optional caller-supplied observation timestamps.
# - Keep Knowledge stages independent from Operational Evidence plumbing.
#
# Must Not:
# - Create OperationalEvidenceRecord directly.
# - Persist Operational Evidence directly.
# - Perform JSON or JSONL serialization.
# - Generate execution or operation identities.
# - Modify governed Knowledge context.
# - Execute Knowledge pipeline stages.
# - Perform failure analysis or root-cause analysis.
# - Infer causality.
# - Implement retry, buffering, batching, or backpressure.
# - Contain Knowledge content, prompts, embeddings, or retrieved text.
#
# Architectural Position:
# - Knowledge Foundation stage-facing Operational Evidence component.
# - Composes KnowledgeExecutionContext with KnowledgeEvidenceService.
# - Provides a small API for future acquisition, parsing, normalization,
#   derivation, representation, indexing, retrieval, Evidence construction,
#   context construction, and evaluation stages.
#
# Future Extensibility:
# - Stage-specific measurements remain supplied through universal
#   OperationalMeasurement contracts.
# - Stage-specific relationships remain supplied through universal
#   OperationalRelationship contracts.
# - Persistence remains independently replaceable behind the service.

from __future__ import annotations

from datetime import datetime

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
from alhf.rag.operational_evidence.knowledge_evidence_service import (
    KnowledgeEvidenceService,
)
from alhf.rag.operational_evidence.knowledge_execution_context import (
    KnowledgeExecutionContext,
)


class KnowledgeStageEvidence:
    """
    Stage-facing Operational Evidence emitter for Knowledge operations.

    execution_context:
        Stable universal execution identity and governed Knowledge context
        shared by related events for the stage operation.

    service:
        Knowledge Operational Evidence application service responsible for
        creating and publishing validated evidence.

    This component contains no persistence or analytical intelligence.
    """

    def __init__(
        self,
        *,
        execution_context: KnowledgeExecutionContext,
        service: KnowledgeEvidenceService,
    ) -> None:
        if not isinstance(
            execution_context,
            KnowledgeExecutionContext,
        ):
            raise TypeError(
                "execution_context must be an instance of "
                "KnowledgeExecutionContext"
            )

        if not isinstance(
            service,
            KnowledgeEvidenceService,
        ):
            raise TypeError(
                "service must be an instance of "
                "KnowledgeEvidenceService"
            )

        self._execution_context = execution_context
        self._service = service

    @property
    def execution_context(self) -> KnowledgeExecutionContext:
        """Return the stable execution context used by this emitter."""

        return self._execution_context

    def emit(
        self,
        *,
        event_type: KnowledgeEventType,
        outcome: OperationalOutcome | None = None,
        measurements: tuple[OperationalMeasurement, ...] = (),
        relationships: tuple[OperationalRelationship, ...] = (),
        observed_at: datetime | None = None,
    ) -> PersistenceResult:
        """Create and publish one stage Operational Evidence event."""

        if not isinstance(
            event_type,
            KnowledgeEventType,
        ):
            raise TypeError(
                "event_type must be an instance of KnowledgeEventType"
            )

        return self._service.record(
            execution=self._execution_context.execution,
            event_type=event_type,
            context=self._execution_context.knowledge,
            outcome=outcome,
            measurements=measurements,
            relationships=relationships,
            observed_at=observed_at,
        )
