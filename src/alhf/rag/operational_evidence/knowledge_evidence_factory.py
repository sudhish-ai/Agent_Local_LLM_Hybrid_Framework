# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Creates Knowledge-specific Operational Evidence while preserving the
# universal ALHF Operational Evidence record model.
#
# Responsibilities:
# - Create universal OperationalEvidenceRecord instances for Knowledge
#   Foundation operations.
# - Compose validated KnowledgeEvidenceContext with universal evidence.
# - Preserve typed KnowledgeEventType semantics.
# - Preserve optional outcomes, measurements, and relationships.
# - Generate record identities independently from execution identities.
# - Preserve caller-supplied observation timestamps when provided.
#
# Must Not:
# - Persist Operational Evidence.
# - Perform JSON or JSONL serialization.
# - Generate execution or operation identities.
# - Create or mutate governed Knowledge state.
# - Perform acquisition, parsing, retrieval, or indexing.
# - Perform failure analysis or root-cause analysis.
# - Infer causality.
# - Contain Knowledge content, prompts, embeddings, or retrieved text.
# - Contain provider-specific persistence behavior.
#
# Architectural Position:
# - Knowledge-specific Operational Evidence construction component.
# - Composes universal Operational Evidence contracts without modifying
#   universal ALHF core semantics.
# - Produces KnowledgeOperationEvidence for downstream persistence.
#
# Future Extensibility:
# - Record-ID generation can be replaced through the supplied callable.
# - Additional Knowledge-specific construction policies can evolve
#   without changing universal Operational Evidence contracts.
# - Persistence remains independently replaceable.

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Callable

from alhf.core.operational_evidence.contracts.execution_identity import (
    ExecutionIdentity,
)
from alhf.core.operational_evidence.contracts.measurement import (
    OperationalMeasurement,
)
from alhf.core.operational_evidence.contracts.outcome import (
    OperationalOutcome,
)
from alhf.core.operational_evidence.contracts.record import (
    OperationalEvidenceRecord,
)
from alhf.core.operational_evidence.contracts.record_family import (
    OperationalRecordFamily,
)
from alhf.core.operational_evidence.contracts.relationship import (
    OperationalRelationship,
)
from alhf.core.operational_evidence.contracts.schema_identity import (
    SchemaIdentity,
)
from alhf.rag.operational_evidence.contracts.knowledge_event_type import (
    KnowledgeEventType,
)
from alhf.rag.operational_evidence.contracts.knowledge_evidence_context import (
    KnowledgeEvidenceContext,
)
from alhf.rag.operational_evidence.contracts.knowledge_operation_evidence import (
    KnowledgeOperationEvidence,
)


class KnowledgeEvidenceFactory:
    """Create validated Knowledge-specific Operational Evidence."""

    DEFAULT_SCHEMA = SchemaIdentity(
        schema_id="operational-evidence-record",
        schema_version="1.0",
    )

    def __init__(
        self,
        *,
        producer: str,
        record_id_factory: Callable[[], str] | None = None,
        schema: SchemaIdentity = DEFAULT_SCHEMA,
    ) -> None:
        self._producer = self._normalize_required_text(
            value=producer,
            field_name="producer",
        )

        if not isinstance(
            schema,
            SchemaIdentity,
        ):
            raise TypeError(
                "schema must be an instance of SchemaIdentity"
            )

        if (
            record_id_factory is not None
            and not callable(record_id_factory)
        ):
            raise TypeError(
                "record_id_factory must be callable or None"
            )

        self._schema = schema
        self._record_id_factory = (
            record_id_factory
            if record_id_factory is not None
            else self._default_record_id
        )

    def create(
        self,
        *,
        execution: ExecutionIdentity,
        event_type: KnowledgeEventType,
        context: KnowledgeEvidenceContext,
        outcome: OperationalOutcome | None = None,
        measurements: tuple[OperationalMeasurement, ...] = (),
        relationships: tuple[OperationalRelationship, ...] = (),
        observed_at: datetime | None = None,
    ) -> KnowledgeOperationEvidence:
        """Create one validated Knowledge Operational Evidence object."""

        record_id = self._record_id_factory()

        if not isinstance(
            record_id,
            str,
        ):
            raise TypeError(
                "record_id_factory must return a string"
            )

        record_id = record_id.strip()

        if not record_id:
            raise ValueError(
                "record_id_factory cannot return an empty identifier"
            )

        record_arguments = {
            "record_id": record_id,
            "schema": self._schema,
            "record_family": OperationalRecordFamily.OPERATIONAL_EVENT,
            "producer": self._producer,
            "event_name": event_type.value,
            "execution": execution,
            "outcome": outcome,
            "measurements": measurements,
            "relationships": relationships,
        }

        if observed_at is not None:
            record_arguments["observed_at"] = observed_at

        record = OperationalEvidenceRecord(
            **record_arguments
        )

        return KnowledgeOperationEvidence(
            record=record,
            event_type=event_type,
            context=context,
        )

    @staticmethod
    def _default_record_id() -> str:
        """Generate a storage-independent evidence-record identity."""

        return str(
            uuid.uuid4()
        )

    @staticmethod
    def _normalize_required_text(
        *,
        value: str,
        field_name: str,
    ) -> str:
        """Validate and normalize required factory text."""

        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                f"{field_name} must be a string"
            )

        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError(
                f"{field_name} cannot be empty"
            )

        return normalized_value
