# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the universal ALHF PersistenceResult contract.
#
# Responsibilities:
# - Validate successful persistence results.
# - Validate failed persistence results.
# - Validate rejected persistence results.
# - Validate unknown persistence results.
# - Validate record identity normalization.
# - Validate failure-information normalization.
# - Validate retry-disposition semantics.
# - Validate invalid persistence states.
# - Validate invalid field types.
# - Validate immutability.
#
# Must Not:
# - Test physical persistence.
# - Test JSON or JSONL behavior.
# - Test buffering, batching, or backpressure.
# - Test provider-specific failures.
# - Test RAG or Knowledge-specific behavior.
# - Test retry execution.
# - Test failure analysis or root-cause analysis.

from dataclasses import FrozenInstanceError

import pytest

from alhf.core.operational_evidence.contracts.outcome import (
    RetryDisposition,
)
from alhf.core.operational_evidence.contracts.persistence_result import (
    PersistenceResult,
    PersistenceStatus,
)


def test_create_persisted_result() -> None:
    result = PersistenceResult(
        record_id="record-001",
        status=PersistenceStatus.PERSISTED,
    )

    assert result.record_id == "record-001"
    assert result.status == PersistenceStatus.PERSISTED
    assert result.failure_code is None
    assert result.failure_message is None
    assert result.retry_disposition is None


def test_persisted_result_reports_is_persisted() -> None:
    result = PersistenceResult(
        record_id="record-001",
        status=PersistenceStatus.PERSISTED,
    )

    assert result.is_persisted is True
    assert result.has_failure is False
    assert result.is_unknown is False


def test_create_failed_result() -> None:
    result = PersistenceResult(
        record_id="record-001",
        status=PersistenceStatus.FAILED,
        failure_code="PERSISTENCE_UNAVAILABLE",
        failure_message="Persistence provider is unavailable",
        retry_disposition=RetryDisposition.RETRYABLE,
    )

    assert result.record_id == "record-001"
    assert result.status == PersistenceStatus.FAILED
    assert result.failure_code == "PERSISTENCE_UNAVAILABLE"
    assert (
        result.failure_message
        == "Persistence provider is unavailable"
    )
    assert (
        result.retry_disposition
        == RetryDisposition.RETRYABLE
    )


def test_failed_result_reports_failure() -> None:
    result = PersistenceResult(
        record_id="record-001",
        status=PersistenceStatus.FAILED,
        failure_code="PERSISTENCE_UNAVAILABLE",
        failure_message="Persistence provider is unavailable",
        retry_disposition=RetryDisposition.RETRYABLE,
    )

    assert result.is_persisted is False
    assert result.has_failure is True
    assert result.is_unknown is False


def test_create_rejected_result() -> None:
    result = PersistenceResult(
        record_id="record-001",
        status=PersistenceStatus.REJECTED,
        failure_code="RECORD_REJECTED",
        failure_message="Record was rejected",
        retry_disposition=RetryDisposition.NOT_RETRYABLE,
    )

    assert result.status == PersistenceStatus.REJECTED
    assert result.failure_code == "RECORD_REJECTED"
    assert result.failure_message == "Record was rejected"
    assert (
        result.retry_disposition
        == RetryDisposition.NOT_RETRYABLE
    )


def test_rejected_result_reports_failure() -> None:
    result = PersistenceResult(
        record_id="record-001",
        status=PersistenceStatus.REJECTED,
        failure_code="RECORD_REJECTED",
        failure_message="Record was rejected",
        retry_disposition=RetryDisposition.NOT_RETRYABLE,
    )

    assert result.is_persisted is False
    assert result.has_failure is True
    assert result.is_unknown is False


def test_create_unknown_result() -> None:
    result = PersistenceResult(
        record_id="record-001",
        status=PersistenceStatus.UNKNOWN,
    )

    assert result.status == PersistenceStatus.UNKNOWN
    assert result.failure_code is None
    assert result.failure_message is None
    assert result.retry_disposition is None


