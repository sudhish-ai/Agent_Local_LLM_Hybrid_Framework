# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Validates the end-to-end Knowledge Operational Evidence path through
# the local ALHF JSONL persistence and repository implementation.
#
# Responsibilities:
# - Create stage-facing Knowledge Operational Evidence.
# - Persist evidence through the Knowledge evidence runtime path.
# - Retrieve persisted universal evidence through the JSONL repository.
# - Validate execution identity preservation.
# - Validate Knowledge event preservation.
# - Validate outcome and measurement preservation.
# - Validate execution and correlation queries.
#
# Must Not:
# - Execute Knowledge pipeline stages.
# - Perform failure analysis or root-cause analysis.
# - Test Knowledge content.
# - Test retention or archival behavior.
# - Test distributed persistence.

from pathlib import Path

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
from alhf.core.operational_evidence.providers.jsonl_evidence_repository import (
    JsonlEvidenceRepository,
)
from alhf.core.operational_evidence.providers.jsonl_evidence_store import (
    JsonlEvidenceStore,
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
from alhf.rag.operational_evidence.knowledge_evidence_runtime import (
    KnowledgeEvidenceRuntime,
)
from alhf.rag.operational_evidence.knowledge_evidence_service import (
    KnowledgeEvidenceService,
)


def _runtime(
    directory: Path,
) -> KnowledgeEvidenceRuntime:
    store = JsonlEvidenceStore(
        directory,
        max_file_size_bytes=65_536,
    )
    evidence_factory = KnowledgeEvidenceFactory(
        producer="knowledge-foundation",
        record_id_factory=lambda: "record-001",
    )
    publisher = KnowledgeEvidencePublisher(
        sink=store,
    )
    service = KnowledgeEvidenceService(
        factory=evidence_factory,
        publisher=publisher,
    )

    return KnowledgeEvidenceRuntime(
        service=service,
    )


def _repository(
    directory: Path,
) -> JsonlEvidenceRepository:
    return JsonlEvidenceRepository(
        directory,
        max_line_bytes=65_536,
        max_scan_entries=100,
    )


def _execution() -> ExecutionIdentity:
    return ExecutionIdentity(
        correlation_id="correlation-001",
        execution_id="execution-001",
        operation_id="operation-001",
    )


def _knowledge() -> KnowledgeEvidenceContext:
    return KnowledgeEvidenceContext(
        knowledge_scope_ref="scope-001",
        logical_resource_ref="resource-001",
        revision_ref="revision-001",
        derivation_ref="derivation-001",
    )


def test_knowledge_evidence_round_trip(
    tmp_path: Path,
) -> None:
    stage_evidence = _runtime(
        tmp_path,
    ).for_operation(
        execution=_execution(),
        knowledge=_knowledge(),
    )

    result = stage_evidence.emit(
        event_type=KnowledgeEventType.RETRIEVAL_COMPLETED,
    )

    assert result.is_persisted is True

    recovered = _repository(
        tmp_path,
    ).get_by_record_id(
        "record-001",
    )

    assert recovered is not None
    assert recovered.record_id == "record-001"
    assert recovered.event_name == "RETRIEVAL_COMPLETED"


def test_round_trip_preserves_execution_identity(
    tmp_path: Path,
) -> None:
    stage_evidence = _runtime(
        tmp_path,
    ).for_operation(
        execution=_execution(),
        knowledge=_knowledge(),
    )

    stage_evidence.emit(
        event_type=KnowledgeEventType.PARSING_COMPLETED,
    )

    recovered = _repository(
        tmp_path,
    ).get_by_record_id(
        "record-001",
    )

    assert recovered is not None
    assert recovered.execution == _execution()


def test_round_trip_preserves_outcome(
    tmp_path: Path,
) -> None:
    outcome = OperationalOutcome(
        completion=CompletionState.PARTIAL,
        quality=QualityState.DEGRADED,
        criticality=OperationalCriticality.REQUIRED,
    )

    stage_evidence = _runtime(
        tmp_path,
    ).for_operation(
        execution=_execution(),
        knowledge=_knowledge(),
    )

    stage_evidence.emit(
        event_type=KnowledgeEventType.RETRIEVAL_DEGRADED,
        outcome=outcome,
    )

    recovered = _repository(
        tmp_path,
    ).get_by_record_id(
        "record-001",
    )

    assert recovered is not None
    assert recovered.outcome == outcome


def test_round_trip_preserves_measurements(
    tmp_path: Path,
) -> None:
    measurement = OperationalMeasurement(
        measurement_id="retrieved_items",
        value=5,
        unit="count",
    )

    stage_evidence = _runtime(
        tmp_path,
    ).for_operation(
        execution=_execution(),
        knowledge=_knowledge(),
    )

    stage_evidence.emit(
        event_type=KnowledgeEventType.RETRIEVAL_COMPLETED,
        measurements=(measurement,),
    )

    recovered = _repository(
        tmp_path,
    ).get_by_record_id(
        "record-001",
    )

    assert recovered is not None
    assert recovered.measurements == (measurement,)


def test_execution_query_finds_knowledge_evidence(
    tmp_path: Path,
) -> None:
    stage_evidence = _runtime(
        tmp_path,
    ).for_operation(
        execution=_execution(),
        knowledge=_knowledge(),
    )

    stage_evidence.emit(
        event_type=KnowledgeEventType.INDEXING_COMPLETED,
    )

    recovered = _repository(
        tmp_path,
    ).get_by_execution_id(
        "execution-001",
        limit=10,
    )

    assert len(recovered) == 1
    assert recovered[0].record_id == "record-001"
    assert recovered[0].event_name == "INDEXING_COMPLETED"


def test_correlation_query_finds_knowledge_evidence(
    tmp_path: Path,
) -> None:
    stage_evidence = _runtime(
        tmp_path,
    ).for_operation(
        execution=_execution(),
        knowledge=_knowledge(),
    )

    stage_evidence.emit(
        event_type=KnowledgeEventType.PARSING_COMPLETED,
    )

    recovered = _repository(
        tmp_path,
    ).get_by_correlation_id(
        "correlation-001",
        limit=10,
    )

    assert len(recovered) == 1
    assert (
        recovered[0].execution.correlation_id
        == "correlation-001"
    )


def test_sequential_stage_events_are_persisted_and_queryable(
    tmp_path: Path,
) -> None:
    counter = iter(
        (
            "record-001",
            "record-002",
        )
    )

    store = JsonlEvidenceStore(
        tmp_path,
        max_file_size_bytes=65_536,
    )
    evidence_factory = KnowledgeEvidenceFactory(
        producer="knowledge-foundation",
        record_id_factory=lambda: next(counter),
    )
    publisher = KnowledgeEvidencePublisher(
        sink=store,
    )
    service = KnowledgeEvidenceService(
        factory=evidence_factory,
        publisher=publisher,
    )
    runtime = KnowledgeEvidenceRuntime(
        service=service,
    )

    stage_evidence = runtime.for_operation(
        execution=_execution(),
        knowledge=_knowledge(),
    )

    started = stage_evidence.emit(
        event_type=KnowledgeEventType.RETRIEVAL_STARTED,
    )
    completed = stage_evidence.emit(
        event_type=KnowledgeEventType.RETRIEVAL_COMPLETED,
    )

    assert started.is_persisted is True
    assert completed.is_persisted is True

    recovered = _repository(
        tmp_path,
    ).get_by_execution_id(
        "execution-001",
        limit=10,
    )

    assert tuple(
        record.record_id
        for record in recovered
    ) == (
        "record-001",
        "record-002",
    )

    assert tuple(
        record.event_name
        for record in recovered
    ) == (
        "RETRIEVAL_STARTED",
        "RETRIEVAL_COMPLETED",
    )
