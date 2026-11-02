# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Validates preservation of Knowledge Foundation failure and degradation
# semantics through the complete local Operational Evidence path.
#
# Responsibilities:
# - Emit degraded Knowledge Operational Evidence.
# - Emit failed Knowledge Operational Evidence.
# - Persist failure evidence through the JSONL evidence store.
# - Recover persisted failure evidence through the JSONL repository.
# - Preserve completion and quality semantics.
# - Preserve failure cause and retry disposition.
# - Preserve operational criticality.
# - Preserve execution and correlation identities.
# - Validate failed evidence remains queryable for future RCA consumers.
#
# Must Not:
# - Perform root-cause analysis.
# - Infer causality from operational failure facts.
# - Execute corrective actions.
# - Test Knowledge content.
# - Test retention or archival behavior.
# - Test distributed persistence.

from itertools import count
from pathlib import Path

from alhf.core.operational_evidence.contracts.execution_identity import (
    ExecutionIdentity,
)
from alhf.core.operational_evidence.contracts.outcome import (
    CompletionState,
    FailureCause,
    OperationalCriticality,
    OperationalOutcome,
    QualityState,
    RetryDisposition,
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
    record_counter = count(
        start=1,
    )

    store = JsonlEvidenceStore(
        directory,
        max_file_size_bytes=65_536,
    )
    evidence_factory = KnowledgeEvidenceFactory(
        producer="knowledge-foundation",
        record_id_factory=lambda: (
            f"record-{next(record_counter):03d}"
        ),
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
        correlation_id="correlation-failure-001",
        execution_id="execution-failure-001",
        operation_id="retrieval-operation-001",
    )


def _knowledge() -> KnowledgeEvidenceContext:
    return KnowledgeEvidenceContext(
        knowledge_scope_ref="scope-001",
        logical_resource_ref="resource-001",
        revision_ref="revision-007",
        derivation_ref="derivation-003",
        affected_scope_ref="affected-scope-001",
    )


def test_degraded_knowledge_evidence_survives_round_trip(
    tmp_path: Path,
) -> None:
    runtime = _runtime(
        tmp_path,
    )
    stage_evidence = runtime.for_operation(
        execution=_execution(),
        knowledge=_knowledge(),
    )

    outcome = OperationalOutcome(
        completion=CompletionState.COMPLETE,
        quality=QualityState.DEGRADED,
        criticality=OperationalCriticality.REQUIRED,
    )

    result = stage_evidence.emit(
        event_type=KnowledgeEventType.RETRIEVAL_DEGRADED,
        outcome=outcome,
    )

    assert result.is_persisted is True

    recovered = _repository(
        tmp_path,
    ).get_by_record_id(
        result.record_id,
    )

    assert recovered is not None
    assert recovered.event_name == "RETRIEVAL_DEGRADED"
    assert recovered.outcome == outcome
    assert recovered.outcome.is_complete is True
    assert recovered.outcome.is_degraded is True


def test_failed_knowledge_evidence_survives_round_trip(
    tmp_path: Path,
) -> None:
    runtime = _runtime(
        tmp_path,
    )
    stage_evidence = runtime.for_operation(
        execution=_execution(),
        knowledge=_knowledge(),
    )

    outcome = OperationalOutcome(
        completion=CompletionState.INCOMPLETE,
        quality=QualityState.UNUSABLE,
        criticality=OperationalCriticality.REQUIRED,
        failure_cause=FailureCause.DEPENDENCY,
        retry_disposition=RetryDisposition.RETRYABLE,
    )

    result = stage_evidence.emit(
        event_type=KnowledgeEventType.RETRIEVAL_FAILED,
        outcome=outcome,
    )

    recovered = _repository(
        tmp_path,
    ).get_by_record_id(
        result.record_id,
    )

    assert recovered is not None
    assert recovered.event_name == "RETRIEVAL_FAILED"
    assert recovered.outcome == outcome
    assert recovered.outcome.has_failure is True
    assert (
        recovered.outcome.failure_cause
        == FailureCause.DEPENDENCY
    )
    assert (
        recovered.outcome.retry_disposition
        == RetryDisposition.RETRYABLE
    )


def test_unknown_failure_semantics_survive_round_trip(
    tmp_path: Path,
) -> None:
    runtime = _runtime(
        tmp_path,
    )
    stage_evidence = runtime.for_operation(
        execution=_execution(),
        knowledge=_knowledge(),
    )

    outcome = OperationalOutcome(
        completion=CompletionState.UNKNOWN,
        quality=QualityState.UNKNOWN,
        criticality=OperationalCriticality.MANDATORY,
        failure_cause=FailureCause.UNKNOWN,
        retry_disposition=RetryDisposition.UNKNOWN,
    )

    result = stage_evidence.emit(
        event_type=KnowledgeEventType.INDEXING_FAILED,
        outcome=outcome,
    )

    recovered = _repository(
        tmp_path,
    ).get_by_record_id(
        result.record_id,
    )

    assert recovered is not None
    assert recovered.outcome is not None
    assert (
        recovered.outcome.completion
        == CompletionState.UNKNOWN
    )
    assert (
        recovered.outcome.quality
        == QualityState.UNKNOWN
    )
    assert (
        recovered.outcome.failure_cause
        == FailureCause.UNKNOWN
    )
    assert (
        recovered.outcome.retry_disposition
        == RetryDisposition.UNKNOWN
    )


def test_failed_evidence_preserves_execution_identity(
    tmp_path: Path,
) -> None:
    runtime = _runtime(
        tmp_path,
    )
    execution = _execution()

    result = runtime.for_operation(
        execution=execution,
        knowledge=_knowledge(),
    ).emit(
        event_type=KnowledgeEventType.PARSING_FAILED,
        outcome=OperationalOutcome(
            completion=CompletionState.INCOMPLETE,
            quality=QualityState.UNUSABLE,
            criticality=OperationalCriticality.MANDATORY,
            failure_cause=FailureCause.PROCESSING,
            retry_disposition=RetryDisposition.UNKNOWN,
        ),
    )

    recovered = _repository(
        tmp_path,
    ).get_by_record_id(
        result.record_id,
    )

    assert recovered is not None
    assert recovered.execution == execution


def test_failed_evidence_is_queryable_by_execution(
    tmp_path: Path,
) -> None:
    runtime = _runtime(
        tmp_path,
    )

    result = runtime.for_operation(
        execution=_execution(),
        knowledge=_knowledge(),
    ).emit(
        event_type=KnowledgeEventType.REPRESENTATION_FAILED,
        outcome=OperationalOutcome(
            completion=CompletionState.PARTIAL,
            quality=QualityState.DEGRADED,
            criticality=OperationalCriticality.REQUIRED,
            failure_cause=FailureCause.DEPENDENCY,
            retry_disposition=RetryDisposition.RETRYABLE,
        ),
    )

    assert result.is_persisted is True

    records = _repository(
        tmp_path,
    ).get_by_execution_id(
        "execution-failure-001",
        limit=10,
    )

    assert len(records) == 1
    assert records[0].event_name == "REPRESENTATION_FAILED"
    assert records[0].outcome is not None
    assert records[0].outcome.has_failure is True


def test_degraded_then_failed_history_remains_visible(
    tmp_path: Path,
) -> None:
    runtime = _runtime(
        tmp_path,
    )
    stage_evidence = runtime.for_operation(
        execution=_execution(),
        knowledge=_knowledge(),
    )

    degraded = stage_evidence.emit(
        event_type=KnowledgeEventType.RETRIEVAL_DEGRADED,
        outcome=OperationalOutcome(
            completion=CompletionState.PARTIAL,
            quality=QualityState.DEGRADED,
            criticality=OperationalCriticality.REQUIRED,
        ),
    )
    failed = stage_evidence.emit(
        event_type=KnowledgeEventType.RETRIEVAL_FAILED,
        outcome=OperationalOutcome(
            completion=CompletionState.INCOMPLETE,
            quality=QualityState.UNUSABLE,
            criticality=OperationalCriticality.REQUIRED,
            failure_cause=FailureCause.DEPENDENCY,
            retry_disposition=RetryDisposition.RETRYABLE,
        ),
    )

    assert degraded.is_persisted is True
    assert failed.is_persisted is True

    records = _repository(
        tmp_path,
    ).get_by_execution_id(
        "execution-failure-001",
        limit=10,
    )

    assert tuple(
        record.event_name
        for record in records
    ) == (
        "RETRIEVAL_DEGRADED",
        "RETRIEVAL_FAILED",
    )

    assert records[0].outcome is not None
    assert records[0].outcome.is_degraded is True

    assert records[1].outcome is not None
    assert records[1].outcome.has_failure is True
