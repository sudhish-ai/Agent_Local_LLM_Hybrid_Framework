# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF KnowledgeEvidenceFactory.
#
# Responsibilities:
# - Validate Knowledge Operational Evidence construction.
# - Validate deterministic record-ID injection.
# - Validate default record-ID generation.
# - Validate Knowledge event propagation.
# - Validate Knowledge context preservation.
# - Validate execution identity preservation.
# - Validate optional outcome and measurement preservation.
# - Validate observation timestamp preservation.
# - Validate factory configuration and record-ID failures.
#
# Must Not:
# - Test Operational Evidence persistence.
# - Test JSON or JSONL behavior.
# - Test retrieval, indexing, or evaluation execution.
# - Test failure analysis or root-cause analysis.
# - Test Knowledge content.

from datetime import datetime, timezone

import pytest

from alhf.core.operational_evidence.contracts.execution_identity import (
    ExecutionIdentity,
)
from alhf.core.operational_evidence.contracts.measurement import (
    OperationalMeasurement,
)
from alhf.core.operational_evidence.contracts.outcome import (
    CompletionState,
    OperationalCriticality,
    OperationalOutcome,
    QualityState,
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
from alhf.rag.operational_evidence.knowledge_evidence_factory import (
    KnowledgeEvidenceFactory,
)


def _execution() -> ExecutionIdentity:
    return ExecutionIdentity(
        correlation_id="correlation-001",
        execution_id="execution-001",
        operation_id="operation-001",
    )


def _context() -> KnowledgeEvidenceContext:
    return KnowledgeEvidenceContext(
        knowledge_scope_ref="scope-001",
        logical_resource_ref="resource-001",
        revision_ref="revision-001",
    )


def _factory() -> KnowledgeEvidenceFactory:
    return KnowledgeEvidenceFactory(
        producer="knowledge-foundation",
        record_id_factory=lambda: "record-001",
    )


def test_create_knowledge_operation_evidence() -> None:
    evidence = _factory().create(
        execution=_execution(),
        event_type=KnowledgeEventType.RETRIEVAL_COMPLETED,
        context=_context(),
    )

    assert evidence.record_id == "record-001"
    assert evidence.execution_id == "execution-001"
    assert evidence.operation_id == "operation-001"
    assert evidence.context == _context()


def test_factory_sets_operational_event_family() -> None:
    evidence = _factory().create(
        execution=_execution(),
        event_type=KnowledgeEventType.PARSING_STARTED,
        context=_context(),
    )

    assert (
        evidence.record.record_family
        == OperationalRecordFamily.OPERATIONAL_EVENT
    )


def test_factory_preserves_knowledge_event() -> None:
    evidence = _factory().create(
        execution=_execution(),
        event_type=KnowledgeEventType.INDEXING_DEGRADED,
        context=_context(),
    )

    assert (
        evidence.event_type
        == KnowledgeEventType.INDEXING_DEGRADED
    )
    assert (
        evidence.record.event_name
        == "INDEXING_DEGRADED"
    )


def test_factory_normalizes_producer() -> None:
    factory = KnowledgeEvidenceFactory(
        producer="  knowledge-foundation  ",
        record_id_factory=lambda: "record-001",
    )

    evidence = factory.create(
        execution=_execution(),
        event_type=KnowledgeEventType.RETRIEVAL_STARTED,
        context=_context(),
    )

    assert evidence.record.producer == "knowledge-foundation"


def test_factory_preserves_supplied_timestamp() -> None:
    observed_at = datetime(
        2026,
        10,
        27,
        12,
        30,
        tzinfo=timezone.utc,
    )

    evidence = _factory().create(
        execution=_execution(),
        event_type=KnowledgeEventType.RETRIEVAL_COMPLETED,
        context=_context(),
        observed_at=observed_at,
    )

    assert evidence.record.observed_at == observed_at


def test_factory_preserves_outcome_and_measurements() -> None:
    outcome = OperationalOutcome(
        completion=CompletionState.COMPLETE,
        quality=QualityState.ACCEPTABLE,
        criticality=OperationalCriticality.REQUIRED,
    )
    measurement = OperationalMeasurement(
        measurement_id="retrieved_items",
        value=5,
        unit="count",
    )

    evidence = _factory().create(
        execution=_execution(),
        event_type=KnowledgeEventType.RETRIEVAL_COMPLETED,
        context=_context(),
        outcome=outcome,
        measurements=(measurement,),
    )

    assert evidence.record.outcome == outcome
    assert evidence.record.measurements == (measurement,)


def test_custom_schema_is_preserved() -> None:
    schema = SchemaIdentity(
        schema_id="custom-evidence-schema",
        schema_version="2.0",
    )
    factory = KnowledgeEvidenceFactory(
        producer="knowledge-foundation",
        record_id_factory=lambda: "record-001",
        schema=schema,
    )

    evidence = factory.create(
        execution=_execution(),
        event_type=KnowledgeEventType.PARSING_COMPLETED,
        context=_context(),
    )

    assert evidence.record.schema == schema


def test_default_record_id_is_non_empty_string() -> None:
    factory = KnowledgeEvidenceFactory(
        producer="knowledge-foundation",
    )

    evidence = factory.create(
        execution=_execution(),
        event_type=KnowledgeEventType.PARSING_STARTED,
        context=_context(),
    )

    assert isinstance(evidence.record_id, str)
    assert evidence.record_id


@pytest.mark.parametrize("producer", ("", "   "))
def test_factory_rejects_empty_producer(
    producer: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="producer cannot be empty",
    ):
        KnowledgeEvidenceFactory(
            producer=producer,
        )


def test_factory_rejects_invalid_schema() -> None:
    with pytest.raises(
        TypeError,
        match="schema must be an instance of SchemaIdentity",
    ):
        KnowledgeEvidenceFactory(
            producer="knowledge-foundation",
            schema="invalid-schema",
        )


def test_factory_rejects_non_callable_record_id_factory() -> None:
    with pytest.raises(
        TypeError,
        match="record_id_factory must be callable or None",
    ):
        KnowledgeEvidenceFactory(
            producer="knowledge-foundation",
            record_id_factory="not-callable",
        )


def test_record_id_factory_rejects_non_string_result() -> None:
    factory = KnowledgeEvidenceFactory(
        producer="knowledge-foundation",
        record_id_factory=lambda: 123,
    )

    with pytest.raises(
        TypeError,
        match="record_id_factory must return a string",
    ):
        factory.create(
            execution=_execution(),
            event_type=KnowledgeEventType.PARSING_STARTED,
            context=_context(),
        )


def test_record_id_factory_rejects_empty_result() -> None:
    factory = KnowledgeEvidenceFactory(
        producer="knowledge-foundation",
        record_id_factory=lambda: "   ",
    )

    with pytest.raises(
        ValueError,
        match=(
            "record_id_factory cannot return an empty identifier"
        ),
    ):
        factory.create(
            execution=_execution(),
            event_type=KnowledgeEventType.PARSING_STARTED,
            context=_context(),
        )
