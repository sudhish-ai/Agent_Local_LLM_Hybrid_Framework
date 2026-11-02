# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides provider-neutral Context-packing orchestration for ALHF RAG V1.
#
# Problem Solved:
# Evidence must be converted into bounded Knowledge Context through a
# configured ContextPacker while common orchestration protects execution
# limits and output integrity.
#
# Responsibilities:
# - Accept an incremental Evidence stream.
# - Validate the target Knowledge scope.
# - Validate the explicit byte boundary.
# - Delegate packing to the configured ContextPacker.
# - Validate KnowledgeContext output.
# - Validate Knowledge scope continuity.
# - Enforce the requested Context size boundary.
#
# Must Not:
# - Implement Evidence selection or packing algorithms.
# - Perform retrieval or reranking.
# - Determine Evidence truth or sufficiency.
# - Generate prompts or answers.
# - Implement token budgeting or model routing.
# - Implement adaptive Context Intelligence.
# - Treat Context as durable memory.
# - Depend on external RAG frameworks.
#
# Architectural Position:
# - Common orchestration boundary for Context packing.
# - Separates Context policies from concrete packing implementations.
# - Protects bounded execution before downstream consumption.
#
# Reuse Value:
# - V1 deterministic Standard RAG.
# - Local and cloud downstream consumers.
# - Evidence-backed agents and workflows.
# - Future GraphRAG and Agentic RAG.
#
# Future Extensibility:
# - Token-aware packers can replace the V1 implementation.
# - Context Intelligence can select packing strategies above this layer.
# - Token Budget Manager can provide externally governed limits.
# - Multimodal packing can evolve behind ContextPacker.

from __future__ import annotations

from collections.abc import Iterator

from alhf.rag.context_packing.contracts.knowledge_context import (
    KnowledgeContext,
)
from alhf.rag.context_packing.interfaces.context_packer import (
    ContextPacker,
)
from alhf.rag.evidence.contracts.evidence_item import (
    EvidenceItem,
)


class ContextPackingService:
    """Provider-neutral orchestration for bounded Context packing."""

    def __init__(
        self,
        *,
        packer: ContextPacker,
    ) -> None:
        if not isinstance(
            packer,
            ContextPacker,
        ):
            raise TypeError(
                "packer must be an instance of ContextPacker"
            )

        self._packer = packer

    def pack(
        self,
        *,
        evidence: Iterator[EvidenceItem],
        knowledge_scope_ref: str,
        max_bytes: int,
    ) -> KnowledgeContext:
        """Pack governed Evidence into one bounded Knowledge Context."""

        if not isinstance(
            evidence,
            Iterator,
        ):
            raise TypeError(
                "evidence must be an Iterator"
            )

        scope = self._required_text(
            value=knowledge_scope_ref,
            field_name="knowledge_scope_ref",
        )
        self._validate_max_bytes(
            max_bytes
        )

        context = self._packer.pack(
            evidence=evidence,
            knowledge_scope_ref=scope,
            max_bytes=max_bytes,
        )

        if not isinstance(
            context,
            KnowledgeContext,
        ):
            raise TypeError(
                "packer must return KnowledgeContext"
            )

        if context.knowledge_scope_ref != scope:
            raise ValueError(
                "KnowledgeContext scope must match request"
            )

        if context.size_bytes > max_bytes:
            raise ValueError(
                "KnowledgeContext exceeds max_bytes"
            )

        return context

    @staticmethod
    def _validate_max_bytes(
        max_bytes: int,
    ) -> None:
        if isinstance(
            max_bytes,
            bool,
        ) or not isinstance(
            max_bytes,
            int,
        ):
            raise TypeError(
                "max_bytes must be an int"
            )

        if max_bytes <= 0:
            raise ValueError(
                "max_bytes must be greater than zero"
            )

    @staticmethod
    def _required_text(
        *,
        value: str,
        field_name: str,
    ) -> str:
        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                f"{field_name} must be a string"
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                f"{field_name} cannot be empty"
            )

        return normalized
