# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh

"""Structured pipeline result contract for ALHF.

Every non-fatal pipeline stage should return PipelineResult instead of
returning raw values or leaking operational exceptions upward.

This keeps ingestion, retrieval, generation, security validation, telemetry,
audit reporting, MCP execution, local LLM calls, and agent orchestration
consistent across the framework.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Generic, Mapping, Optional, Tuple, TypeVar

from alhf.core.status import ErrorSeverity, PipelineStatus

T = TypeVar("T")


@dataclass(frozen=True)
class PipelineResult(Generic[T]):
    """Standard result object returned by pipeline components.

    This object is intentionally immutable at the top level. Metadata and
    metrics are defensively copied and wrapped in MappingProxyType to reduce
    accidental mutation across pipeline stages.

    Attributes:
        status: Standard pipeline status.
        data: Optional successful result payload.
        error_code: Stable machine-readable error or reason code.
        error_message: Human-readable error or reason message.
        retryable: Whether retrying may succeed.
        severity: Severity level for failures or warnings.
        warnings: Non-fatal warnings.
        metadata: Additional structured context.
        metrics: Numeric metrics associated with the operation.
        trace_id: Optional trace/correlation identifier.
        stage_name: Name of the pipeline stage producing this result.
    """

    status: PipelineStatus
    data: Optional[T] = None

    error_code: Optional[str] = None
    error_message: Optional[str] = None
    retryable: bool = False
    severity: ErrorSeverity = ErrorSeverity.INFO

    warnings: Tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)
    metrics: Mapping[str, float] = field(default_factory=dict)

    trace_id: Optional[str] = None
    stage_name: Optional[str] = None

    def __post_init__(self) -> None:
        self._validate()
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))
        object.__setattr__(self, "metrics", MappingProxyType(dict(self.metrics)))
        object.__setattr__(self, "warnings", tuple(self.warnings))

    @property
    def is_success(self) -> bool:
        """Return True when the stage completed successfully."""

        return self.status == PipelineStatus.SUCCESS

    @property
    def is_failure(self) -> bool:
        """Return True when the result represents a failure or blocked action."""

        return self.status in {
            PipelineStatus.FAILED_RETRYABLE,
            PipelineStatus.FAILED_NON_RETRYABLE,
            PipelineStatus.QUARANTINED,
            PipelineStatus.ACCESS_DENIED,
        }

    @property
    def is_skipped(self) -> bool:
        """Return True when the item was intentionally skipped."""

        return self.status == PipelineStatus.SKIPPED

    def require_success(self) -> T:
        """Return data if successful, otherwise raise RuntimeError.

        This should only be used at strict boundaries where continuation is
        not possible. Most pipeline code should inspect status and continue
        gracefully.
        """

        if not self.is_success:
            raise RuntimeError(
                "PipelineResult is not successful: "
                f"status={self.status.value}, "
                f"error_code={self.error_code}, "
                f"error_message={self.error_message}"
            )

        if self.data is None:
            raise RuntimeError("PipelineResult was successful but data is None")

        return self.data

    @classmethod
    def success(
        cls,
        data: T,
        *,
        warnings: Tuple[str, ...] = (),
        metadata: Optional[Mapping[str, Any]] = None,
        metrics: Optional[Mapping[str, float]] = None,
        trace_id: Optional[str] = None,
        stage_name: Optional[str] = None,
    ) -> "PipelineResult[T]":
        """Create a successful result."""

        return cls(
            status=PipelineStatus.SUCCESS,
            data=data,
            warnings=warnings,
            metadata=metadata or {},
            metrics=metrics or {},
            trace_id=trace_id,
            stage_name=stage_name,
            severity=ErrorSeverity.INFO,
        )

    @classmethod
    def skipped(
        cls,
        *,
        reason_code: str,
        reason_message: str,
        metadata: Optional[Mapping[str, Any]] = None,
        metrics: Optional[Mapping[str, float]] = None,
        trace_id: Optional[str] = None,
        stage_name: Optional[str] = None,
    ) -> "PipelineResult[None]":
        """Create a skipped result."""

        return cls(
            status=PipelineStatus.SKIPPED,
            data=None,
            error_code=reason_code,
            error_message=reason_message,
            retryable=False,
            severity=ErrorSeverity.INFO,
            metadata=metadata or {},
            metrics=metrics or {},
            trace_id=trace_id,
            stage_name=stage_name,
        )

    @classmethod
    def failed_retryable(
        cls,
        *,
        error_code: str,
        error_message: str,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        metadata: Optional[Mapping[str, Any]] = None,
        metrics: Optional[Mapping[str, float]] = None,
        trace_id: Optional[str] = None,
        stage_name: Optional[str] = None,
    ) -> "PipelineResult[None]":
        """Create a retryable failure result."""

        return cls(
            status=PipelineStatus.FAILED_RETRYABLE,
            data=None,
            error_code=error_code,
            error_message=error_message,
            retryable=True,
            severity=severity,
            metadata=metadata or {},
            metrics=metrics or {},
            trace_id=trace_id,
            stage_name=stage_name,
        )

    @classmethod
    def failed_non_retryable(
        cls,
        *,
        error_code: str,
        error_message: str,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        metadata: Optional[Mapping[str, Any]] = None,
        metrics: Optional[Mapping[str, float]] = None,
        trace_id: Optional[str] = None,
        stage_name: Optional[str] = None,
    ) -> "PipelineResult[None]":
        """Create a non-retryable failure result."""

        return cls(
            status=PipelineStatus.FAILED_NON_RETRYABLE,
            data=None,
            error_code=error_code,
            error_message=error_message,
            retryable=False,
            severity=severity,
            metadata=metadata or {},
            metrics=metrics or {},
            trace_id=trace_id,
            stage_name=stage_name,
        )

    @classmethod
    def quarantined(
        cls,
        *,
        error_code: str,
        error_message: str,
        metadata: Optional[Mapping[str, Any]] = None,
        metrics: Optional[Mapping[str, float]] = None,
        trace_id: Optional[str] = None,
        stage_name: Optional[str] = None,
    ) -> "PipelineResult[None]":
        """Create a quarantined result requiring manual review."""

        return cls(
            status=PipelineStatus.QUARANTINED,
            data=None,
            error_code=error_code,
            error_message=error_message,
            retryable=False,
            severity=ErrorSeverity.CRITICAL,
            metadata=metadata or {},
            metrics=metrics or {},
            trace_id=trace_id,
            stage_name=stage_name,
        )

    @classmethod
    def access_denied(
        cls,
        *,
        error_code: str = "ACCESS_DENIED",
        error_message: str = "Access denied by policy",
        metadata: Optional[Mapping[str, Any]] = None,
        metrics: Optional[Mapping[str, float]] = None,
        trace_id: Optional[str] = None,
        stage_name: Optional[str] = None,
    ) -> "PipelineResult[None]":
        """Create an access-denied result."""

        return cls(
            status=PipelineStatus.ACCESS_DENIED,
            data=None,
            error_code=error_code,
            error_message=error_message,
            retryable=False,
            severity=ErrorSeverity.CRITICAL,
            metadata=metadata or {},
            metrics=metrics or {},
            trace_id=trace_id,
            stage_name=stage_name,
        )

    def _validate(self) -> None:
        """Validate internal consistency of the result object."""

        if not isinstance(self.status, PipelineStatus):
            raise TypeError("status must be an instance of PipelineStatus")

        if not isinstance(self.severity, ErrorSeverity):
            raise TypeError("severity must be an instance of ErrorSeverity")

        if self.status == PipelineStatus.SUCCESS:
            if self.error_code is not None or self.error_message is not None:
                raise ValueError("SUCCESS result cannot contain error_code or error_message")
            if self.retryable:
                raise ValueError("SUCCESS result cannot be retryable")

        if self.status == PipelineStatus.FAILED_RETRYABLE and not self.retryable:
            raise ValueError("FAILED_RETRYABLE result must have retryable=True")

        if self.status in {
            PipelineStatus.FAILED_NON_RETRYABLE,
            PipelineStatus.QUARANTINED,
            PipelineStatus.ACCESS_DENIED,
        } and self.retryable:
            raise ValueError(f"{self.status.value} result cannot be retryable")

        if self.is_failure and not self.error_code:
            raise ValueError(f"{self.status.value} result must include error_code")

        if self.is_failure and not self.error_message:
            raise ValueError(f"{self.status.value} result must include error_message")

        if self.status == PipelineStatus.SKIPPED and not self.error_code:
            raise ValueError("SKIPPED result must include reason error_code")

        if self.status == PipelineStatus.SKIPPED and not self.error_message:
            raise ValueError("SKIPPED result must include reason error_message")
