# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines a bounded acquisition request for the
# ALHF Knowledge Foundation ingestion plane.
#
# Problem Solved:
# Acquisition orchestration needs a provider-neutral request describing
# what logical Knowledge source to acquire and how much work may be
# performed without exposing physical provider details.
#
# Responsibilities:
# - Preserve the logical Knowledge source being acquired.
# - Preserve an explicit maximum resource count per acquisition request.
# - Preserve an optional continuation reference for resumable acquisition.
# - Preserve an optional synchronization checkpoint reference.
# - Normalize and validate bounded acquisition inputs.
# - Remain independent from concrete source providers.
#
# Must Not:
# - Store credentials, secrets, URLs, paths, or connection information.
# - Materialize acquired resources.
# - Perform acquisition.
# - Define provider-specific pagination tokens.
# - Generate source or resource identities.
# - Perform parsing, chunking, embedding, indexing, or retrieval.
# - Contain Standard, Graph, or Agentic RAG behavior.
# - Contain arbitrary metadata dictionaries.
#
# Architectural Position:
# - Provider-neutral request contract for the acquisition plane.
# - Consumed by acquisition orchestration and source adapters.
# - Explicitly bounded for large-scale Knowledge ingestion.
#
# Future Extensibility:
# - Continuation references can support resumable acquisition.
# - Synchronization checkpoints can evolve independently.
# - Provider-specific cursor state remains behind adapters.
# - Acquisition orchestration can page repeatedly without changing
#   this bounded request contract.

from __future__ import annotations

from dataclasses import dataclass

from alhf.rag.ingestion.contracts.knowledge_source import (
    KnowledgeSource,
)


@dataclass(frozen=True, slots=True)
class AcquisitionRequest:
    """
    Immutable bounded request for Knowledge source acquisition.

    source:
        Logical Knowledge source to acquire.

    max_resources:
        Maximum number of resources that may be produced for this
        acquisition request.

    continuation_ref:
        Optional provider-neutral reference used to resume a bounded
        acquisition sequence.

    checkpoint_ref:
        Optional governed reference to synchronization state from which
        acquisition should proceed.
    """

    source: KnowledgeSource
    max_resources: int
    continuation_ref: str | None = None
    checkpoint_ref: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(
            self.source,
            KnowledgeSource,
        ):
            raise TypeError(
                "source must be an instance of KnowledgeSource"
            )

        max_resources = self._positive_int(
            value=self.max_resources,
            field_name="max_resources",
        )
        continuation_ref = self._optional_text(
            value=self.continuation_ref,
            field_name="continuation_ref",
        )
        checkpoint_ref = self._optional_text(
            value=self.checkpoint_ref,
            field_name="checkpoint_ref",
        )

        object.__setattr__(
            self,
            "max_resources",
            max_resources,
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

    @property
    def source_id(self) -> str:
        """Return the logical Knowledge source identity."""

        return self.source.source_id

    @property
    def knowledge_scope_ref(self) -> str:
        """Return the governed Knowledge scope reference."""

        return self.source.knowledge_scope_ref

    @staticmethod
    def _positive_int(
        *,
        value: int,
        field_name: str,
    ) -> int:
        """Validate one positive integer bound."""

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

    @staticmethod
    def _optional_text(
        *,
        value: str | None,
        field_name: str,
    ) -> str | None:
        """Validate and normalize an optional reference."""

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
