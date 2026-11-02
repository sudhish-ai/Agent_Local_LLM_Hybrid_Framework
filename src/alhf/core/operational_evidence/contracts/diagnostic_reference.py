# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the universal diagnostic-reference contract used by the
# ALHF Operational Evidence Foundation.
#
# Problem Solved:
# Operational Evidence must remain compact, secure, and storage-neutral
# while still allowing authorized failure analysis to locate separately
# governed diagnostic detail when deeper investigation is required.
#
# Large or sensitive diagnostics must not be embedded directly into every
# Operational Evidence record merely for debugging convenience.
#
# Responsibilities:
# - Identify one separately governed diagnostic artifact.
# - Describe the semantic kind of diagnostic artifact referenced.
# - Preserve the producer responsible for the diagnostic artifact.
# - Preserve an optional media type for interpreting diagnostic content.
# - Normalize and validate diagnostic-reference values.
# - Provide immutable and storage-independent reference semantics.
#
# Must Not:
# - Contain diagnostic artifact content.
# - Contain exception objects or stack traces.
# - Contain credentials, secrets, or authentication tokens.
# - Define diagnostic-artifact storage locations.
# - Contain filesystem paths, URLs, database keys, or provider locators.
# - Determine diagnostic-artifact authorization.
# - Determine diagnostic-artifact retention.
# - Perform redaction or sanitization.
# - Contain RAG or Knowledge-specific semantics.
# - Contain persistence, JSON, or JSONL behavior.
# - Contain arbitrary metadata or payload dictionaries.
#
# Architectural Position:
# - Universal ALHF Operational Evidence contract.
# - Keeps heavy or sensitive diagnostic detail outside primary evidence
#   records while preserving a governed reference to that detail.
# - Independent from persistence providers and diagnostic storage.
#
# Reuse Value:
# - Knowledge Foundation operational diagnostics.
# - Multi-agent operational diagnostics.
# - V3 operational diagnostics.
# - Failure analysis and RCA.
# - Provider-failure investigation.
# - Post-remediation validation.
#
# Future Extensibility:
# - Diagnostic artifact storage remains provider-specific.
# - Authorization and classification remain separate responsibilities.
# - Additional diagnostic kinds may be introduced when they represent
#   genuinely universal diagnostic semantics.
# - Content integrity verification remains a separate responsibility.

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class DiagnosticKind(str, Enum):
    """Universal diagnostic artifact classifications."""

    ERROR_DETAIL = "ERROR_DETAIL"
    STACK_TRACE = "STACK_TRACE"
    INPUT_SAMPLE = "INPUT_SAMPLE"
    OUTPUT_SAMPLE = "OUTPUT_SAMPLE"
    PROVIDER_DETAIL = "PROVIDER_DETAIL"
    VALIDATION_DETAIL = "VALIDATION_DETAIL"
    PERFORMANCE_DETAIL = "PERFORMANCE_DETAIL"
    OTHER = "OTHER"


@dataclass(frozen=True, slots=True)
class DiagnosticReference:
    """
    Immutable reference to a separately governed diagnostic artifact.

    diagnostic_id:
        Stable logical identity of the diagnostic artifact.

    diagnostic_kind:
        Universal classification describing the diagnostic artifact.

    producer:
        Stable identity of the ALHF component that produced the artifact.

    media_type:
        Optional media type describing the diagnostic artifact format.

    This contract identifies diagnostic information without containing the
    diagnostic content or exposing its physical storage location.
    """

    diagnostic_id: str
    diagnostic_kind: DiagnosticKind
    producer: str
    media_type: str | None = None

    def __post_init__(self) -> None:
        diagnostic_id = self._normalize_required_text(
            value=self.diagnostic_id,
            field_name="diagnostic_id",
        )
        producer = self._normalize_required_text(
            value=self.producer,
            field_name="producer",
        )
        media_type = self._normalize_optional_text(
            value=self.media_type,
            field_name="media_type",
        )

        if not isinstance(
            self.diagnostic_kind,
            DiagnosticKind,
        ):
            raise TypeError(
                "diagnostic_kind must be an instance of DiagnosticKind"
            )

        object.__setattr__(
            self,
            "diagnostic_id",
            diagnostic_id,
        )
        object.__setattr__(
            self,
            "producer",
            producer,
        )
        object.__setattr__(
            self,
            "media_type",
            media_type,
        )

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
