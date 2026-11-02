# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Implements the universal Operational Evidence repository interface
# using local JSONL partitions.
#
# Responsibilities:
# - Retrieve evidence by record identity.
# - Retrieve bounded evidence by execution identity.
# - Retrieve bounded evidence by correlation identity.
# - Coordinate partition discovery and partition reading.
# - Enforce bounded physical scanning.
# - Surface detected partition corruption instead of hiding it.
#
# Must Not:
# - Persist Operational Evidence.
# - Decode JSON records directly.
# - Discover partition filenames directly.
# - Read physical JSONL lines directly.
# - Perform failure analysis or root-cause analysis.
# - Contain RAG or Knowledge-specific semantics.
# - Perform retention, rotation, or archival.
# - Silently ignore malformed Operational Evidence.
#
# Architectural Position:
# - Concrete local implementation of EvidenceRepository.
# - Coordinates JsonlPartitionLocator and JsonlPartitionReader.
# - Keeps repository consumers independent from JSONL storage.
#
# Future Extensibility:
# - Derived query indexes can reduce partition scanning.
# - Query acceleration can evolve without changing repository consumers.
# - Alternative persistence providers can implement the same repository
#   interface independently.

from __future__ import annotations

from pathlib import Path
from typing import Callable

from alhf.core.operational_evidence.contracts.record import (
    OperationalEvidenceRecord,
)
from alhf.core.operational_evidence.interfaces.evidence_repository import (
    EvidenceRepository,
)
from alhf.core.operational_evidence.providers.jsonl_partition_locator import (
    JsonlPartitionLocator,
)
from alhf.core.operational_evidence.providers.jsonl_partition_reader import (
    JsonlPartitionReader,
)


class JsonlEvidenceRepository(EvidenceRepository):
    """Bounded read/query repository over local JSONL evidence."""

    def __init__(
        self,
        directory: str | Path,
        *,
        max_line_bytes: int,
        max_scan_entries: int,
        file_prefix: str = "operational_evidence",
    ) -> None:
        self._max_scan_entries = self._validate_positive_int(
            value=max_scan_entries,
            field_name="max_scan_entries",
        )
        self._locator = JsonlPartitionLocator(
            directory,
            file_prefix=file_prefix,
        )
        self._reader = JsonlPartitionReader(
            max_line_bytes=max_line_bytes,
        )

    def get_by_record_id(
        self,
        record_id: str,
    ) -> OperationalEvidenceRecord | None:
        """Retrieve one evidence record by semantic record identity."""

        normalized_record_id = self._normalize_identifier(
            value=record_id,
            field_name="record_id",
        )

        records = self._find(
            predicate=lambda record: (
                record.record_id == normalized_record_id
            ),
            result_limit=1,
        )

        if not records:
            return None

        return records[0]

    def get_by_execution_id(
        self,
        execution_id: str,
        *,
        limit: int,
    ) -> tuple[OperationalEvidenceRecord, ...]:
        """Retrieve bounded evidence belonging to one execution."""

        normalized_execution_id = self._normalize_identifier(
            value=execution_id,
            field_name="execution_id",
        )
        validated_limit = self._validate_positive_int(
            value=limit,
            field_name="limit",
        )

        return self._find(
            predicate=lambda record: (
                record.execution.execution_id
                == normalized_execution_id
            ),
            result_limit=validated_limit,
        )

    def get_by_correlation_id(
        self,
        correlation_id: str,
        *,
        limit: int,
    ) -> tuple[OperationalEvidenceRecord, ...]:
        """Retrieve bounded evidence belonging to one correlation."""

        normalized_correlation_id = self._normalize_identifier(
            value=correlation_id,
            field_name="correlation_id",
        )
        validated_limit = self._validate_positive_int(
            value=limit,
            field_name="limit",
        )

        return self._find(
            predicate=lambda record: (
                record.execution.correlation_id
                == normalized_correlation_id
            ),
            result_limit=validated_limit,
        )

    def _find(
        self,
        *,
        predicate: Callable[[OperationalEvidenceRecord], bool],
        result_limit: int,
    ) -> tuple[OperationalEvidenceRecord, ...]:
        """Search partitions within the configured physical scan bound."""

        results: list[OperationalEvidenceRecord] = []
        scanned_entries = 0

        for partition in self._locator.locate():
            remaining_scan = (
                self._max_scan_entries - scanned_entries
            )

            if remaining_scan <= 0:
                break

            entries = self._reader.read(
                partition,
                limit=remaining_scan,
            )

            for entry in entries:
                scanned_entries += 1

                if not entry.is_valid:
                    raise RuntimeError(
                        "Operational Evidence repository contains "
                        f"invalid record at line {entry.line_number}: "
                        f"{entry.error_code}"
                    )

                record = entry.record

                if record is None:
                    raise RuntimeError(
                        "Operational Evidence reader returned an "
                        "invalid empty record state"
                    )

                if predicate(record):
                    results.append(record)

                    if len(results) >= result_limit:
                        return tuple(results)

                if scanned_entries >= self._max_scan_entries:
                    break

        return tuple(results)

    @staticmethod
    def _normalize_identifier(
        *,
        value: str,
        field_name: str,
    ) -> str:
        """Validate and normalize a required query identifier."""

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
    def _validate_positive_int(
        *,
        value: int,
        field_name: str,
    ) -> int:
        """Validate a positive integer query bound."""

        if isinstance(value, bool) or not isinstance(
            value,
            int,
        ):
            raise TypeError(
                f"{field_name} must be an int"
            )

        if value <= 0:
            raise ValueError(
                f"{field_name} must be greater than zero"
            )

        return value
