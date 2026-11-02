# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the provider-neutral result of one bounded Knowledge
# acquisition request in the ALHF Knowledge Foundation.
#
# Problem Solved:
# Acquisition orchestration needs an explicit result describing whether
# bounded acquisition completed, whether more resources remain, and which
# continuation or checkpoint state should govern subsequent work.
#
# Responsibilities:
# - Represent bounded acquisition completion semantics.
# - Preserve the source identity associated with the acquisition.
# - Report the number of resources produced by this request.
# - Preserve optional continuation and checkpoint references.
# - Preserve whether additional acquisition work remains.
# - Keep acquired resources outside the result contract.
#
# Must Not:
# - Contain acquired resource collections.
# - Contain Knowledge content.
# - Store provider-specific cursors or pagination tokens.
# - Store credentials, URLs, paths, or connection information.
# - Perform acquisition or synchronization.
# - Perform parsing, chunking, indexing, or retrieval.
# - Contain Standard, Graph, or Agentic RAG behavior.
# - Contain arbitrary metadata dictionaries.
#
# Architectural Position:
# - Provider-neutral bounded acquisition-result contract.
# - Complements AcquisitionRequest without duplicating acquired content.
# - Supports future resumable and incremental ingestion workflows.
#
# Future Extensibility:
# - Provider cursor state remains hidden behind governed references.
# - Synchronization state can evolve independently.
# - Operational Evidence captures execution details separately.
# - Large-scale acquisition remains bounded across repeated requests.

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class AcquisitionStatus(str, Enum):
    """Provider-neutral result state of bounded acquisition."""

    COMPLETED = "COMPLETED"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"


@dataclass(frozen=True, slots=True)
class AcquisitionResult:
    """
    Immutable result of one bounded acquisition request.

    source_ref:
        Stable logical Knowledge source identity.

    status:
        Provider-neutral acquisition outcome.

    acquired_count:
        Number of resources produced during this bounded request.

    has_more:
        Indicates whether additional acquisition work remains.

    continuation_ref:
        Optional governed reference used to continue acquisition.

    checkpoint_ref:
        Optional governed synchronization checkpoint reference.
    """

    source_ref: str
    status: AcquisitionStatus
    acquired_count: int
    has_more: bool
    continuation_ref: str | None = None
    checkpoint_ref: str | None = None

    def __post_init__(self) -> None:
        source_ref = self._required_text(
            value=self.source_ref,
            field_name="source_ref",
        )

        if not isinstance(
            self.status,
            AcquisitionStatus,
        ):
            raise TypeError(
                "status must be an instance of AcquisitionStatus"
            )

        acquired_count = self._non_negative_int(
            value=self.acquired_count,
            field_name="acquired_count",
        )

        if not isinstance(
            self.has_more,
            bool,
        ):
            raise TypeError(
                "has_more must be a bool"
            )

        continuation_ref = self._optional_text(
            value=self.continuation_ref,
            field_name="continuation_ref",
        )
        checkpoint_ref = self._optional_text(
            value=self.checkpoint_ref,
            field_name="checkpoint_ref",
        )

        self._validate_state(
            status=self.status,
            has_more=self.has_more,
            continuation_ref=continuation_ref,
        )

        object.__setattr__(self, "source_ref", source_ref)
        object.__setattr__(
            self,
            "acquired_count",
            acquired_count,
        )
        object.__setattr__(
            self,
            "continuation_ref",
            continuation_ref,
        )
        object.__setattr__(
            self,
            "checkpoint_ref",
            checkpoint_ref,
        )

    @staticmethod
    def _validate_state(
        *,
        status: AcquisitionStatus,
        has_more: bool,
        continuation_ref: str | None,
    ) -> None:
        """Validate bounded acquisition state consistency."""

        if status == AcquisitionStatus.COMPLETED and has_more:
            raise ValueError(
                "completed acquisition cannot have additional work"
            )

        if status == AcquisitionStatus.FAILED and has_more:
            raise ValueError(
                "failed acquisition cannot declare additional work"
            )

        if has_more and continuation_ref is None:
            raise ValueError(
                "additional acquisition work requires continuation_ref"
            )

        if not has_more and continuation_ref is not None:
            raise ValueError(
                "continuation_ref requires additional acquisition work"
            )

    @staticmethod
    def _non_negative_int(
        *,
        value: int,
        field_name: str,
    ) -> int:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(
                f"{field_name} must be an int"
            )

        if value < 0:
            raise ValueError(
                f"{field_name} cannot be negative"
            )

        return value

    @staticmethod
    def _required_text(
        *,
        value: str,
        field_name: str,
    ) -> str:
        if not isinstance(value, str):
            raise TypeError(
                f"{field_name} must be a string"
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                f"{field_name} cannot be empty"
            )

        return normalized

    @staticmethod
    def _optional_text(
        *,
        value: str | None,
        field_name: str,
    ) -> str | None:
        if value is None:
            return None

        if not isinstance(value, str):
            raise TypeError(
                f"{field_name} must be a string or None"
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                f"{field_name} cannot be empty when provided"
            )

        return normalized
