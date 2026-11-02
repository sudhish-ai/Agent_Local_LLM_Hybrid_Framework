# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the governed internal source plan produced after ALHF interprets
# a minimal customer Knowledge source input.
#
# Problem Solved:
# The production runtime needs a stable bridge from source-only customer
# input to internal ingestion execution without exposing adapters, parsers,
# providers, indexes, or RAG modes to the customer.
#
# Responsibilities:
# - Preserve governed source and Knowledge-scope identity.
# - Preserve the selected acquisition adapter reference.
# - Preserve an optional governed source-configuration reference.
# - Declare synchronization participation.
# - Remain independent from parsing and downstream retrieval technology.
#
# Must Not:
# - Store credentials, source contents, paths, URLs, or arbitrary metadata.
# - Select parsers, derivation strategies, representations, or indexes.
# - Encode Standard RAG, GraphRAG, Agentic RAG, or deployment technology.
# - Execute acquisition or any Knowledge pipeline stage.
#
# Architectural Position:
# - Internal governed output of source interpretation.
# - Input to production ingestion composition and execution.
# - Separates the source-only customer boundary from provider mechanics.
#
# Future Extensibility:
# - Additional source technologies remain isolated behind adapters.
# - Profiles and capability intelligence can produce this same contract.
# - Source authorization remains governed independently.

from __future__ import annotations

from dataclasses import dataclass

from alhf.rag.ingestion.contracts.knowledge_source import (
    KnowledgeSource,
    KnowledgeSourceKind,
)


@dataclass(frozen=True, slots=True)
class KnowledgeSourcePlan:
    """Governed internal plan for acquiring one interpreted source."""

    source_id: str
    knowledge_scope_ref: str
    source_kind: KnowledgeSourceKind
    adapter_ref: str
    configuration_ref: str | None = None
    synchronization_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "source_id",
            "knowledge_scope_ref",
            "adapter_ref",
        ):
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
            self.source_kind,
            KnowledgeSourceKind,
        ):
            raise TypeError(
                "source_kind must be an instance of "
                "KnowledgeSourceKind"
            )

        configuration_ref = self._optional_text(
            value=self.configuration_ref,
            field_name="configuration_ref",
        )

        object.__setattr__(
            self,
            "configuration_ref",
            configuration_ref,
        )

        if not isinstance(
            self.synchronization_enabled,
            bool,
        ):
            raise TypeError(
                "synchronization_enabled must be a bool"
            )

    def to_knowledge_source(
        self,
    ) -> KnowledgeSource:
        """Create the governed ingestion source contract."""

        return KnowledgeSource(
            source_id=self.source_id,
            knowledge_scope_ref=self.knowledge_scope_ref,
            source_kind=self.source_kind,
            adapter_ref=self.adapter_ref,
            configuration_ref=self.configuration_ref,
            synchronization_enabled=self.synchronization_enabled,
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

    @staticmethod
    def _optional_text(
        *,
        value: str | None,
        field_name: str,
    ) -> str | None:
        if value is None:
            return None

        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                f"{field_name} must be a string or None"
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                f"{field_name} cannot be empty when provided"
            )

        return normalized
