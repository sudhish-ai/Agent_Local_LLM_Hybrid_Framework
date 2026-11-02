# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF KnowledgeOperationEvidence contract.
#
# Responsibilities:
# - Validate composition of universal and Knowledge-specific evidence.
# - Validate Knowledge event typing.
# - Validate Knowledge context composition.
# - Validate universal record-family constraints.
# - Validate Knowledge event-name alignment.
# - Validate execution identity convenience accessors.
# - Validate invalid composed-contract rejection.
# - Validate immutability.
#
# Must Not:
# - Test Operational Evidence persistence.
# - Test JSON or JSONL behavior.
# - Test retrieval, indexing, or evaluation execution.
# - Test failure analysis or root-cause analysis.
# - Test Knowledge content.
# - Test identity generation.

from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from alhf.core.operational_evidence.contracts.execution_identity import (
    ExecutionIdentity,
)
from alhf.core.operational_evidence.contracts.record import (
    OperationalEvidenceRecord,
)
from alhf.core.operational_evidence.contracts.record_family import (
    OperationalRecordFamily,
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


def _record(
    *,
    event_name: str = "RETRIEVAL_COMPLETED",
    record_family: OperationalRecordFamily = (
        OperationalRecordFamily.OPERATIONAL_EVENT
    ),
) -> OperationalEvidenceRecord:
    return OperationalEvidenceRecord(
        record_id="record-001",
        schema=SchemaIdentity(
            schema_id="operational-evidence-record",
            schema_version="1.0",
        ),
        record_family=record_family,
        producer="knowledge-foundation",
        event_name=event_name,
        execution=ExecutionIdentity(
            correlation_id="correlation-001",
            execution_id="execution-001",
            operation_id="operation-001",
        ),
        observed_at=datetime(
            2026,
            10,
            27,
            12,
            30,
            tzinfo=timezone.utc,
        ),
    )


def _context() -> KnowledgeEvidenceContext:
    return KnowledgeEvidenceContext(
        knowledge_scope_ref="scope-001",
        logical_resource_ref="resource-001",
        revision_ref="revision-001",
        derivation_ref="derivation-001",
    )


def test_create_knowledge_operation_evidence() -> None:
    record = _record()
    context = _context()

    evidence = KnowledgeOperationEvidence(
        record=record,
        event_type=KnowledgeEventType.RETRIEVAL_COMPLETED,
        context=context,
    )

    assert evidence.record is record
    assert (
        evidence.event_type
        == KnowledgeEventType.RETRIEVAL_COMPLETED
    )
    assert evidence.context is context


def test_record_id_returns_universal_record_identity() -> None:
    evidence = KnowledgeOperationEvidence(
        record=_record(),
        event_type=KnowledgeEventType.RETRIEVAL_COMPLETED,
        context=_context(),
    )

    assert evidence.record_id == "record-001"


def test_execution_id_returns_universal_execution_identity() -> None:
    evidence = KnowledgeOperationEvidence(
        record=_record(),
        event_type=KnowledgeEventType.RETRIEVAL_COMPLETED,
        context=_context(),
    )

    assert evidence.execution_id == "execution-001"


def test_operation_id_returns_universal_operation_identity() -> None:
    evidence = KnowledgeOperationEvidence(
        record=_record(),
        event_type=KnowledgeEventType.RETRIEVAL_COMPLETED,
        context=_context(),
    )

    assert evidence.operation_id == "operation-001"


@pytest.mark.parametrize(
    "event_type",
    tuple(KnowledgeEventType),
)
def test_all_knowledge_events_can_be_composed(
    event_type: KnowledgeEventType,
) -> None:
    evidence = KnowledgeOperationEvidence(
        record=_record(
            event_name=event_type.value,
        ),
        event_type=event_type,
        context=_context(),
    )

    assert evidence.event_type == event_type
    assert evidence.record.event_name == event_type.value


def test_record_rejects_invalid_contract() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "record must be an instance of "
            "OperationalEvidenceRecord"
        ),
    ):
        KnowledgeOperationEvidence(
            record="invalid-record",
            event_type=KnowledgeEventType.RETRIEVAL_COMPLETED,
            context=_context(),
        )


def test_event_type_rejects_invalid_contract() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "event_type must be an instance of "
            "KnowledgeEventType"
        ),
    ):
        KnowledgeOperationEvidence(
            record=_record(),
            event_type="RETRIEVAL_COMPLETED",
            context=_context(),
        )


def test_context_rejects_invalid_contract() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "context must be an instance of "
            "KnowledgeEvidenceContext"
        ),
    ):
        KnowledgeOperationEvidence(
            record=_record(),
            event_type=KnowledgeEventType.RETRIEVAL_COMPLETED,
            context="invalid-context",
        )


def test_requires_operational_event_record_family() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "Knowledge operation evidence requires "
            "OPERATIONAL_EVENT record family"
        ),
    ):
        KnowledgeOperationEvidence(
            record=_record(
                record_family=OperationalRecordFamily.MEASUREMENT,
            ),
            event_type=KnowledgeEventType.RETRIEVAL_COMPLETED,
            context=_context(),
        )


def test_record_event_name_must_match_knowledge_event() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "record event_name must match Knowledge event_type"
        ),
    ):
        KnowledgeOperationEvidence(
            record=_record(
                event_name="PARSING_COMPLETED",
            ),
            event_type=KnowledgeEventType.RETRIEVAL_COMPLETED,
            context=_context(),
        )


def test_knowledge_operation_evidence_is_immutable() -> None:
    evidence = KnowledgeOperationEvidence(
        record=_record(),
        event_type=KnowledgeEventType.RETRIEVAL_COMPLETED,
        context=_context(),
    )

    with pytest.raises(FrozenInstanceError):
        evidence.context = KnowledgeEvidenceContext(
            knowledge_scope_ref="scope-002",
        )
