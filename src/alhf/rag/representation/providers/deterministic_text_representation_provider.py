# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides the deterministic text representation provider used by the
# ALHF Knowledge Foundation V1 representation layer.
#
# Problem Solved:
# V1 requires a deterministic retrieval representation that proves the
# KnowledgeUnit-to-representation pipeline before introducing embedding
# models or external representation technologies.
#
# Responsibilities:
# - Accept canonical text Knowledge Units.
# - Produce deterministic lexical Knowledge representations.
# - Preserve Knowledge Unit and derivation provenance.
# - Preserve Knowledge scope, resource, and revision provenance.
# - Produce deterministic representation identity.
# - Preserve strategy identity and version.
# - Remain independent from embedding models and vector stores.
#
# Must Not:
# - Modify Knowledge Unit content or identity.
# - Generate dense embeddings.
# - Depend on an external model or provider.
# - Perform indexing, retrieval, reranking, or context construction.
# - Implement Representation Intelligence or adaptive provider selection.
# - Contain vector-store-specific behavior.
# - Implement concurrency, batching, or NFT execution policy.
# - Depend on LangChain, LangGraph, or external frameworks.
#
# Architectural Position:
# - Concrete V1 implementation of RepresentationProvider.
# - Deterministic baseline for proving representation flow.
# - Produces provider-neutral KnowledgeRepresentation contracts.
#
# Reuse Value:
# - V1 Standard RAG pipeline validation.
# - Deterministic representation integration testing.
# - Lexical retrieval foundations.
# - Baseline comparison for future embedding providers.
#
# Future Extensibility:
# - Dense embedding providers can implement RepresentationProvider.
# - Sparse, graph, structured, and multimodal providers can coexist.
# - Model-backed representations require no KnowledgeUnit changes.
# - Representation Intelligence can select providers above this boundary.
# - External tool implementations can remain isolated behind adapters.

from __future__ import annotations

import hashlib

from alhf.rag.chunking.contracts.knowledge_unit import (
    KnowledgeUnit,
)
from alhf.rag.ingestion.contracts.canonical_content import (
    CanonicalContentKind,
)
from alhf.rag.representation.contracts.knowledge_representation import (
    KnowledgeRepresentation,
    RepresentationKind,
)
from alhf.rag.representation.interfaces.representation_provider import (
    RepresentationProvider,
)


class DeterministicTextRepresentationProvider(
    RepresentationProvider
):
    """Produce deterministic lexical representations of text units."""

    _PROVIDER_REF = "deterministic-text-representation"
    _PROVIDER_VERSION = "1.0"

    @property
    def provider_ref(self) -> str:
        """Return the stable logical provider identifier."""

        return self._PROVIDER_REF

    @property
    def provider_version(self) -> str:
        """Return the stable provider behavior version."""

        return self._PROVIDER_VERSION

    def supports(
        self,
        unit: KnowledgeUnit,
    ) -> bool:
        """Return whether the provider supports this Knowledge Unit."""

        return (
            isinstance(unit, KnowledgeUnit)
            and unit.content_kind == CanonicalContentKind.TEXT
            and unit.media_type.strip().lower() == "text/plain"
        )

    def represent(
        self,
        unit: KnowledgeUnit,
    ) -> KnowledgeRepresentation:
        """Produce one deterministic lexical representation."""

        if not isinstance(
            unit,
            KnowledgeUnit,
        ):
            raise TypeError(
                "unit must be an instance of KnowledgeUnit"
            )

        if not self.supports(
            unit,
        ):
            raise ValueError(
                "DeterministicTextRepresentationProvider "
                "requires a text Knowledge Unit"
            )

        return KnowledgeRepresentation(
            representation_id=self._representation_id(
                unit,
            ),
            knowledge_unit_ref=unit.unit_id,
            derivation_id=unit.derivation_id,
            knowledge_scope_ref=unit.knowledge_scope_ref,
            resource_ref=unit.resource_ref,
            revision_ref=unit.revision_ref,
            kind=RepresentationKind.LEXICAL,
            payload=unit.content,
            media_type="text/plain",
            strategy_ref=self.provider_ref,
            strategy_version=self.provider_version,
        )

    def _representation_id(
        self,
        unit: KnowledgeUnit,
    ) -> str:
        """Build deterministic representation identity."""

        material = (
            f"{unit.knowledge_scope_ref}|"
            f"{unit.resource_ref}|"
            f"{unit.revision_ref}|"
            f"{unit.derivation_id}|"
            f"{unit.unit_id}|"
            f"{self.provider_ref}|"
            f"{self.provider_version}"
        ).encode("utf-8")

        digest = hashlib.sha256(
            material
        ).hexdigest()

        return f"representation:{digest}"
