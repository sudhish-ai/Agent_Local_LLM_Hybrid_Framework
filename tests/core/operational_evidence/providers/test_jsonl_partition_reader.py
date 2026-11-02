# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF JSONL Operational Evidence partition reader.
#
# Responsibilities:
# - Validate bounded JSONL partition reading.
# - Validate valid Operational Evidence reconstruction.
# - Validate malformed JSON handling.
# - Validate invalid UTF-8 handling.
# - Validate oversized-line handling.
# - Validate invalid Operational Evidence handling.
# - Validate partition and limit validation.
# - Validate JsonlReadEntry invariants.
#
# Must Not:
# - Test partition discovery.
# - Test repository query orchestration.
# - Test Operational Evidence persistence.
# - Test RAG or Knowledge-specific semantics.
# - Test retention, rotation, or archival behavior.

import json
from pathlib import Path

import pytest

from alhf.core.operational_evidence.contracts.record import (
    OperationalEvidenceRecord,
)
from alhf.core.operational_evidence.providers.jsonl_partition_reader import (
    JsonlPartitionReader,
    JsonlReadEntry,
)


def _record_data(
    record_id: str = "record-001",
) -> dict[str, object]:
    return {
        "record_id": record_id,
        "schema": {
            "schema_id": "operational-evidence-record",
            "schema_version": "1.0",
        },
        "record_family": "OPERATIONAL_EVENT",
        "producer": "test-component",
        "event_name": "OPERATION_COMPLETED",
        "execution": {
            "correlation_id": "correlation-001",
            "execution_id": "execution-001",
            "operation_id": "operation-001",
            "parent_operation_id": None,
        },
        "observed_at": "2026-10-27T12:30:00+00:00",
        "outcome": None,
        "measurements": [],
        "relationships": [],
    }


def _write_jsonl(
    path: Path,
    records: list[dict[str, object]],
) -> None:
    with path.open(
        mode="w",
        encoding="utf-8",
    ) as stream:
        for record in records:
            stream.write(
                json.dumps(record)
            )
            stream.write("\n")


def test_read_valid_partition(
    tmp_path: Path,
) -> None:
    partition = tmp_path / "evidence.jsonl"
    _write_jsonl(
        partition,
        [_record_data()],
    )
    reader = JsonlPartitionReader(
        max_line_bytes=4096,
    )

    entries = reader.read(
        partition,
        limit=10,
    )

    assert len(entries) == 1
    assert entries[0].is_valid is True
    assert isinstance(
        entries[0].record,
        OperationalEvidenceRecord,
    )
    assert entries[0].record.record_id == "record-001"


def test_read_preserves_physical_line_numbers(
    tmp_path: Path,
) -> None:
    partition = tmp_path / "evidence.jsonl"
    _write_jsonl(
        partition,
        [
            _record_data("record-001"),
            _record_data("record-002"),
        ],
    )
    reader = JsonlPartitionReader(
        max_line_bytes=4096,
    )

    entries = reader.read(
        partition,
        limit=10,
    )

    assert tuple(
        entry.line_number
        for entry in entries
    ) == (1, 2)


def test_read_enforces_limit(
    tmp_path: Path,
) -> None:
    partition = tmp_path / "evidence.jsonl"
    _write_jsonl(
        partition,
        [
            _record_data("record-001"),
            _record_data("record-002"),
            _record_data("record-003"),
        ],
    )
    reader = JsonlPartitionReader(
        max_line_bytes=4096,
    )

    entries = reader.read(
        partition,
        limit=2,
    )

    assert len(entries) == 2


def test_malformed_json_does_not_hide_valid_records(
    tmp_path: Path,
) -> None:
    partition = tmp_path / "evidence.jsonl"
    valid_record = json.dumps(
        _record_data("record-002")
    )

    partition.write_text(
        "{invalid-json}\n"
        f"{valid_record}\n",
        encoding="utf-8",
    )

    reader = JsonlPartitionReader(
        max_line_bytes=4096,
    )

    entries = reader.read(
        partition,
        limit=10,
    )

    assert entries[0].error_code == "INVALID_JSON"
    assert entries[0].is_valid is False
    assert entries[1].is_valid is True
    assert entries[1].record is not None
    assert entries[1].record.record_id == "record-002"


