# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF AcquisitionResult contract.
#
# Responsibilities:
# - Validate bounded acquisition-result semantics.
# - Validate acquisition completion states.
# - Validate acquired-resource counts.
# - Validate continuation semantics.
# - Validate synchronization checkpoint references.
# - Validate state consistency.
# - Validate normalization and immutability.
#
# Must Not:
# - Test source acquisition.
# - Test provider-specific pagination.
# - Test acquired resource collections.
# - Test synchronization execution.
# - Test parsing, chunking, indexing, or retrieval.

from dataclasses import FrozenInstanceError

import pytest

from alhf.rag.ingestion.contracts.acquisition_result import (
    AcquisitionResult,
    AcquisitionStatus,
)


def test_create_completed_acquisition_result() -> None:
    result = AcquisitionResult(
        source_ref="source-001",
        status=AcquisitionStatus.COMPLETED,
        acquired_count=10,
        has_more=False,
    )

    assert result.source_ref == "source-001"
    assert result.status == AcquisitionStatus.COMPLETED
    assert result.acquired_count == 10
    assert result.has_more is False
    assert result.continuation_ref is None
    assert result.checkpoint_ref is None


def test_create_partial_acquisition_result() -> None:
    result = AcquisitionResult(
        source_ref="source-001",
        status=AcquisitionStatus.PARTIAL,
        acquired_count=100,
        has_more=True,
        continuation_ref="continuation-001",
        checkpoint_ref="checkpoint-001",
    )

    assert result.status == AcquisitionStatus.PARTIAL
    assert result.acquired_count == 100
    assert result.has_more is True
    assert result.continuation_ref == "continuation-001"
    assert result.checkpoint_ref == "checkpoint-001"


def test_create_failed_acquisition_result() -> None:
    result = AcquisitionResult(
        source_ref="source-001",
        status=AcquisitionStatus.FAILED,
        acquired_count=0,
        has_more=False,
    )

    assert result.status == AcquisitionStatus.FAILED
    assert result.acquired_count == 0
    assert result.has_more is False


@pytest.mark.parametrize(
    "status",
    tuple(AcquisitionStatus),
)
def test_all_acquisition_statuses_are_supported(
    status: AcquisitionStatus,
) -> None:
    result = AcquisitionResult(
        source_ref="source-001",
        status=status,
        acquired_count=0,
        has_more=False,
    )

    assert result.status == status


def test_zero_acquired_count_is_supported() -> None:
    result = AcquisitionResult(
        source_ref="source-001",
        status=AcquisitionStatus.COMPLETED,
        acquired_count=0,
        has_more=False,
    )

    assert result.acquired_count == 0


def test_source_ref_is_normalized() -> None:
    result = AcquisitionResult(
        source_ref="  source-001  ",
        status=AcquisitionStatus.COMPLETED,
        acquired_count=1,
        has_more=False,
    )

    assert result.source_ref == "source-001"


def test_optional_references_are_normalized() -> None:
    result = AcquisitionResult(
        source_ref="source-001",
        status=AcquisitionStatus.PARTIAL,
        acquired_count=10,
        has_more=True,
        continuation_ref="  continuation-001  ",
        checkpoint_ref="  checkpoint-001  ",
    )

    assert result.continuation_ref == "continuation-001"
    assert result.checkpoint_ref == "checkpoint-001"


@pytest.mark.parametrize(
    "source_ref",
    (
        "",
        "   ",
    ),
)
def test_source_ref_rejects_empty_value(
    source_ref: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="source_ref cannot be empty",
    ):
        AcquisitionResult(
            source_ref=source_ref,
            status=AcquisitionStatus.COMPLETED,
            acquired_count=0,
            has_more=False,
        )


def test_source_ref_rejects_non_string_value() -> None:
    with pytest.raises(
        TypeError,
        match="source_ref must be a string",
    ):
        AcquisitionResult(
            source_ref=123,
            status=AcquisitionStatus.COMPLETED,
            acquired_count=0,
            has_more=False,
        )


def test_status_rejects_non_enum_value() -> None:
    with pytest.raises(
        TypeError,
        match="status must be an instance of AcquisitionStatus",
    ):
        AcquisitionResult(
            source_ref="source-001",
            status="COMPLETED",
            acquired_count=0,
            has_more=False,
        )


@pytest.mark.parametrize(
    "acquired_count",
    (
        -1,
        -100,
    ),
)
def test_acquired_count_rejects_negative_value(
    acquired_count: int,
) -> None:
    with pytest.raises(
        ValueError,
        match="acquired_count cannot be negative",
    ):
        AcquisitionResult(
            source_ref="source-001",
            status=AcquisitionStatus.COMPLETED,
            acquired_count=acquired_count,
            has_more=False,
        )


@pytest.mark.parametrize(
    "acquired_count",
    (
        True,
        False,
        1.5,
        "10",
        None,
    ),
)
def test_acquired_count_rejects_non_integer_value(
    acquired_count: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="acquired_count must be an int",
    ):
        AcquisitionResult(
            source_ref="source-001",
            status=AcquisitionStatus.COMPLETED,
            acquired_count=acquired_count,
            has_more=False,
        )


@pytest.mark.parametrize(
    "has_more",
    (
        0,
        1,
        "true",
        None,
    ),
)
def test_has_more_requires_boolean(
    has_more: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="has_more must be a bool",
    ):
        AcquisitionResult(
            source_ref="source-001",
            status=AcquisitionStatus.PARTIAL,
            acquired_count=1,
            has_more=has_more,
        )


def test_additional_work_requires_continuation_ref() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "additional acquisition work requires continuation_ref"
        ),
    ):
        AcquisitionResult(
            source_ref="source-001",
            status=AcquisitionStatus.PARTIAL,
            acquired_count=10,
            has_more=True,
        )


def test_completed_result_cannot_have_more_work() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "completed acquisition cannot have additional work"
        ),
    ):
        AcquisitionResult(
            source_ref="source-001",
            status=AcquisitionStatus.COMPLETED,
            acquired_count=10,
            has_more=True,
            continuation_ref="continuation-001",
        )


def test_failed_result_cannot_have_more_work() -> None:
    with pytest.raises(
        ValueError,
        match="failed acquisition cannot declare additional work",
    ):
        AcquisitionResult(
            source_ref="source-001",
            status=AcquisitionStatus.FAILED,
            acquired_count=2,
            has_more=True,
            continuation_ref="continuation-001",
        )


def test_continuation_ref_requires_more_work() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "continuation_ref requires additional acquisition work"
        ),
    ):
        AcquisitionResult(
            source_ref="source-001",
            status=AcquisitionStatus.PARTIAL,
            acquired_count=10,
            has_more=False,
            continuation_ref="continuation-001",
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "continuation_ref",
        "checkpoint_ref",
    ),
)
def test_optional_reference_rejects_empty_value(
    field_name: str,
) -> None:
    values = {
        "source_ref": "source-001",
        "status": AcquisitionStatus.COMPLETED,
        "acquired_count": 1,
        "has_more": False,
        field_name: "   ",
    }

    with pytest.raises(
        ValueError,
        match=f"{field_name} cannot be empty when provided",
    ):
        AcquisitionResult(**values)


def test_acquisition_result_is_immutable() -> None:
    result = AcquisitionResult(
        source_ref="source-001",
        status=AcquisitionStatus.COMPLETED,
        acquired_count=10,
        has_more=False,
    )

    with pytest.raises(FrozenInstanceError):
        result.acquired_count = 20
