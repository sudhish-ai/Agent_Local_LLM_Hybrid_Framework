# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the universal schema identity contract used by the
# ALHF Operational Evidence Foundation.
#
# Problem Solved:
# Operational evidence can remain useful for failure analysis, historical
# comparison, recovery, and validation only when consumers can determine
# which schema semantics were used to create each record.
#
# Schema identity must remain independent from storage technology,
# serialization format, provider implementation, and ALHF product version.
#
# Responsibilities:
# - Identify the semantic schema used by operational evidence.
# - Preserve an explicit schema version.
# - Normalize and validate schema identity values.
# - Provide immutable schema identity semantics.
# - Support historical interpretation and schema evolution.
#
# Must Not:
# - Represent the ALHF product version.
# - Define schema migration logic.
# - Define schema compatibility rules.
# - Define serialization format.
# - Contain JSON or JSONL behavior.
# - Contain provider-specific schema identifiers.
# - Contain RAG or Knowledge-specific semantics.
# - Perform persistence or query operations.
# - Contain arbitrary metadata or payload dictionaries.
#
# Architectural Position:
# - Universal ALHF Operational Evidence contract.
# - Provides explicit semantic version identity for evidence records.
# - Independent from persistence providers and physical storage layout.
#
# Reuse Value:
# - Knowledge Foundation operational evidence.
# - Multi-agent operational evidence.
# - V3 operational evidence.
# - Historical failure analysis and RCA.
# - Predictive reliability analysis.
# - Post-remediation validation.
#
# Future Extensibility:
# - Compatibility evaluation remains a separate responsibility.
# - Schema migration remains a separate responsibility.
# - Subsystem extension schemas may use their own schema identities.
# - Storage-provider migration does not change semantic schema identity.

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SchemaIdentity:
    """
    Immutable semantic identity for an Operational Evidence schema.

    schema_id:
        Stable identifier describing the semantic schema.

    schema_version:
        Explicit version describing which revision of the semantic schema
        was used.

    Schema identity is deliberately independent from ALHF product versions,
    serialization formats, persistence providers, and storage locations.
    """

    schema_id: str
    schema_version: str

    def __post_init__(self) -> None:
        schema_id = self._normalize_required_text(
            value=self.schema_id,
            field_name="schema_id",
        )
        schema_version = self._normalize_required_text(
            value=self.schema_version,
            field_name="schema_version",
        )

        object.__setattr__(
            self,
            "schema_id",
            schema_id,
        )
        object.__setattr__(
            self,
            "schema_version",
            schema_version,
        )

    @staticmethod
    def _normalize_required_text(
        *,
        value: str,
        field_name: str,
    ) -> str:
        """Validate and normalize a required schema identity value."""

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
