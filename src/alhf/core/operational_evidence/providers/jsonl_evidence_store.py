# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides the local JSONL persistence implementation for the
# ALHF Operational Evidence Foundation.
#
# Problem Solved:
# ALHF requires a simple local persistence provider that can durably
# append serialized Operational Evidence records while keeping producers
# independent from JSONL and filesystem implementation details.
#
# Responsibilities:
# - Implement the universal EvidenceSink persistence boundary.
# - Persist Operational Evidence as one JSON object per line.
# - Keep individual JSONL partitions bounded by configured size.
# - Rotate to a new partition before a configured size limit is exceeded.
# - Preserve deterministic serializer output.
# - Flush successfully written evidence before reporting persistence.
# - Return provider-neutral PersistenceResult outcomes.
# - Serialize concurrent writes within one provider instance.
#
# Must Not:
# - Define Operational Evidence semantics.
# - Modify Operational Evidence records.
# - Generate evidence-record identities.
# - Perform failure analysis or root-cause analysis.
# - Contain RAG or Knowledge-specific semantics.
# - Expose physical file locations through PersistenceResult.
# - Implement Operational Evidence querying.
# - Implement retention or archival policy.
# - Implement asynchronous buffering.
# - Implement distributed or multi-process coordination.
# - Contain arbitrary metadata or diagnostic payloads.
#
# Architectural Position:
# - Concrete local Operational Evidence persistence provider.
# - Implements the universal EvidenceSink interface.
# - Uses JsonEvidenceSerializer for deterministic record serialization.
# - Replaceable without changing Operational Evidence producers.
#
# Reuse Value:
# - Local ALHF development.
# - Deterministic integration testing.
# - Local Knowledge Foundation execution.
# - Failure-analysis and RCA development.
# - Reference behavior for future persistence providers.
#
# Future Extensibility:
# - Repository/query behavior remains a separate responsibility.
# - Retention and archival remain separate policies.
# - Stronger durability behavior can be introduced behind provider
#   configuration.
# - Multi-process and distributed persistence remain separate provider
#   capabilities.

from __future__ import annotations

import os
import threading
from pathlib import Path

from alhf.core.operational_evidence.contracts.outcome import (
    RetryDisposition,
)
from alhf.core.operational_evidence.contracts.persistence_result import (
    PersistenceResult,
    PersistenceStatus,
)
from alhf.core.operational_evidence.contracts.record import (
    OperationalEvidenceRecord,
)
from alhf.core.operational_evidence.interfaces.evidence_sink import (
    EvidenceSink,
)
from alhf.core.operational_evidence.serializers.json_evidence_serializer import (
    JsonEvidenceSerializer,
)


