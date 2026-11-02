# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines provider-neutral capability declarations for ALHF Knowledge
# source acquisition adapters.
#
# Problem Solved:
# Knowledge source adapters may expose different acquisition behaviors.
# ALHF must understand those differences explicitly instead of assuming
# that every adapter supports synchronization, continuation, or
# incremental change processing.
#
# Responsibilities:
# - Declare synchronization capability.
# - Declare continuation capability.
# - Declare incremental-change capability.
# - Declare deletion-detection capability.
# - Declare resumable-acquisition capability.
# - Provide immutable provider-neutral capability semantics.
#
# Must Not:
# - Execute acquisition.
# - Select or register adapters.
# - Contain provider names or provider-specific behavior.
# - Contain credentials or connection information.
# - Define provider-specific cursor formats.
# - Perform synchronization or change detection.
# - Perform parsing, chunking, embedding, indexing, or retrieval.
# - Contain Standard RAG, GraphRAG, or Agentic RAG behavior.
# - Contain arbitrary metadata dictionaries.
#
# Architectural Position:
# - Universal capability contract for Knowledge source adapters.
# - Allows acquisition orchestration to verify behavioral compatibility.
# - Independent from local, cloud, hybrid, and future source providers.
#
# Reuse Value:
# - Local source adapters.
# - Cloud source adapters.
# - Enterprise collaboration adapters.
# - Database and API source adapters.
# - Future plugin and capability-discovery mechanisms.
#
# Future Extensibility:
# - New universal acquisition capabilities may be added when proven by
#   implementation requirements.
# - Provider-specific capabilities remain outside this common contract.
# - Capability discovery and adapter registration remain separate.
# - Knowledge profiles may eventually use capabilities when selecting
#   compatible acquisition strategies.

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AdapterCapabilities:
    """
    Immutable acquisition capabilities of one Knowledge source adapter.

    supports_synchronization:
        Adapter can participate in synchronization workflows.

    supports_continuation:
        Adapter supports bounded acquisition continuation.

    supports_incremental_changes:
        Adapter can acquire source changes incrementally.

    supports_deletion_detection:
        Adapter can identify resources deleted from the source.

    supports_resume:
        Adapter can resume interrupted acquisition using governed state.
    """

    supports_synchronization: bool = False
    supports_continuation: bool = False
    supports_incremental_changes: bool = False
    supports_deletion_detection: bool = False
    supports_resume: bool = False

    def __post_init__(self) -> None:
        self._validate_boolean(
            value=self.supports_synchronization,
            field_name="supports_synchronization",
        )
        self._validate_boolean(
            value=self.supports_continuation,
            field_name="supports_continuation",
        )
        self._validate_boolean(
            value=self.supports_incremental_changes,
            field_name="supports_incremental_changes",
        )
        self._validate_boolean(
            value=self.supports_deletion_detection,
            field_name="supports_deletion_detection",
        )
        self._validate_boolean(
            value=self.supports_resume,
            field_name="supports_resume",
        )

        if (
            self.supports_incremental_changes
            and not self.supports_synchronization
        ):
            raise ValueError(
                "incremental changes require synchronization capability"
            )

        if (
            self.supports_deletion_detection
            and not self.supports_synchronization
        ):
            raise ValueError(
                "deletion detection requires synchronization capability"
            )

        if (
            self.supports_resume
            and not self.supports_continuation
        ):
            raise ValueError(
                "resume capability requires continuation capability"
            )

    @staticmethod
    def _validate_boolean(
        *,
        value: bool,
        field_name: str,
    ) -> None:
        """Validate one adapter capability declaration."""

        if not isinstance(value, bool):
            raise TypeError(
                f"{field_name} must be a bool"
            )