def test_unknown_result_reports_unknown() -> None:
    result = PersistenceResult(
        record_id="record-001",
        status=PersistenceStatus.UNKNOWN,
    )

    assert result.is_persisted is False
    assert result.has_failure is False
    assert result.is_unknown is True


def test_record_id_is_whitespace_normalized() -> None:
    result = PersistenceResult(
        record_id="  record-001  ",
        status=PersistenceStatus.PERSISTED,
    )

    assert result.record_id == "record-001"


def test_failure_information_is_whitespace_normalized() -> None:
    result = PersistenceResult(
        record_id="record-001",
        status=PersistenceStatus.FAILED,
        failure_code="  PERSISTENCE_UNAVAILABLE  ",
        failure_message="  Persistence provider is unavailable  ",
        retry_disposition=RetryDisposition.RETRYABLE,
    )

    assert result.failure_code == "PERSISTENCE_UNAVAILABLE"
    assert (
        result.failure_message
        == "Persistence provider is unavailable"
    )


@pytest.mark.parametrize(
    "record_id",
    (
        "",
        "   ",
    ),
)
def test_record_id_rejects_empty_value(
    record_id: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="record_id cannot be empty",
    ):
        PersistenceResult(
            record_id=record_id,
            status=PersistenceStatus.PERSISTED,
        )


def test_record_id_rejects_non_string_value() -> None:
    with pytest.raises(
        TypeError,
        match="record_id must be a string",
    ):
        PersistenceResult(
            record_id=123,
            status=PersistenceStatus.PERSISTED,
        )


def test_status_rejects_non_enum_value() -> None:
    with pytest.raises(
        TypeError,
        match="status must be an instance of PersistenceStatus",
    ):
        PersistenceResult(
            record_id="record-001",
            status="PERSISTED",
        )


@pytest.mark.parametrize(
    "failure_code",
    (
        "",
        "   ",
    ),
)
def test_failure_code_rejects_empty_value_when_provided(
    failure_code: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="failure_code cannot be empty when provided",
    ):
        PersistenceResult(
            record_id="record-001",
            status=PersistenceStatus.FAILED,
            failure_code=failure_code,
            failure_message="Persistence failed",
            retry_disposition=RetryDisposition.RETRYABLE,
        )


def test_failure_code_rejects_non_string_value() -> None:
    with pytest.raises(
        TypeError,
        match="failure_code must be a string or None",
    ):
        PersistenceResult(
            record_id="record-001",
            status=PersistenceStatus.FAILED,
            failure_code=123,
            failure_message="Persistence failed",
            retry_disposition=RetryDisposition.RETRYABLE,
        )


@pytest.mark.parametrize(
    "failure_message",
    (
        "",
        "   ",
    ),
)
def test_failure_message_rejects_empty_value_when_provided(
    failure_message: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="failure_message cannot be empty when provided",
    ):
        PersistenceResult(
            record_id="record-001",
            status=PersistenceStatus.FAILED,
            failure_code="PERSISTENCE_FAILED",
            failure_message=failure_message,
            retry_disposition=RetryDisposition.RETRYABLE,
        )


def test_failure_message_rejects_non_string_value() -> None:
    with pytest.raises(
        TypeError,
        match="failure_message must be a string or None",
    ):
        PersistenceResult(
            record_id="record-001",
            status=PersistenceStatus.FAILED,
            failure_code="PERSISTENCE_FAILED",
            failure_message=123,
            retry_disposition=RetryDisposition.RETRYABLE,
        )


def test_retry_disposition_rejects_non_enum_value() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "retry_disposition must be an instance of "
            "RetryDisposition or None"
        ),
    ):
        PersistenceResult(
            record_id="record-001",
            status=PersistenceStatus.FAILED,
            failure_code="PERSISTENCE_FAILED",
            failure_message="Persistence failed",
            retry_disposition="RETRYABLE",
        )


@pytest.mark.parametrize(
    "retry_disposition",
    tuple(RetryDisposition),
)
def test_failed_result_supports_all_retry_dispositions(
    retry_disposition: RetryDisposition,
) -> None:
    result = PersistenceResult(
        record_id="record-001",
        status=PersistenceStatus.FAILED,
        failure_code="PERSISTENCE_FAILED",
        failure_message="Persistence failed",
        retry_disposition=retry_disposition,
    )

    assert result.retry_disposition == retry_disposition