class JsonlEvidenceStore(EvidenceSink):
    """
    Local JSONL persistence provider for Operational Evidence.

    Each record is serialized as deterministic JSON and persisted as one
    newline-terminated UTF-8 entry.

    Physical partitions are bounded by max_file_size_bytes. Rotation is
    provider-internal and never changes Operational Evidence identity.

    Thread synchronization protects writes performed through one provider
    instance. This provider does not claim multi-process coordination.
    """

    _FILE_SUFFIX = ".jsonl"
    _DEFAULT_FILE_PREFIX = "operational_evidence"

    def __init__(
        self,
        directory: str | Path,
        *,
        max_file_size_bytes: int,
        file_prefix: str = _DEFAULT_FILE_PREFIX,
        flush_to_disk: bool = False,
    ) -> None:
        self._directory = self._validate_directory(
            directory=directory,
        )
        self._max_file_size_bytes = self._validate_max_file_size(
            value=max_file_size_bytes,
        )
        self._file_prefix = self._normalize_required_text(
            value=file_prefix,
            field_name="file_prefix",
        )

        if not isinstance(
            flush_to_disk,
            bool,
        ):
            raise TypeError(
                "flush_to_disk must be a bool"
            )

        self._flush_to_disk = flush_to_disk
        self._lock = threading.Lock()
        self._partition_number: int | None = None

    def persist(
        self,
        record: OperationalEvidenceRecord,
    ) -> PersistenceResult:
        """
        Persist one Operational Evidence record.

        Persistence failures are returned through the provider-neutral
        PersistenceResult contract rather than exposing filesystem
        exceptions to evidence producers.
        """

        if not isinstance(
            record,
            OperationalEvidenceRecord,
        ):
            raise TypeError(
                "record must be an instance of OperationalEvidenceRecord"
            )

        try:
            serialized_record = JsonEvidenceSerializer.to_json(
                record,
            )
            encoded_record = (
                serialized_record + "\n"
            ).encode("utf-8")
        except (TypeError, ValueError):
            return PersistenceResult(
                record_id=record.record_id,
                status=PersistenceStatus.REJECTED,
                failure_code="SERIALIZATION_REJECTED",
                failure_message=(
                    "Operational Evidence record could not be serialized"
                ),
                retry_disposition=RetryDisposition.NOT_RETRYABLE,
            )

        if len(encoded_record) > self._max_file_size_bytes:
            return PersistenceResult(
                record_id=record.record_id,
                status=PersistenceStatus.REJECTED,
                failure_code="RECORD_EXCEEDS_PARTITION_LIMIT",
                failure_message=(
                    "Serialized Operational Evidence record exceeds the "
                    "configured partition size limit"
                ),
                retry_disposition=RetryDisposition.NOT_RETRYABLE,
            )

        try:
            with self._lock:
                self._directory.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                partition = self._resolve_partition(
                    incoming_size=len(encoded_record),
                )

                with partition.open(
                    mode="ab",
                ) as stream:
                    stream.write(
                        encoded_record,
                    )
                    stream.flush()

                    if self._flush_to_disk:
                        os.fsync(
                            stream.fileno(),
                        )

        except (OSError, RuntimeError):
            return PersistenceResult(
                record_id=record.record_id,
                status=PersistenceStatus.FAILED,
                failure_code="PERSISTENCE_IO_FAILURE",
                failure_message=(
                    "Operational Evidence could not be persisted"
                ),
                retry_disposition=RetryDisposition.UNKNOWN,
            )

        return PersistenceResult(
            record_id=record.record_id,
            status=PersistenceStatus.PERSISTED,
        )

    def _resolve_partition(
        self,
        *,
        incoming_size: int,
    ) -> Path:
        """Resolve the writable partition for the incoming record."""

        if self._partition_number is None:
            self._partition_number = self._discover_latest_partition()

        partition = self._partition_path(
            partition_number=self._partition_number,
        )

        if not partition.exists():
            return partition

        current_size = partition.stat().st_size

        if (
            current_size + incoming_size
            <= self._max_file_size_bytes
        ):
            return partition

        self._partition_number += 1

        return self._partition_path(
            partition_number=self._partition_number,
        )

    def _discover_latest_partition(self) -> int:
        """Discover the highest existing partition number."""

        highest_partition = 1
        found_partition = False

        pattern = (
            f"{self._file_prefix}-*"
            f"{self._FILE_SUFFIX}"
        )

        for path in self._directory.glob(
            pattern,
        ):
            partition_number = self._extract_partition_number(
                path=path,
            )

            if partition_number is None:
                continue

            if (
                not found_partition
                or partition_number > highest_partition
            ):
                highest_partition = partition_number
                found_partition = True

        if not found_partition:
            return 1

        return highest_partition

    def _extract_partition_number(
        self,
        *,
        path: Path,
    ) -> int | None:
        """Extract a valid partition number from a provider filename."""

        expected_prefix = f"{self._file_prefix}-"
        filename = path.name

        if not filename.startswith(
            expected_prefix,
        ):
            return None

        if not filename.endswith(
            self._FILE_SUFFIX,
        ):
            return None

        number_text = filename[
            len(expected_prefix):
            -len(self._FILE_SUFFIX)
        ]

        if not number_text.isdigit():
            return None

        partition_number = int(
            number_text,
        )

        if partition_number < 1:
            return None

        return partition_number

    def _partition_path(
        self,
        *,
        partition_number: int,
    ) -> Path:
        """Create the physical path for one JSONL partition."""

        filename = (
            f"{self._file_prefix}-"
            f"{partition_number:06d}"
            f"{self._FILE_SUFFIX}"
        )

        return self._directory / filename

    @staticmethod
    def _validate_directory(
        *,
        directory: str | Path,
    ) -> Path:
        """Validate the configured local evidence directory."""

        if isinstance(
            directory,
            Path,
        ):
            path = directory
        elif isinstance(
            directory,
            str,
        ):
            normalized_directory = directory.strip()

            if not normalized_directory:
                raise ValueError(
                    "directory cannot be empty"
                )

            path = Path(
                normalized_directory,
            )
        else:
            raise TypeError(
                "directory must be a string or Path"
            )

        if not str(path).strip():
            raise ValueError(
                "directory cannot be empty"
            )

        return path

    @staticmethod
    def _validate_max_file_size(
        *,
        value: int,
    ) -> int:
        """Validate the configured maximum JSONL partition size."""

        if isinstance(
            value,
            bool,
        ) or not isinstance(
            value,
            int,
        ):
            raise TypeError(
                "max_file_size_bytes must be an int"
            )

        if value <= 0:
            raise ValueError(
                "max_file_size_bytes must be greater than zero"
            )

        return value

    @staticmethod
    def _normalize_required_text(
        *,
        value: str,
        field_name: str,
    ) -> str:
        """Validate and normalize one required provider text value."""

        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                f"{field_name} must be a string"
            )

        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError(
                f"{field_name} cannot be empty"
            )

        return normalized_value
