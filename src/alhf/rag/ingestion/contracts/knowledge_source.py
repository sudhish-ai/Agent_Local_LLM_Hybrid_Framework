# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the universal Knowledge Source contract used by the
# ALHF Knowledge Foundation ingestion plane.
#
# Problem Solved:
# ALHF must acquire knowledge from many physical source technologies
# without coupling the common Knowledge Foundation to local files,
# object storage, databases, APIs, repositories, or cloud platforms.
#
# Responsibilities:
# - Identify one logical customer Knowledge source.
# - Preserve the governed Knowledge scope owning the source.
# - Classify the source through stable provider-neutral semantics.
# - Preserve an adapter reference used to resolve acquisition behavior.
# - Preserve optional source configuration reference.
# - Preserve whether the source participates in synchronization.
# - Provide immutable, provider-neutral source semantics.
#
# Must Not:
# - Store credentials, secrets, tokens, or connection strings.
# - Store filesystem paths, URLs, bucket names, or database locations.
# - Perform source acquisition.
# - Discover resources within a source.
# - Detect source changes.
# - Define synchronization checkpoints.
# - Load source contents into memory.
# - Contain parsing, chunking, embedding, or retrieval behavior.
# - Contain Standard RAG, GraphRAG, or Agentic RAG logic.
# - Contain arbitrary metadata or payload dictionaries.
#
# Architectural Position:
# - Universal Knowledge Foundation ingestion contract.
# - Defines logical source identity before physical acquisition.
# - Physical source behavior belongs to acquisition adapters.
#
# Future Extensibility:
# - New source technologies require adapters, not core contract changes.
# - Source lifecycle and synchronization remain separate responsibilities.
# - Security and authorization remain governed through their own context.
# - Deployment-specific configuration remains external to this contract.

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class KnowledgeSourceKind(str, Enum):
    """Provider-neutral categories of customer Knowledge sources."""

    FILE = "FILE"
    OBJECT_STORAGE = "OBJECT_STORAGE"
    DATABASE = "DATABASE"
    API = "API"
    WEB = "WEB"
    REPOSITORY = "REPOSITORY"
    COLLABORATION = "COLLABORATION"
    STREAM = "STREAM"
    OTHER = "OTHER"


@dataclass(frozen=True, slots=True)
class KnowledgeSource:
    """
    Immutable logical identity of one Knowledge source.

    source_id:
        Stable logical identity of the configured Knowledge source.

    knowledge_scope_ref:
        Governed Knowledge scope to which acquired resources belong.

    source_kind:
        Provider-neutral classification of the source.

    adapter_ref:
        Stable reference identifying the acquisition adapter responsible
        for interpreting the physical source configuration.

    configuration_ref:
        Optional governed reference to external source configuration.

    synchronization_enabled:
        Declares whether this source participates in synchronization
        workflows. It does not implement synchronization itself.
    """

    source_id: str
    knowledge_scope_ref: str
    source_kind: KnowledgeSourceKind
    adapter_ref: str
    configuration_ref: str | None = None
    synchronization_enabled: bool = False

    def __post_init__(self) -> None:
        source_id = self._required_text(
            self.source_id,
            "source_id",
        )
        knowledge_scope_ref = self._required_text(
            self.knowledge_scope_ref,
            "knowledge_scope_ref",
        )
        adapter_ref = self._required_text(
            self.adapter_ref,
            "adapter_ref",
        )
        configuration_ref = self._optional_text(
            self.configuration_ref,
            "configuration_ref",
        )

        if not isinstance(
            self.source_kind,
            KnowledgeSourceKind,
        ):
            raise TypeError(
                "source_kind must be an instance of KnowledgeSourceKind"
            )

        if not isinstance(
            self.synchronization_enabled,
            bool,
        ):
            raise TypeError(
                "synchronization_enabled must be a bool"
            )

        object.__setattr__(self, "source_id", source_id)
        object.__setattr__(
            self,
            "knowledge_scope_ref",
            knowledge_scope_ref,
        )
        object.__setattr__(self, "adapter_ref", adapter_ref)
        object.__setattr__(
            self,
            "configuration_ref",
            configuration_ref,
        )

    @staticmethod
    def _required_text(
        value: str,
        field_name: str,
    ) -> str:
        """Validate and normalize required source text."""

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
        value: str | None,
        field_name: str,
    ) -> str | None:
        """Validate and normalize optional source text."""

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