def test_invalid_record_is_reported(
    tmp_path: Path,
) -> None:
    partition = tmp_path / "evidence.jsonl"
    partition.write_text(
        '{"record_id":"incomplete"}\n',
        encoding="utf-8",
    )

    reader = JsonlPartitionReader(
        max_line_bytes=4096,
    )

    entries = reader.read(
        partition,
        limit=10,
    )

    assert entries[0].error_code == "INVALID_RECORD"
    assert entries[0].is_valid is False


def test_non_object_json_is_reported_as_invalid_record(
    tmp_path: Path,
) -> None:
    partition = tmp_path / "evidence.jsonl"
    partition.write_text(
        '["not-an-object"]\n',
        encoding="utf-8",
    )

    reader = JsonlPartitionReader(
        max_line_bytes=4096,
    )

    entries = reader.read(
        partition,
        limit=10,
    )

    assert entries[0].error_code == "INVALID_RECORD"


def test_invalid_utf8_is_reported(
    tmp_path: Path,
) -> None:
    partition = tmp_path / "evidence.jsonl"
    partition.write_bytes(
        b"\xff\xfe\xfd\n"
    )

    reader = JsonlPartitionReader(
        max_line_bytes=4096,
    )

    entries = reader.read(
        partition,
        limit=10,
    )

    assert entries[0].error_code == "INVALID_UTF8"


def test_oversized_line_is_reported(
    tmp_path: Path,
) -> None:
    partition = tmp_path / "evidence.jsonl"
    partition.write_bytes(
        b"x" * 101 + b"\n"
    )

    reader = JsonlPartitionReader(
        max_line_bytes=100,
    )

    entries = reader.read(
        partition,
        limit=10,
    )

    assert entries[0].error_code == "LINE_SIZE_EXCEEDED"


@pytest.mark.parametrize(
    "max_line_bytes",
    (
        0,
        -1,
    ),
)
def test_max_line_bytes_must_be_positive(
    max_line_bytes: int,
) -> None:
    with pytest.raises(
        ValueError,
        match="max_line_bytes must be greater than zero",
    ):
        JsonlPartitionReader(
            max_line_bytes=max_line_bytes,
        )


@pytest.mark.parametrize(
    "max_line_bytes",
    (
        True,
        1.5,
        "100",
    ),
)
def test_max_line_bytes_requires_integer(
    max_line_bytes: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="max_line_bytes must be an int",
    ):
        JsonlPartitionReader(
            max_line_bytes=max_line_bytes,
        )


@pytest.mark.parametrize(
    "limit",
    (
        0,
        -1,
    ),
)
def test_read_limit_must_be_positive(
    tmp_path: Path,
    limit: int,
) -> None:
    reader = JsonlPartitionReader(
        max_line_bytes=4096,
    )

    with pytest.raises(
        ValueError,
        match="limit must be greater than zero",
    ):
        reader.read(
            tmp_path / "unused.jsonl",
            limit=limit,
        )


def test_partition_rejects_empty_string() -> None:
    reader = JsonlPartitionReader(
        max_line_bytes=4096,
    )

    with pytest.raises(
        ValueError,
        match="partition cannot be empty",
    ):
        reader.read(
            "   ",
            limit=1,
        )


def test_read_entry_requires_record_or_error() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "read entry must contain either record or error_code"
        ),
    ):
        JsonlReadEntry(
            line_number=1,
        )


def test_read_entry_rejects_record_and_error_together() -> None:
    record_data = _record_data()
    from alhf.core.operational_evidence.providers.jsonl_record_decoder import (
        JsonlRecordDecoder,
    )

    record = JsonlRecordDecoder.decode(
        record_data,
    )

    with pytest.raises(
        ValueError,
        match=(
            "read entry must contain either record or error_code"
        ),
    ):
        JsonlReadEntry(
            line_number=1,
            record=record,
            error_code="INVALID_RECORD",
        )
