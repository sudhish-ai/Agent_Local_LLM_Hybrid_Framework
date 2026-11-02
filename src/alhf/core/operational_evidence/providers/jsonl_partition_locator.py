# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Locates JSONL partitions used by the local
# ALHF Operational Evidence provider.
#
# Responsibilities:
# - Discover valid Operational Evidence JSONL partitions.
# - Preserve deterministic partition ordering.
# - Ignore unrelated or malformed filenames.
# - Keep physical partition discovery separate from repository queries.
# - Validate provider directory and file-prefix configuration.
#
# Must Not:
# - Read JSONL record contents.
# - Decode Operational Evidence records.
# - Perform repository queries.
# - Persist Operational Evidence.
# - Perform failure analysis or root-cause analysis.
# - Contain RAG or Knowledge-specific semantics.
# - Implement retention, rotation, or archival behavior.
# - Infer evidence completeness from partition presence.
#
# Architectural Position:
# - Local JSONL provider partition-discovery component.
# - Used below the JSONL repository implementation.
# - Independent from record decoding and physical line reading.
#
# Future Extensibility:
# - Derived query indexes can reduce broad partition discovery later.
# - Partition manifests can be introduced without changing repository
#   consumers.
# - Alternative providers can implement their own discovery mechanisms.

from __future__ import annotations

from pathlib import Path


class JsonlPartitionLocator:
    """Locate valid Operational Evidence JSONL partitions."""

    _FILE_SUFFIX = ".jsonl"
    _DEFAULT_FILE_PREFIX = "operational_evidence"

    def __init__(
        self,
        directory: str | Path,
        *,
        file_prefix: str = _DEFAULT_FILE_PREFIX,
    ) -> None:
        self._directory = self._validate_directory(
            directory=directory,
        )
        self._file_prefix = self._normalize_required_text(
            value=file_prefix,
            field_name="file_prefix",
        )

    def locate(self) -> tuple[Path, ...]:
        """
        Return valid JSONL partitions in ascending partition order.

        A missing provider directory represents an empty local evidence
        repository and therefore returns an empty tuple.
        """

        if not self._directory.exists():
            return ()

        if not self._directory.is_dir():
            raise NotADirectoryError(
                "Operational Evidence location is not a directory"
            )

        partitions: list[tuple[int, Path]] = []

        pattern = (
            f"{self._file_prefix}-*"
            f"{self._FILE_SUFFIX}"
        )

        for path in self._directory.glob(
            pattern,
        ):
            if not path.is_file():
                continue

            partition_number = self._extract_partition_number(
                path=path,
            )

            if partition_number is None:
                continue

            partitions.append(
                (
                    partition_number,
                    path,
                )
            )

        partitions.sort(
            key=lambda item: item[0],
        )

        return tuple(
            path
            for _, path in partitions
        )

    def _extract_partition_number(
        self,
        *,
        path: Path,
    ) -> int | None:
        """Extract a valid positive partition number."""

        filename = path.name
        expected_prefix = f"{self._file_prefix}-"

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

    @staticmethod
    def _validate_directory(
        *,
        directory: str | Path,
    ) -> Path:
        """Validate the configured provider directory."""

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
    def _normalize_required_text(
        *,
        value: str,
        field_name: str,
    ) -> str:
        """Validate and normalize one required text value."""

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
