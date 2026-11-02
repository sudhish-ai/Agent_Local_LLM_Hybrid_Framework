# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides the runtime composition boundary for ALHF Knowledge
# Operational Evidence.
#
# Responsibilities:
# - Compose Knowledge Operational Evidence construction and publication.
# - Create stage-facing evidence emitters for Knowledge operations.
# - Accept universal execution identity from Knowledge runtime callers.
# - Accept governed Knowledge evidence context from callers.
# - Keep stage consumers independent from persistence-provider details.
# - Provide one reusable Operational Evidence entry point.
#
# Must Not:
# - Generate execution or operation identities.
# - Generate governed Knowledge identities.
# - Execute Knowledge pipeline stages.
# - Create OperationalEvidenceRecord directly.
# - Perform JSON or JSONL serialization.
# - Perform failure analysis or root-cause analysis.
# - Infer causality.
# - Implement retry, buffering, batching, or backpressure.
# - Contain Knowledge content, prompts, embeddings, or retrieved text.
#
# Architectural Position:
# - Knowledge Operational Evidence runtime-composition component.
# - Composes KnowledgeEvidenceService and KnowledgeStageEvidenceFactory.
# - Provides the integration boundary used by Knowledge pipeline stages.
#
# Future Extensibility:
# - Evidence persistence remains independently replaceable.
# - Stage-specific Operational Evidence evolves through existing contracts.
# - Additional Knowledge execution modes can reuse this runtime boundary.

from __future__ import annotations

from alhf.core.operational_evidence.contracts.execution_identity import (
    ExecutionIdentity,
)
from alhf.rag.operational_evidence.contracts.knowledge_evidence_context import (
    KnowledgeEvidenceContext,
)
from alhf.rag.operational_evidence.knowledge_evidence_service import (
    KnowledgeEvidenceService,
)
from alhf.rag.operational_evidence.knowledge_stage_evidence import (
    KnowledgeStageEvidence,
)
from alhf.rag.operational_evidence.knowledge_stage_evidence_factory import (
    KnowledgeStageEvidenceFactory,
)


class KnowledgeEvidenceRuntime:
    """
    Runtime entry point for Knowledge Operational Evidence.

    Knowledge pipeline callers provide existing execution identity and
    governed Knowledge context. The runtime returns a stage-facing
    KnowledgeStageEvidence emitter bound to those identities.

    Evidence creation, publication, serialization, and persistence remain
    delegated to their existing components.
    """

    def __init__(
        self,
        *,
        service: KnowledgeEvidenceService,
    ) -> None:
        if not isinstance(
            service,
            KnowledgeEvidenceService,
        ):
            raise TypeError(
                "service must be an instance of "
                "KnowledgeEvidenceService"
            )

        self._stage_factory = KnowledgeStageEvidenceFactory(
            service=service,
        )

    def for_operation(
        self,
        *,
        execution: ExecutionIdentity,
        knowledge: KnowledgeEvidenceContext,
    ) -> KnowledgeStageEvidence:
        """
        Create a stage-facing evidence emitter for one Knowledge operation.
        """

        if not isinstance(
            execution,
            ExecutionIdentity,
        ):
            raise TypeError(
                "execution must be an instance of ExecutionIdentity"
            )

        if not isinstance(
            knowledge,
            KnowledgeEvidenceContext,
        ):
            raise TypeError(
                "knowledge must be an instance of "
                "KnowledgeEvidenceContext"
            )

        return self._stage_factory.create(
            execution=execution,
            knowledge=knowledge,
        )
