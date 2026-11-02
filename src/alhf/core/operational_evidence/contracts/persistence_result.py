# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the universal persistence-result contract used by the
# ALHF Operational Evidence Foundation.
#
# Problem Solved:
# Operational Evidence persistence must report whether a record was
# durably accepted without exposing provider-specific storage behavior
# to producers or consumers.
#
# Persistence outcomes must remain independent from JSONL, databases,
# object storage, event infrastructure, or future persistence providers.
#
# Responsibilities:
# - Represent the result of one evidence-persistence operation.
# - Preserve the identity of the affected Operational Evidence record.
# - Preserve the persistence outcome.
# - Preserve optional provider-neutral failure information.
# - Preserve retryability without forcing false certainty.
# - Provide immutable, storage-independent persistence semantics.
#
# Must Not:
# - Persist Operational Evidence.
# - Contain JSON or JSONL behavior.
# - Expose physical file paths, line numbers, row identifiers, or offsets.
# - Contain provider-specific error codes.
# - Contain RAG or Knowledge-specific semantics.
# - Perform retry logic.
# - Perform buffering, batching, or backpressure.
# - Perform failure analysis or root-cause analysis.
# - Contain arbitrary metadata or payload dictionaries.
#
# Architectural Position:
# - Universal ALHF Operational Evidence contract.
# - Boundary result between evidence producers and persistence providers.
# - Independent from physical storage implementation.
#
# Reuse Value:
# - Local Operational Evidence persistence.
# - Future database-backed persistence.
# - Future object-backed persistence.
# - Future distributed persistence providers.
# - Failure analysis of evidence-persistence health.
#
# Future Extensibility:
# - Provider-specific diagnostics remain separately governed.
# - Durability policy remains separate from persistence outcome.
# - Batching and asynchronous delivery remain provider responsibilities.
# - Repository query semantics remain separate from persistence semantics.

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from alhf.core.operational_evidence.contracts.outcome import (
    RetryDisposition,
)


class PersistenceStatus(str, Enum):
    """Provider-neutral status of an Operational Evidence persistence."""

    PERSISTED = "PERSISTED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class PersistenceResult:
    """
    Immutable result of one Operational Evidence persistence operation.

    record_id:
        Storage-independent identity of the Operational Evidence record.

    status:
        Provider-neutral persistence outcome.

    failure_code:
        Optional stable ALHF-level failure identifier.

    failure_message:
        Optional bounded provider-neutral diagnostic message.

    retry_disposition:
        Optional retryability classification for failed or rejected
        persistence.

    A successfully persisted result cannot contain failure information.
    Failed or rejected persistence must include a failure code, failure
    message, and retry disposition.

    UNKNOWN preserves uncertainty when the persistence outcome cannot be
    established. It does not fabricate failure or success.
    """

    record_id: str
    status: PersistenceStatus
    failure_code: str | None = None
    failure_message: str | None = None
    retry_disposition: RetryDisposition | None = None

    def __post_init__(self) -> None:
        record_id = self._normalize_required_text(
            value=self.record_id,
            field_name="record_id",
        )
        failure_code = self._normalize_optional_text(
            value=self.failure_code,
            field_name="failure_code",
        )
        failure_message = self._normalize_optional_text(
            value=self.failure_message,
            field_name="failure_message",
        )

        if not isinstance(
            self.status,
            PersistenceStatus,
        ):
            raise TypeError(
                "status must be an instance of PersistenceStatus"
            )

        if (
            self.retry_disposition is not None
            and not isinstance(
                self.retry_disposition,
                RetryDisposition,
            )
        ):
            raise TypeError(
                "retry_disposition must be an instance of "
                "RetryDisposition or None"
            )

        self._validate_state(
            status=self.status,
            failure_code=failure_code,
            failure_message=failure_message,
            retry_disposition=self.retry_disposition,
        )

        object.__setattr__(
            self,
            "record_id",
            record_id,
        )
        object.__setattr__(
            self,
            "failure_code",
            failure_code,
        )
        object.__setattr__(
            self,
            "failure_message",
            failure_message,
        )

    @property
    def is_persisted(self) -> bool:
        """Return whether persistence is explicitly successful."""

        return self.status == PersistenceStatus.PERSISTED

    @property
    def has_failure(self) -> bool:
        """Return whether persistence explicitly failed or was rejected."""

        return self.status in {
            PersistenceStatus.REJECTED,
            PersistenceStatus.FAILED,
        }

    @property
    def is_unknown(self) -> bool:
        """Return whether the persistence outcome is unknown."""

        return self.status == PersistenceStatus.UNKNOWN

    @staticmethod
    def _normalize_required_text(
        *,
        value: str,
        field_name: str,
    ) -> str:
        """Validate and normalize a required text value."""

        if not isinstance(value, str):
            raise TypeError(
                f"{field_name} must be a string"
            )

        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError(
                f"{field_name} cannot be empty"
            )

        return normalized_value

    @staticmethod
    def _normalize_optional_text(
        *,
        value: str | None,
        field_name: str,
    ) -> str | None:
        """Validate and normalize an optional text value."""

        if value is None:
            return None

        if not isinstance(value, str):
            raise TypeError(
                f"{field_name} must be a string or None"
            )

        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError(
                f"{field_name} cannot be empty when provided"
            )

        return normalized_value

    @staticmethod
    def _validate_state(
        *,
        status: PersistenceStatus,
        failure_code: str | None,
        failure_message: str | None,
        retry_disposition: RetryDisposition | None,
    ) -> None:
        """Validate persistence-result state consistency."""

        if status == PersistenceStatus.PERSISTED:
            if (
                failure_code is not None
                or failure_message is not None
                or retry_disposition is not None
            ):
                raise ValueError(
                    "persisted result cannot contain failure information"
                )
            return

        if status in {
            PersistenceStatus.REJECTED,
            PersistenceStatus.FAILED,
        }:
            if failure_code is None:
                raise ValueError(
                    "failed or rejected result requires failure_code"
                )

            if failure_message is None:
                raise ValueError(
                    "failed or rejected result requires failure_message"
                )

            if retry_disposition is None:
                raise ValueError(
                    "failed or rejected result requires "
                    "retry_disposition"
                )

            return

        if status == PersistenceStatus.UNKNOWN:
            if (
                failure_code is not None
                or failure_message is not None
                or retry_disposition is not None
            ):
                raise ValueError(
                    "unknown result cannot contain failure information"
                )
