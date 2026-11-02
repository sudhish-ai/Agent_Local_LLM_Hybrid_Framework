# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides bounded reading of one local Operational Evidence JSONL
# partition.
#
# Responsibilities:
# - Read one physical JSONL partition.
# - Decode valid JSONL records through JsonlRecordDecoder.
# - Preserve valid records when another line is malformed.
# - Surface malformed records explicitly instead of silently skipping them.
# - Enforce bounded record retrieval.
# - Enforce a configurable maximum physical line size.
#
# Must Not:
# - Discover JSONL partitions.
# - Select partitions for repository queries.
# - Perform repository queries.
# - Persist Operational Evidence.
# - Perform failure analysis or root-cause analysis.
# - Contain RAG or Knowledge-specific semantics.
# - Repair malformed Operational Evidence.
# - Define retention, rotation, or archival behavior.
#
# Architectural Position:
# - Local JSONL provider reading component.
# - Operates below the JSONL repository implementation.
# - Uses JsonlRecordDecoder for contract reconstruction.
# - Keeps physical reading separate from repository query semantics.
#
# Future Extensibility:
# - Partition discovery remains a separate component.
# - Query acceleration remains a separate responsibility.
# - Corrupt-record recovery remains separately governed.
# - Alternative providers can implement independent physical readers.

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from alhf.core.operational_evidence.contracts.record import (
    OperationalEvidenceRecord,
)
from alhf.core.operational_evidence.providers.jsonl_record_decoder import (
    JsonlRecordDecoder,
)


@dataclass(frozen=True, slots=True)
class JsonlReadEntry:
    """Result of reading and decoding one physical JSONL line."""

    line_number: int
    record: OperationalEvidenceRecord | None = None
    error_code: str | None = None

    def __post_init__(self) -> None:
        if (
            isinstance(self.line_number, bool)
            or not isinstance(self.line_number, int)
        ):
            raise TypeError(
                "line_number must be an int"
            )

        if self.line_number < 1:
            raise ValueError(
                "line_number must be greater than zero"
            )

        has_record = self.record is not None
        has_error = self.error_code is not None

        if has_record == has_error:
            raise ValueError(
                "read entry must contain either record or error_code"
            )

        if self.record is not None and not isinstance(
            self.record,
            OperationalEvidenceRecord,
        ):
            raise TypeError(
                "record must be an instance of "
                "OperationalEvidenceRecord or None"
            )

        if self.error_code is not None:
            if not isinstance(
                self.error_code,
                str,
            ):
                raise TypeError(
                    "error_code must be a string or None"
                )

            normalized_error_code = self.error_code.strip()

            if not normalized_error_code:
                raise ValueError(
                    "error_code cannot be empty when provided"
                )

            object.__setattr__(
                self,
                "error_code",
                normalized_error_code,
            )

    @property
    def is_valid(self) -> bool:
        """Return whether this line produced a valid evidence record."""

        return self.record is not None


class JsonlPartitionReader:
    """Bounded reader for one Operational Evidence JSONL partition."""

    def __init__(
        self,
        *,
        max_line_bytes: int,
    ) -> None:
        if (
            isinstance(max_line_bytes, bool)
            or not isinstance(max_line_bytes, int)
        ):
            raise TypeError(
                "max_line_bytes must be an int"
            )

        if max_line_bytes <= 0:
            raise ValueError(
                "max_line_bytes must be greater than zero"
            )

        self._max_line_bytes = max_line_bytes

    def read(
        self,
        partition: str | Path,
        *,
        limit: int,
    ) -> tuple[JsonlReadEntry, ...]:
        """Read at most limit physical entries from one JSONL partition."""

        path = self._validate_partition(
            partition=partition,
        )
        self._validate_limit(
            limit=limit,
        )

        entries: list[JsonlReadEntry] = []

        with path.open(
            mode="rb",
        ) as stream:
            for line_number, raw_line in enumerate(
                stream,
                start=1,
            ):
                if len(entries) >= limit:
                    break

                entries.append(
                    self._decode_line(
                        raw_line=raw_line,
                        line_number=line_number,
                    )
                )

        return tuple(entries)

    def _decode_line(
        self,
        *,
        raw_line: bytes,
        line_number: int,
    ) -> JsonlReadEntry:
        if len(raw_line) > self._max_line_bytes:
            return JsonlReadEntry(
                line_number=line_number,
                error_code="LINE_SIZE_EXCEEDED",
            )

        try:
            decoded_text = raw_line.decode("utf-8")
            data = json.loads(decoded_text)

            if not isinstance(
                data,
                dict,
            ):
                raise TypeError(
                    "JSONL record must decode to an object"
                )

            record = JsonlRecordDecoder.decode(
                data,
            )
        except UnicodeDecodeError:
            return JsonlReadEntry(
                line_number=line_number,
                error_code="INVALID_UTF8",
            )
        except json.JSONDecodeError:
            return JsonlReadEntry(
                line_number=line_number,
                error_code="INVALID_JSON",
            )
        except (TypeError, ValueError):
            return JsonlReadEntry(
                line_number=line_number,
                error_code="INVALID_RECORD",
            )

        return JsonlReadEntry(
            line_number=line_number,
            record=record,
        )

    @staticmethod
    def _validate_partition(
        *,
        partition: str | Path,
    ) -> Path:
        if isinstance(partition, Path):
            return partition

        if not isinstance(partition, str):
            raise TypeError(
                "partition must be a string or Path"
            )

        normalized_partition = partition.strip()

        if not normalized_partition:
            raise ValueError(
                "partition cannot be empty"
            )

        return Path(
            normalized_partition,
        )

    @staticmethod
    def _validate_limit(
        *,
        limit: int,
    ) -> None:
        if isinstance(limit, bool) or not isinstance(
            limit,
            int,
        ):
            raise TypeError(
                "limit must be an int"
            )

        if limit <= 0:
            raise ValueError(
                "limit must be greater than zero"
            )