def test_persisted_result_rejects_failure_code() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "persisted result cannot contain failure information"
        ),
    ):
        PersistenceResult(
            record_id="record-001",
            status=PersistenceStatus.PERSISTED,
            failure_code="UNEXPECTED_FAILURE",
        )


def test_persisted_result_rejects_failure_message() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "persisted result cannot contain failure information"
        ),
    ):
        PersistenceResult(
            record_id="record-001",
            status=PersistenceStatus.PERSISTED,
            failure_message="Unexpected failure",
        )


def test_persisted_result_rejects_retry_disposition() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "persisted result cannot contain failure information"
        ),
    ):
        PersistenceResult(
            record_id="record-001",
            status=PersistenceStatus.PERSISTED,
            retry_disposition=RetryDisposition.RETRYABLE,
        )


def test_failed_result_requires_failure_code() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "failed or rejected result requires failure_code"
        ),
    ):
        PersistenceResult(
            record_id="record-001",
            status=PersistenceStatus.FAILED,
            failure_message="Persistence failed",
            retry_disposition=RetryDisposition.RETRYABLE,
        )


def test_failed_result_requires_failure_message() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "failed or rejected result requires failure_message"
        ),
    ):
        PersistenceResult(
            record_id="record-001",
            status=PersistenceStatus.FAILED,
            failure_code="PERSISTENCE_FAILED",
            retry_disposition=RetryDisposition.RETRYABLE,
        )


def test_failed_result_requires_retry_disposition() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "failed or rejected result requires retry_disposition"
        ),
    ):
        PersistenceResult(
            record_id="record-001",
            status=PersistenceStatus.FAILED,
            failure_code="PERSISTENCE_FAILED",
            failure_message="Persistence failed",
        )


def test_rejected_result_requires_failure_code() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "failed or rejected result requires failure_code"
        ),
    ):
        PersistenceResult(
            record_id="record-001",
            status=PersistenceStatus.REJECTED,
            failure_message="Record rejected",
            retry_disposition=RetryDisposition.NOT_RETRYABLE,
        )


def test_rejected_result_requires_failure_message() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "failed or rejected result requires failure_message"
        ),
    ):
        PersistenceResult(
            record_id="record-001",
            status=PersistenceStatus.REJECTED,
            failure_code="RECORD_REJECTED",
            retry_disposition=RetryDisposition.NOT_RETRYABLE,
        )


def test_rejected_result_requires_retry_disposition() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "failed or rejected result requires retry_disposition"
        ),
    ):
        PersistenceResult(
            record_id="record-001",
            status=PersistenceStatus.REJECTED,
            failure_code="RECORD_REJECTED",
            failure_message="Record rejected",
        )


def test_unknown_result_rejects_failure_code() -> None:
    with pytest.raises(
        ValueError,
        match="unknown result cannot contain failure information",
    ):
        PersistenceResult(
            record_id="record-001",
            status=PersistenceStatus.UNKNOWN,
            failure_code="UNKNOWN_FAILURE",
        )


def test_unknown_result_rejects_failure_message() -> None:
    with pytest.raises(
        ValueError,
        match="unknown result cannot contain failure information",
    ):
        PersistenceResult(
            record_id="record-001",
            status=PersistenceStatus.UNKNOWN,
            failure_message="Unknown persistence state",
        )


def test_unknown_result_rejects_retry_disposition() -> None:
    with pytest.raises(
        ValueError,
        match="unknown result cannot contain failure information",
    ):
        PersistenceResult(
            record_id="record-001",
            status=PersistenceStatus.UNKNOWN,
            retry_disposition=RetryDisposition.UNKNOWN,
        )


def test_persistence_result_is_immutable() -> None:
    result = PersistenceResult(
        record_id="record-001",
        status=PersistenceStatus.PERSISTED,
    )

    with pytest.raises(FrozenInstanceError):
        result.status = PersistenceStatus.FAILED
