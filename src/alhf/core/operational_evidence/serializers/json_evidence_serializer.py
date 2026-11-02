# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides deterministic JSON serialization for universal
# ALHF Operational Evidence records.
#
# Problem Solved:
# Operational Evidence providers require a stable serialized
# representation without coupling the universal evidence contracts
# to JSON, JSONL, filesystems, databases, or provider-specific storage.
#
# Responsibilities:
# - Convert OperationalEvidenceRecord instances to JSON-compatible data.
# - Serialize OperationalEvidenceRecord instances to deterministic JSON.
# - Recursively serialize supported immutable Operational Evidence
#   contract values.
# - Serialize enums using their stable values.
# - Serialize datetime values using ISO 8601.
# - Preserve tuple ordering when producing JSON arrays.
# - Reject unsupported values explicitly.
#
# Must Not:
# - Persist Operational Evidence.
# - Write JSONL files.
# - Read Operational Evidence from storage.
# - Generate identifiers.
# - Mutate Operational Evidence records.
# - Perform failure analysis or root-cause analysis.
# - Contain RAG or Knowledge-specific semantics.
# - Expose physical storage locations.
# - Perform buffering, batching, rotation, or retention.
# - Silently coerce unsupported objects into strings.
#
# Architectural Position:
# - Universal ALHF Operational Evidence serializer.
# - Boundary between validated evidence contracts and JSON-based
#   persistence providers.
# - Independent from physical persistence technology.
#
# Reuse Value:
# - Local JSONL Operational Evidence provider.
# - Diagnostic export where JSON representation is appropriate.
# - Future JSON-compatible persistence providers.
# - Deterministic Operational Evidence testing.
#
# Future Extensibility:
# - Deserialization remains a separate responsibility.
# - JSONL framing remains a persistence-provider responsibility.
# - Alternative serialization formats can be added independently.
# - Subsystem-specific governed contracts can reuse the recursive
#   serialization rules when explicitly supported.

from __future__ import annotations

import json
from dataclasses import fields, is_dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Mapping

from alhf.core.operational_evidence.contracts.record import (
    OperationalEvidenceRecord,
)


class JsonEvidenceSerializer:
    """
    Deterministic JSON serializer for ALHF Operational Evidence.

    The serializer accepts a validated OperationalEvidenceRecord and
    converts supported contract values into JSON-compatible primitives.

    Physical persistence and JSONL framing are deliberately outside this
    serializer.
    """

    @classmethod
    def to_dict(
        cls,
        record: OperationalEvidenceRecord,
    ) -> dict[str, Any]:
        """
        Convert one Operational Evidence record to JSON-compatible data.
        """

        if not isinstance(
            record,
            OperationalEvidenceRecord,
        ):
            raise TypeError(
                "record must be an instance of OperationalEvidenceRecord"
            )

        serialized = cls._serialize_value(
            record,
        )

        if not isinstance(
            serialized,
            dict,
        ):
            raise TypeError(
                "serialized OperationalEvidenceRecord must be a dict"
            )

        return serialized

    @classmethod
    def to_json(
        cls,
        record: OperationalEvidenceRecord,
    ) -> str:
        """
        Serialize one Operational Evidence record to deterministic JSON.
        """

        return json.dumps(
            cls.to_dict(record),
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )

    @classmethod
    def _serialize_value(
        cls,
        value: object,
    ) -> Any:
        """Recursively convert supported values to JSON-compatible data."""

        if value is None:
            return None

        if isinstance(
            value,
            Enum,
        ):
            return cls._serialize_value(
                value.value,
            )

        if isinstance(
            value,
            datetime,
        ):
            return value.isoformat()

        if is_dataclass(value) and not isinstance(
            value,
            type,
        ):
            return {
                dataclass_field.name: cls._serialize_value(
                    getattr(
                        value,
                        dataclass_field.name,
                    )
                )
                for dataclass_field in fields(value)
            }

        if isinstance(
            value,
            Mapping,
        ):
            return cls._serialize_mapping(
                value,
            )

        if isinstance(
            value,
            tuple,
        ):
            return [
                cls._serialize_value(item)
                for item in value
            ]

        if isinstance(
            value,
            list,
        ):
            return [
                cls._serialize_value(item)
                for item in value
            ]

        if isinstance(
            value,
            bool,
        ):
            return value

        if isinstance(
            value,
            (str, int, float),
        ):
            return value

        raise TypeError(
            "unsupported value type for Operational Evidence "
            f"JSON serialization: {type(value).__name__}"
        )

    @classmethod
    def _serialize_mapping(
        cls,
        value: Mapping[object, object],
    ) -> dict[str, Any]:
        """Serialize a mapping with validated string keys."""

        serialized: dict[str, Any] = {}

        for key, item in value.items():
            if not isinstance(
                key,
                str,
            ):
                raise TypeError(
                    "Operational Evidence JSON mapping keys "
                    "must be strings"
                )

            serialized[key] = cls._serialize_value(
                item,
            )

        return serialized
