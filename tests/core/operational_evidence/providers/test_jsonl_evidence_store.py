# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the local ALHF JsonlEvidenceStore provider.
#
# Responsibilities:
# - Validate Operational Evidence persistence to JSONL.
# - Validate deterministic serialized record persistence.
# - Validate JSONL partition naming.
# - Validate partition-size enforcement.
# - Validate partition rotation.
# - Validate existing-partition discovery.
# - Validate oversized-record rejection.
# - Validate serialization-failure handling.
# - Validate filesystem-failure handling.
# - Validate optional fsync behavior.
# - Validate provider configuration validation.
#
# Must Not:
# - Test Operational Evidence query behavior.
# - Test retention or archival behavior.
# - Test multi-process coordination.
# - Test distributed persistence.
# - Test RAG or Knowledge-specific behavior.
# - Test failure analysis or root-cause analysis.

from datetime import datetime, timezone
from pathlib import Path

import pytest

from alhf.core.operational_evidence.contracts.execution_identity import (
    ExecutionIdentity,
)
from alhf.core.operational_evidence.contracts.persistence_result import (
    PersistenceStatus,
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
from alhf.core.operational_evidence.providers.jsonl_evidence_store import (
    JsonlEvidenceStore,
)
from alhf.core.operational_evidence.serializers.json_evidence_serializer import (
    JsonEvidenceSerializer,
)


def _record(
    *,
    record_id: str = "record-001",
    operation_id: str = "operation-001",
) -> OperationalEvidenceRecord:
    return OperationalEvidenceRecord(
        record_id=record_id,
        schema=SchemaIdentity(
            schema_id="operational-evidence-record",
            schema_version="1.0",
        ),
        record_family=OperationalRecordFamily.OPERATIONAL_EVENT,
        producer="test-component",
        event_name="OPERATION_COMPLETED",
        execution=ExecutionIdentity(
            correlation_id="correlation-001",
            execution_id="execution-001",
            operation_id=operation_id,
        ),
        observed_at=datetime(
            2026,
            10,
            28,
            10,
            0,
            tzinfo=timezone.utc,
        ),
    )


def _serialized_size(
    record: OperationalEvidenceRecord,
) -> int:
    return len(
        (
            JsonEvidenceSerializer.to_json(record)
            + "\n"
        ).encode("utf-8")
    )


def test_persist_creates_jsonl_partition(
    tmp_path: Path,
) -> None:
    store = JsonlEvidenceStore(
        directory=tmp_path,
        max_file_size_bytes=10_000,
    )

    result = store.persist(
        _record(),
    )

    partition = (
        tmp_path
        / "operational_evidence-000001.jsonl"
    )

    assert result.status == PersistenceStatus.PERSISTED
    assert partition.exists()


def test_persist_returns_record_identity(
    tmp_path: Path,
) -> None:
    store = JsonlEvidenceStore(
        directory=tmp_path,
        max_file_size_bytes=10_000,
    )

    result = store.persist(
        _record(
            record_id="record-017",
        ),
    )

    assert result.record_id == "record-017"
    assert result.is_persisted is True


def test_persist_writes_one_newline_terminated_json_record(
    tmp_path: Path,
) -> None:
    record = _record()
    store = JsonlEvidenceStore(
        directory=tmp_path,
        max_file_size_bytes=10_000,
    )

    store.persist(record)

    partition = (
        tmp_path
        / "operational_evidence-000001.jsonl"
    )
    persisted_bytes = partition.read_bytes()
    expected_bytes = (
        JsonEvidenceSerializer.to_json(record)
        + "\n"
    ).encode("utf-8")

    assert persisted_bytes == expected_bytes


def test_multiple_records_append_to_same_partition_when_space_exists(
    tmp_path: Path,
) -> None:
    first_record = _record(
        record_id="record-001",
        operation_id="operation-001",
    )
    second_record = _record(
        record_id="record-002",
        operation_id="operation-002",
    )

    store = JsonlEvidenceStore(
        directory=tmp_path,
        max_file_size_bytes=10_000,
    )

    first_result = store.persist(first_record)
    second_result = store.persist(second_record)

    partitions = sorted(
        tmp_path.glob(
            "operational_evidence-*.jsonl"
        )
    )

    assert first_result.is_persisted is True
    assert second_result.is_persisted is True
    assert len(partitions) == 1

    expected_bytes = (
        (
            JsonEvidenceSerializer.to_json(first_record)
            + "\n"
            + JsonEvidenceSerializer.to_json(second_record)
            + "\n"
        ).encode("utf-8")
    )

    assert partitions[0].read_bytes() == expected_bytes


def test_store_rotates_before_partition_limit_is_exceeded(
    tmp_path: Path,
) -> None:
    first_record = _record(
        record_id="record-001",
        operation_id="operation-001",
    )
    second_record = _record(
        record_id="record-002",
        operation_id="operation-002",
    )

    max_file_size = _serialized_size(
        first_record,
    )

    store = JsonlEvidenceStore(
        directory=tmp_path,
        max_file_size_bytes=max_file_size,
    )

    first_result = store.persist(first_record)
    second_result = store.persist(second_record)

    first_partition = (
        tmp_path
        / "operational_evidence-000001.jsonl"
    )
    second_partition = (
        tmp_path
        / "operational_evidence-000002.jsonl"
    )

    assert first_result.is_persisted is True
    assert second_result.is_persisted is True
    assert first_partition.exists()
    assert second_partition.exists()

    assert first_partition.read_bytes() == (
        JsonEvidenceSerializer.to_json(first_record)
        + "\n"
    ).encode("utf-8")

    assert second_partition.read_bytes() == (
        JsonEvidenceSerializer.to_json(second_record)
        + "\n"
    ).encode("utf-8")


def test_record_equal_to_partition_limit_is_persisted(
    tmp_path: Path,
) -> None:
    record = _record()
    max_file_size = _serialized_size(record)

    store = JsonlEvidenceStore(
        directory=tmp_path,
        max_file_size_bytes=max_file_size,
    )

    result = store.persist(record)

    partition = (
        tmp_path
        / "operational_evidence-000001.jsonl"
    )

    assert result.is_persisted is True
    assert partition.stat().st_size == max_file_size


def test_oversized_record_is_rejected_without_creating_partition(
    tmp_path: Path,
) -> None:
    record = _record()

    store = JsonlEvidenceStore(
        directory=tmp_path,
        max_file_size_bytes=1,
    )

    result = store.persist(record)

    assert result.status == PersistenceStatus.REJECTED
    assert (
        result.failure_code
        == "RECORD_EXCEEDS_PARTITION_LIMIT"
    )
    assert result.is_persisted is False
    assert list(
        tmp_path.glob("*.jsonl")
    ) == []


def test_custom_file_prefix_is_used(
    tmp_path: Path,
) -> None:
    store = JsonlEvidenceStore(
        directory=tmp_path,
        max_file_size_bytes=10_000,
        file_prefix="custom_evidence",
    )

    result = store.persist(
        _record(),
    )

    partition = (
        tmp_path
        / "custom_evidence-000001.jsonl"
    )

    assert result.is_persisted is True
    assert partition.exists()


def test_file_prefix_is_whitespace_normalized(
    tmp_path: Path,
) -> None:
    store = JsonlEvidenceStore(
        directory=tmp_path,
        max_file_size_bytes=10_000,
        file_prefix="  custom_evidence  ",
    )

    store.persist(
        _record(),
    )

    assert (
        tmp_path
        / "custom_evidence-000001.jsonl"
    ).exists()


def test_store_discovers_latest_existing_partition(
    tmp_path: Path,
) -> None:
    existing_partition = (
        tmp_path
        / "operational_evidence-000003.jsonl"
    )
    existing_partition.write_text(
        "",
        encoding="utf-8",
    )

    store = JsonlEvidenceStore(
        directory=tmp_path,
        max_file_size_bytes=10_000,
    )

    result = store.persist(
        _record(),
    )

    assert result.is_persisted is True
    assert existing_partition.stat().st_size > 0

    assert not (
        tmp_path
        / "operational_evidence-000001.jsonl"
    ).exists()


def test_store_ignores_invalid_partition_filenames(
    tmp_path: Path,
) -> None:
    (
        tmp_path
        / "operational_evidence-invalid.jsonl"
    ).write_text(
        "",
        encoding="utf-8",
    )
    (
        tmp_path
        / "operational_evidence-000000.jsonl"
    ).write_text(
        "",
        encoding="utf-8",
    )

    store = JsonlEvidenceStore(
        directory=tmp_path,
        max_file_size_bytes=10_000,
    )

    result = store.persist(
        _record(),
    )

    expected_partition = (
        tmp_path
        / "operational_evidence-000001.jsonl"
    )

    assert result.is_persisted is True
    assert expected_partition.exists()


def test_store_creates_missing_directory(
    tmp_path: Path,
) -> None:
    directory = (
        tmp_path
        / "nested"
        / "operational_evidence"
    )

    store = JsonlEvidenceStore(
        directory=directory,
        max_file_size_bytes=10_000,
    )

    result = store.persist(
        _record(),
    )

    assert result.is_persisted is True
    assert directory.exists()


def test_persist_rejects_non_record_value(
    tmp_path: Path,
) -> None:
    store = JsonlEvidenceStore(
        directory=tmp_path,
        max_file_size_bytes=10_000,
    )

    with pytest.raises(
        TypeError,
        match=(
            "record must be an instance of "
            "OperationalEvidenceRecord"
        ),
    ):
        store.persist(
            "invalid-record"
        )


def test_serialization_failure_returns_rejected_result(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store = JsonlEvidenceStore(
        directory=tmp_path,
        max_file_size_bytes=10_000,
    )
    record = _record()

    def reject_serialization(
        cls: type[JsonEvidenceSerializer],
        record_to_serialize: OperationalEvidenceRecord,
    ) -> str:
        raise TypeError(
            "serialization rejected"
        )

    monkeypatch.setattr(
        JsonEvidenceSerializer,
        "to_json",
        classmethod(reject_serialization),
    )

    result = store.persist(record)

    assert result.status == PersistenceStatus.REJECTED
    assert result.failure_code == "SERIALIZATION_REJECTED"
    assert result.is_persisted is False


def test_io_failure_returns_failed_result(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store = JsonlEvidenceStore(
        directory=tmp_path,
        max_file_size_bytes=10_000,
    )

    def fail_open(
        self: Path,
        *args: object,
        **kwargs: object,
    ) -> object:
        raise OSError(
            "simulated persistence failure"
        )

    monkeypatch.setattr(
        Path,
        "open",
        fail_open,
    )

    result = store.persist(
        _record(),
    )

    assert result.status == PersistenceStatus.FAILED
    assert result.failure_code == "PERSISTENCE_IO_FAILURE"
    assert result.is_persisted is False


def test_flush_to_disk_invokes_fsync(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fsync_calls: list[int] = []

    def capture_fsync(
        file_descriptor: int,
    ) -> None:
        fsync_calls.append(
            file_descriptor,
        )

    monkeypatch.setattr(
        "alhf.core.operational_evidence.providers."
        "jsonl_evidence_store.os.fsync",
        capture_fsync,
    )

    store = JsonlEvidenceStore(
        directory=tmp_path,
        max_file_size_bytes=10_000,
        flush_to_disk=True,
    )

    result = store.persist(
        _record(),
    )

    assert result.is_persisted is True
    assert len(fsync_calls) == 1


def test_default_flush_policy_does_not_invoke_fsync(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fsync_calls: list[int] = []

    def capture_fsync(
        file_descriptor: int,
    ) -> None:
        fsync_calls.append(
            file_descriptor,
        )

    monkeypatch.setattr(
        "alhf.core.operational_evidence.providers."
        "jsonl_evidence_store.os.fsync",
        capture_fsync,
    )

    store = JsonlEvidenceStore(
        directory=tmp_path,
        max_file_size_bytes=10_000,
    )

    result = store.persist(
        _record(),
    )

    assert result.is_persisted is True
    assert fsync_calls == []


@pytest.mark.parametrize(
    "directory",
    (
        "",
        "   ",
    ),
)
def test_directory_rejects_empty_string(
    directory: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="directory cannot be empty",
    ):
        JsonlEvidenceStore(
            directory=directory,
            max_file_size_bytes=10_000,
        )


def test_directory_rejects_invalid_type() -> None:
    with pytest.raises(
        TypeError,
        match="directory must be a string or Path",
    ):
        JsonlEvidenceStore(
            directory=123,
            max_file_size_bytes=10_000,
        )


@pytest.mark.parametrize(
    "max_file_size_bytes",
    (
        0,
        -1,
        -100,
    ),
)
def test_max_file_size_rejects_non_positive_value(
    max_file_size_bytes: int,
    tmp_path: Path,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "max_file_size_bytes must be greater than zero"
        ),
    ):
        JsonlEvidenceStore(
            directory=tmp_path,
            max_file_size_bytes=max_file_size_bytes,
        )


@pytest.mark.parametrize(
    "max_file_size_bytes",
    (
        True,
        False,
        1.5,
        "1000",
        None,
    ),
)
def test_max_file_size_rejects_non_integer_value(
    max_file_size_bytes: object,
    tmp_path: Path,
) -> None:
    with pytest.raises(
        TypeError,
        match="max_file_size_bytes must be an int",
    ):
        JsonlEvidenceStore(
            directory=tmp_path,
            max_file_size_bytes=max_file_size_bytes,
        )


@pytest.mark.parametrize(
    "file_prefix",
    (
        "",
        "   ",
    ),
)
def test_file_prefix_rejects_empty_value(
    file_prefix: str,
    tmp_path: Path,
) -> None:
    with pytest.raises(
        ValueError,
        match="file_prefix cannot be empty",
    ):
        JsonlEvidenceStore(
            directory=tmp_path,
            max_file_size_bytes=10_000,
            file_prefix=file_prefix,
        )


def test_file_prefix_rejects_non_string_value(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        TypeError,
        match="file_prefix must be a string",
    ):
        JsonlEvidenceStore(
            directory=tmp_path,
            max_file_size_bytes=10_000,
            file_prefix=123,
        )


@pytest.mark.parametrize(
    "flush_to_disk",
    (
        0,
        1,
        "true",
        None,
    ),
)
def test_flush_to_disk_requires_boolean(
    flush_to_disk: object,
    tmp_path: Path,
) -> None:
    with pytest.raises(
        TypeError,
        match="flush_to_disk must be a bool",
    ):
        JsonlEvidenceStore(
            directory=tmp_path,
            max_file_size_bytes=10_000,
            flush_to_disk=flush_to_disk,
        )
