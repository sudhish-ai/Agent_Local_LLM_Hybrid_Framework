# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the Knowledge-specific Operational Evidence contract used by
# the ALHF Knowledge Foundation.
#
# Responsibilities:
# - Associate one universal Operational Evidence record with governed
#   Knowledge-specific context.
# - Preserve the typed Knowledge event associated with the record.
# - Validate alignment between the typed Knowledge event and the
#   universal record event name.
# - Preserve the universal Operational Evidence record unchanged.
# - Keep Knowledge-specific semantics outside ALHF universal core.
#
# Must Not:
# - Duplicate universal Operational Evidence fields.
# - Modify OperationalEvidenceRecord.
# - Duplicate Knowledge content.
# - Generate record, execution, or Knowledge identities.
# - Perform persistence or serialization.
# - Perform failure analysis or root-cause analysis.
# - Infer causality.
# - Execute retrieval, indexing, or evaluation.
# - Contain provider-specific behavior.
# - Contain arbitrary metadata or payload dictionaries.
#
# Architectural Position:
# - Knowledge-specific composition contract.
# - Wraps universal Operational Evidence with Knowledge context.
# - Keeps Standard RAG, GraphRAG, and Agentic RAG operational facts
#   compatible with the shared Operational Evidence Foundation.
#
# Future Extensibility:
# - Additional Knowledge-specific context can evolve outside universal
#   Operational Evidence.
# - Analytical findings and recommendations remain separate record
#   families.
# - GraphRAG and Agentic RAG can introduce additional governed extensions
#   without changing this universal-to-Knowledge composition boundary.

from __future__ import annotations

from dataclasses import dataclass

from alhf.core.operational_evidence.contracts.record import (
    OperationalEvidenceRecord,
)
from alhf.core.operational_evidence.contracts.record_family import (
    OperationalRecordFamily,
)
from alhf.rag.operational_evidence.contracts.knowledge_event_type import (
    KnowledgeEventType,
)
from alhf.rag.operational_evidence.contracts.knowledge_evidence_context import (
    KnowledgeEvidenceContext,
)


@dataclass(frozen=True, slots=True)
class KnowledgeOperationEvidence:
    """
    Immutable Knowledge-specific Operational Evidence composition.

    record:
        Universal Operational Evidence record containing execution,
        outcome, measurement, relationship, and observation semantics.

    event_type:
        Typed Knowledge Foundation event represented by the universal
        record event name.

    context:
        Governed Knowledge-specific references associated with the
        observed operation.

    The universal record remains authoritative for universal semantics.
    This contract adds only Knowledge-specific meaning.
    """

    record: OperationalEvidenceRecord
    event_type: KnowledgeEventType
    context: KnowledgeEvidenceContext

    def __post_init__(self) -> None:
        self._validate_contract(
            value=self.record,
            expected_type=OperationalEvidenceRecord,
            field_name="record",
        )
        self._validate_contract(
            value=self.event_type,
            expected_type=KnowledgeEventType,
            field_name="event_type",
        )
        self._validate_contract(
            value=self.context,
            expected_type=KnowledgeEvidenceContext,
            field_name="context",
        )

        if (
            self.record.record_family
            != OperationalRecordFamily.OPERATIONAL_EVENT
        ):
            raise ValueError(
                "Knowledge operation evidence requires "
                "OPERATIONAL_EVENT record family"
            )

        if self.record.event_name != self.event_type.value:
            raise ValueError(
                "record event_name must match Knowledge event_type"
            )

    @property
    def record_id(self) -> str:
        """Return the universal Operational Evidence record identity."""

        return self.record.record_id

    @property
    def execution_id(self) -> str:
        """Return the associated execution identity."""

        return self.record.execution.execution_id

    @property
    def operation_id(self) -> str:
        """Return the associated operation identity."""

        return self.record.execution.operation_id

    @staticmethod
    def _validate_contract(
        *,
        value: object,
        expected_type: type,
        field_name: str,
    ) -> None:
        """Validate one required composed contract."""

        if not isinstance(
            value,
            expected_type,
        ):
            raise TypeError(
                f"{field_name} must be an instance of "
                f"{expected_type.__name__}"
            )
