# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides deterministic bounded Context packing for ALHF RAG V1.
#
# Problem Solved:
# Governed Evidence must be assembled into consumable Context while
# preserving order, provenance, deterministic identity, and an explicit
# execution-size boundary.
#
# Responsibilities:
# - Accept an incremental Evidence stream.
# - Preserve Evidence ordering.
# - Validate Knowledge scope continuity.
# - Accept text Evidence for the V1 vertical slice.
# - Enforce the configured byte boundary.
# - Preserve included Evidence references.
# - Produce deterministic KnowledgeContext identity.
#
# Must Not:
# - Perform retrieval or reranking.
# - Determine Evidence truth or sufficiency.
# - Partially truncate individual Evidence items.
# - Generate prompts or answers.
# - Implement token budgeting or model routing.
# - Implement adaptive Context Intelligence.
# - Treat Context as durable memory.
# - Depend on external RAG frameworks.
#
# Architectural Position:
# - Concrete V1 implementation of ContextPacker.
# - Converts ordered governed Evidence into bounded KnowledgeContext.
# - Keeps downstream consumers independent from packing mechanics.
#
# Reuse Value:
# - V1 deterministic Standard RAG.
# - Local-first E2E validation.
# - Evidence-backed LLM and agent consumers.
# - Production failure analysis through preserved Evidence references.
#
# Future Extensibility:
# - Token-aware packers can implement ContextPacker later.
# - Evidence prioritization and deduplication can evolve independently.
# - Context Intelligence can dynamically choose packing strategies.
# - Multimodal packers can coexist through governed evolution.

from __future__ import annotations

import hashlib
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


class DeterministicContextPacker(ContextPacker):
    """Pack ordered text Evidence deterministically within a byte limit."""

    _PACKER_REF = "deterministic-context-packer"
    _PACKER_VERSION = "1.0"
    _SEPARATOR = b"\n\n"

    @property
    def packer_ref(self) -> str:
        return self._PACKER_REF

    @property
    def packer_version(self) -> str:
        return self._PACKER_VERSION

    def pack(
        self,
        *,
        evidence: Iterator[EvidenceItem],
        knowledge_scope_ref: str,
        max_bytes: int,
    ) -> KnowledgeContext:
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

        evidence_refs = []
        content_parts = []
        size_bytes = 0

        for item in evidence:
            self._validate_evidence(
                item=item,
                knowledge_scope_ref=scope,
            )

            separator_size = (
                len(self._SEPARATOR)
                if content_parts
                else 0
            )
            required_bytes = (
                separator_size
                + item.size_bytes
            )

            if size_bytes + required_bytes > max_bytes:
                break

            if content_parts:
                content_parts.append(
                    self._SEPARATOR
                )
                size_bytes += separator_size

            content_parts.append(
                item.content
            )
            size_bytes += item.size_bytes
            evidence_refs.append(
                item.evidence_id
            )

        content = b"".join(
            content_parts
        )
        refs = tuple(
            evidence_refs
        )

        return KnowledgeContext(
            context_id=self._context_id(
                scope=scope,
                evidence_refs=refs,
                content=content,
            ),
            knowledge_scope_ref=scope,
            evidence_refs=refs,
            content=content,
            media_type="text/plain",
            strategy_ref=self.packer_ref,
            strategy_version=self.packer_version,
        )

    @staticmethod
    def _validate_evidence(
        *,
        item: EvidenceItem,
        knowledge_scope_ref: str,
    ) -> None:
        if not isinstance(
            item,
            EvidenceItem,
        ):
            raise TypeError(
                "evidence must yield EvidenceItem"
            )

        if item.knowledge_scope_ref != knowledge_scope_ref:
            raise ValueError(
                "Evidence knowledge_scope_ref must match Context scope"
            )

        if item.media_type != "text/plain":
            raise ValueError(
                "DeterministicContextPacker requires "
                "text/plain Evidence"
            )

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

    def _context_id(
        self,
        *,
        scope: str,
        evidence_refs: tuple[str, ...],
        content: bytes,
    ) -> str:
        material = b"|".join(
            (
                scope.encode("utf-8"),
                ",".join(evidence_refs).encode("utf-8"),
                content,
                self.packer_ref.encode("utf-8"),
                self.packer_version.encode("utf-8"),
            )
        )

        digest = hashlib.sha256(
            material
        ).hexdigest()

        return f"context:{digest}"

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
