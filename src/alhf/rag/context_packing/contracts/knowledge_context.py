# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the provider-neutral Knowledge Context produced from governed
# Evidence by the ALHF Knowledge Foundation context-packing layer.
#
# Problem Solved:
# Evidence must be assembled into bounded consumable Context without
# losing provenance or coupling Knowledge to an LLM, agent, prompt
# framework, generation provider, or model-specific representation.
#
# Responsibilities:
# - Identify one constructed Knowledge Context.
# - Preserve the originating Knowledge scope.
# - Preserve ordered Evidence references.
# - Preserve packed Context content.
# - Record Context-packing strategy identity and version.
# - Provide immutable provider-neutral Context semantics.
#
# Must Not:
# - Perform retrieval or reranking.
# - Determine Evidence truth or sufficiency.
# - Generate answers or prompts.
# - Contain model-provider-specific objects.
# - Implement token budgeting or model routing.
# - Implement adaptive Context Intelligence.
# - Treat Context as durable memory.
# - Depend on external RAG or orchestration frameworks.
#
# Architectural Position:
# - Stable boundary between governed Evidence and downstream consumers.
# - Preserves Evidence lineage after Context packing.
# - Keeps Context construction independent from model invocation.
#
# Reuse Value:
# - V1 deterministic Standard RAG.
# - Local and cloud LLM consumers.
# - Evidence-backed agents and workflows.
# - Future hybrid and Agentic RAG.
#
# Future Extensibility:
# - Token-aware packing can evolve behind this boundary.
# - Evidence prioritization and deduplication can evolve later.
# - Context Intelligence can dynamically optimize packing.
# - Token Budget Manager can govern limits externally.
# - Multimodal Context can evolve through governed contract evolution.

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class KnowledgeContext:
    """Immutable Evidence-backed Knowledge Context."""

    context_id: str
    knowledge_scope_ref: str
    evidence_refs: tuple[str, ...]
    content: bytes
    media_type: str
    strategy_ref: str
    strategy_version: str

    def __post_init__(self) -> None:
        fields = (
            "context_id",
            "knowledge_scope_ref",
            "media_type",
            "strategy_ref",
            "strategy_version",
        )

        for field_name in fields:
            normalized = self._required_text(
                value=getattr(
                    self,
                    field_name,
                ),
                field_name=field_name,
            )

            object.__setattr__(
                self,
                field_name,
                normalized,
            )

        if not isinstance(
            self.evidence_refs,
            tuple,
        ):
            raise TypeError(
                "evidence_refs must be a tuple"
            )

        normalized_refs = tuple(
            self._required_text(
                value=evidence_ref,
                field_name="evidence_ref",
            )
            for evidence_ref in self.evidence_refs
        )

        if len(normalized_refs) != len(set(normalized_refs)):
            raise ValueError(
                "evidence_refs must not contain duplicates"
            )

        object.__setattr__(
            self,
            "evidence_refs",
            normalized_refs,
        )

        if not isinstance(
            self.content,
            bytes,
        ):
            raise TypeError(
                "content must be bytes"
            )

    @property
    def size_bytes(self) -> int:
        """Return Context content size without copying it."""

        return len(
            self.content
        )

    @property
    def evidence_count(self) -> int:
        """Return the number of Evidence items represented."""

        return len(
            self.evidence_refs
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
