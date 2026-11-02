# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the local ALHF JSONL Operational Evidence repository.
#
# Responsibilities:
# - Validate retrieval by record identity.
# - Validate bounded retrieval by execution identity.
# - Validate bounded retrieval by correlation identity.
# - Validate missing-record behavior.
# - Validate identifier and limit validation.
# - Validate physical scan bounds.
# - Validate malformed evidence detection.
#
# Must Not:
# - Test Operational Evidence persistence.
# - Test partition rotation or retention.
# - Test RAG or Knowledge-specific semantics.
# - Test failure analysis or root-cause analysis.

import json
from pathlib import Path

import pytest

from alhf.core.operational_evidence.providers.jsonl_evidence_repository import (
    JsonlEvidenceRepository,
)


def _record_data(
    record_id: str,
    *,
    execution_id: str = "execution-001",
    correlation_id: str = "correlation-001",
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
            "correlation_id": correlation_id,
            "execution_id": execution_id,
            "operation_id": f"operation-{record_id}",
            "parent_operation_id": None,
        },
        "observed_at": "2026-10-27T12:30:00+00:00",
        "outcome": None,
        "measurements": [],
        "relationships": [],
    }


def _write_partition(
    directory: Path,
    partition_number: int,
    records: list[dict[str, object]],
) -> Path:
    partition = directory / (
        f"operational_evidence-{partition_number:06d}.jsonl"
    )

    with partition.open(
        mode="w",
        encoding="utf-8",
    ) as stream:
        for record in records:
            stream.write(json.dumps(record))
            stream.write("\n")

    return partition


def _repository(
    directory: Path,
    *,
    max_scan_entries: int = 100,
) -> JsonlEvidenceRepository:
    return JsonlEvidenceRepository(
        directory,
        max_line_bytes=4096,
        max_scan_entries=max_scan_entries,
    )


def test_get_by_record_id_returns_matching_record(
    tmp_path: Path,
) -> None:
    _write_partition(
        tmp_path,
        1,
        [
            _record_data("record-001"),
            _record_data("record-002"),
        ],
    )

    record = _repository(tmp_path).get_by_record_id(
        "record-002"
    )

    assert record is not None
    assert record.record_id == "record-002"


def test_get_by_record_id_returns_none_when_missing(
    tmp_path: Path,
) -> None:
    _write_partition(
        tmp_path,
        1,
        [_record_data("record-001")],
    )

    assert (
        _repository(tmp_path).get_by_record_id(
            "missing-record"
        )
        is None
    )


def test_record_id_is_whitespace_normalized(
    tmp_path: Path,
) -> None:
    _write_partition(
        tmp_path,
        1,
        [_record_data("record-001")],
    )

    record = _repository(tmp_path).get_by_record_id(
        "  record-001  "
    )

    assert record is not None
    assert record.record_id == "record-001"


def test_get_by_execution_id_returns_matching_records(
    tmp_path: Path,
) -> None:
    _write_partition(
        tmp_path,
        1,
        [
            _record_data("record-001", execution_id="execution-a"),
            _record_data("record-002", execution_id="execution-b"),
            _record_data("record-003", execution_id="execution-a"),
        ],
    )

    records = _repository(tmp_path).get_by_execution_id(
        "execution-a",
        limit=10,
    )

    assert tuple(record.record_id for record in records) == (
        "record-001",
        "record-003",
    )


def test_execution_query_respects_result_limit(
    tmp_path: Path,
) -> None:
    _write_partition(
        tmp_path,
        1,
        [
            _record_data("record-001"),
            _record_data("record-002"),
            _record_data("record-003"),
        ],
    )

    records = _repository(tmp_path).get_by_execution_id(
        "execution-001",
        limit=2,
    )

    assert len(records) == 2


def test_get_by_correlation_id_returns_matching_records(
    tmp_path: Path,
) -> None:
    _write_partition(
        tmp_path,
        1,
        [
            _record_data("record-001", correlation_id="correlation-a"),
            _record_data("record-002", correlation_id="correlation-b"),
            _record_data("record-003", correlation_id="correlation-a"),
        ],
    )

    records = _repository(tmp_path).get_by_correlation_id(
        "correlation-a",
        limit=10,
    )

    assert tuple(record.record_id for record in records) == (
        "record-001",
        "record-003",
    )


def test_repository_reads_across_partitions(
    tmp_path: Path,
) -> None:
    _write_partition(
        tmp_path,
        1,
        [_record_data("record-001")],
    )
    _write_partition(
        tmp_path,
        2,
        [_record_data("record-002")],
    )

    record = _repository(tmp_path).get_by_record_id(
        "record-002"
    )

    assert record is not None
    assert record.record_id == "record-002"


def test_physical_scan_bound_is_enforced(
    tmp_path: Path,
) -> None:
    _write_partition(
        tmp_path,
        1,
        [
            _record_data("record-001"),
            _record_data("record-002"),
        ],
    )

    record = _repository(
        tmp_path,
        max_scan_entries=1,
    ).get_by_record_id(
        "record-002"
    )

    assert record is None


def test_invalid_record_surfaces_repository_failure(
    tmp_path: Path,
) -> None:
    partition = (
        tmp_path / "operational_evidence-000001.jsonl"
    )
    partition.write_text(
        "{invalid-json}\n",
        encoding="utf-8",
    )

    with pytest.raises(
        RuntimeError,
        match="Operational Evidence repository contains invalid record",
    ):
        _repository(tmp_path).get_by_record_id(
            "record-001"
        )


@pytest.mark.parametrize(
    "identifier",
    (
        "",
        "   ",
    ),
)
def test_record_id_rejects_empty_value(
    tmp_path: Path,
    identifier: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="record_id cannot be empty",
    ):
        _repository(tmp_path).get_by_record_id(
            identifier
        )


@pytest.mark.parametrize(
    "limit",
    (
        0,
        -1,
    ),
)
def test_execution_limit_must_be_positive(
    tmp_path: Path,
    limit: int,
) -> None:
    with pytest.raises(
        ValueError,
        match="limit must be greater than zero",
    ):
        _repository(tmp_path).get_by_execution_id(
            "execution-001",
            limit=limit,
        )


def test_max_scan_entries_rejects_boolean(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        TypeError,
        match="max_scan_entries must be an int",
    ):
        JsonlEvidenceRepository(
            tmp_path,
            max_line_bytes=4096,
            max_scan_entries=True,
        )
