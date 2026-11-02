# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the universal Context-packing boundary used by the ALHF
# Knowledge Foundation context-packing layer.
#
# Problem Solved:
# Governed Evidence must become bounded consumable Knowledge Context
# without coupling Evidence to LLMs, prompt frameworks, model providers,
# or a specific Context-packing implementation.
#
# Responsibilities:
# - Accept an incremental stream of governed Evidence items.
# - Accept the target Knowledge scope.
# - Enforce an explicit Context size boundary.
# - Produce one provider-neutral KnowledgeContext.
# - Expose stable packer identity and version.
# - Preserve Evidence references and ordering.
#
# Must Not:
# - Perform retrieval or reranking.
# - Determine Evidence truth or sufficiency.
# - Generate prompts or answers.
# - Implement model routing.
# - Implement token accounting.
# - Treat Context as durable memory.
# - Implement adaptive Context Intelligence.
# - Depend on external RAG or orchestration frameworks.
#
# Architectural Position:
# - Stable execution boundary between Evidence and KnowledgeContext.
# - Keeps Context construction independent from downstream consumers.
# - Provides bounded execution semantics required by production RAG.
#
# Reuse Value:
# - V1 deterministic Standard RAG.
# - Local and cloud model consumers.
# - Evidence-backed agents.
# - Future GraphRAG and Agentic RAG consumers.
#
# Future Extensibility:
# - Token-aware packers can implement this boundary later.
# - Evidence prioritization can evolve behind separate strategies.
# - Context Intelligence can select packing strategies dynamically.
# - Model-aware packing can evolve without changing Evidence contracts.
# - Multimodal packers can be introduced through governed evolution.

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator

from alhf.rag.context_packing.contracts.knowledge_context import (
    KnowledgeContext,
)
from alhf.rag.evidence.contracts.evidence_item import (
    EvidenceItem,
)


class ContextPacker(ABC):
    """Universal provider-neutral Context-packing boundary."""

    @property
    @abstractmethod
    def packer_ref(self) -> str:
        """Return the stable logical Context-packer identifier."""

        raise NotImplementedError

    @property
    @abstractmethod
    def packer_version(self) -> str:
        """Return the stable Context-packer behavior version."""

        raise NotImplementedError

    @abstractmethod
    def pack(
        self,
        *,
        evidence: Iterator[EvidenceItem],
        knowledge_scope_ref: str,
        max_bytes: int,
    ) -> KnowledgeContext:
        """
        Pack governed Evidence into one bounded Knowledge Context.

        Evidence ordering is significant and must be preserved by
        deterministic V1 implementations.

        The max_bytes parameter is an execution boundary rather than
        model-specific token budgeting.
        """

        raise NotImplementedError
