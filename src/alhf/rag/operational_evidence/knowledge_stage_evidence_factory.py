# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Creates stage-facing Operational Evidence emitters for the
# ALHF Knowledge Foundation.
#
# Responsibilities:
# - Accept a KnowledgeEvidenceService dependency.
# - Create KnowledgeExecutionContext from validated execution and
#   Knowledge evidence contracts.
# - Create KnowledgeStageEvidence bound to that execution context.
# - Keep stage integration independent from evidence plumbing.
# - Preserve caller-supplied execution and Knowledge identities.
#
# Must Not:
# - Generate execution or operation identities.
# - Generate Knowledge identities.
# - Create OperationalEvidenceRecord directly.
# - Persist Operational Evidence directly.
# - Perform JSON or JSONL serialization.
# - Execute Knowledge pipeline stages.
# - Perform failure analysis or root-cause analysis.
# - Infer causality.
# - Contain Knowledge content, prompts, embeddings, or retrieved text.
# - Contain provider-specific behavior.
#
# Architectural Position:
# - Knowledge Foundation Operational Evidence integration factory.
# - Creates KnowledgeStageEvidence instances for pipeline operations.
# - Composes existing validated Operational Evidence components.
#
# Future Extensibility:
# - Stage integration policies can evolve independently.
# - Execution-identity generation remains a separate responsibility.
# - Persistence remains replaceable behind KnowledgeEvidenceService.

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
from alhf.rag.operational_evidence.knowledge_execution_context import (
    KnowledgeExecutionContext,
)
from alhf.rag.operational_evidence.knowledge_stage_evidence import (
    KnowledgeStageEvidence,
)


class KnowledgeStageEvidenceFactory:
    """
    Creates stage-facing Knowledge Operational Evidence emitters.

    The factory binds a validated ExecutionIdentity and
    KnowledgeEvidenceContext to the configured KnowledgeEvidenceService.

    It does not create identities, evidence records, or persistence
    results itself.
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

        self._service = service

    def create(
        self,
        *,
        execution: ExecutionIdentity,
        knowledge: KnowledgeEvidenceContext,
    ) -> KnowledgeStageEvidence:
        """
        Create one stage-facing Operational Evidence emitter.

        Args:
            execution:
                Stable universal execution identity for the Knowledge
                operation.

            knowledge:
                Governed Knowledge-specific context associated with the
                operation.

        Returns:
            KnowledgeStageEvidence bound to the supplied execution and
            Knowledge context.
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

        execution_context = KnowledgeExecutionContext(
            execution=execution,
            knowledge=knowledge,
        )

        return KnowledgeStageEvidence(
            execution_context=execution_context,
            service=self._service,
        )
