# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides provider-neutral Knowledge derivation orchestration for the
# ALHF Knowledge Foundation chunking layer.
#
# Problem Solved:
# Canonical Knowledge requires bounded derivation into Knowledge Units,
# while common orchestration must remain independent from concrete
# chunking algorithms, source technologies, and input file formats.
#
# Responsibilities:
# - Accept one CanonicalContent artifact.
# - Resolve a compatible strategy through DerivationRegistry.
# - Validate resolved strategy compatibility.
# - Delegate derivation to DerivationStrategy.
# - Validate each produced KnowledgeUnit.
# - Preserve ResourceIdentity across derivation.
# - Preserve deterministic incremental unit delivery.
#
# Must Not:
# - Acquire, parse, or normalize Knowledge content.
# - Contain source-specific or file-format-specific behavior.
# - Hard-code chunk size, overlap, or derivation strategy.
# - Implement North-Star Derivation Intelligence.
# - Materialize all Knowledge Units in memory.
# - Generate embeddings or retrieval representations.
# - Perform indexing, retrieval, reranking, or context construction.
# - Implement concurrency or NFT execution policy.
# - Depend on external RAG or orchestration frameworks.
#
# Architectural Position:
# - Common orchestration boundary for Knowledge derivation.
# - Connects CanonicalContent to dynamically resolved strategies.
# - Produces a bounded stream of provider-neutral KnowledgeUnit objects.
#
# Reuse Value:
# - V1 deterministic text derivation.
# - Semantic and hierarchical derivation.
# - Structure-aware derivation.
# - Graph-aware Knowledge derivation.
# - Future evidence-driven derivation planning.
#
# Future Extensibility:
# - Derivation Intelligence can select strategies above this boundary.
# - New strategies require no downstream Knowledge contract changes.
# - Native and externally backed strategies can coexist.
# - Derivation provenance mapping can compose beside KnowledgeUnit.
# - Parallel execution can evolve without changing semantic contracts.

from __future__ import annotations

from collections.abc import Iterator

from alhf.rag.chunking.contracts.knowledge_unit import (
    KnowledgeUnit,
)
from alhf.rag.chunking.interfaces.derivation_registry import (
    DerivationRegistry,
)
from alhf.rag.chunking.interfaces.derivation_strategy import (
    DerivationStrategy,
)
from alhf.rag.ingestion.contracts.canonical_content import (
    CanonicalContent,
)


class DerivationService:
    """Orchestrate bounded Knowledge derivation."""

    def __init__(
        self,
        *,
        registry: DerivationRegistry,
    ) -> None:
        if not isinstance(
            registry,
            DerivationRegistry,
        ):
            raise TypeError(
                "registry must be an instance of DerivationRegistry"
            )

        self._registry = registry

    def derive(
        self,
        content: CanonicalContent,
    ):
        """Yield validated Knowledge Units incrementally."""

        if not isinstance(
            content,
            CanonicalContent,
        ):
            raise TypeError(
                "content must be an instance of CanonicalContent"
            )

        strategy = self._registry.resolve(
            content,
        )

        self._validate_strategy(
            strategy=strategy,
            content=content,
        )

        units = strategy.derive(
            content,
        )

        if not isinstance(
            units,
            Iterator,
        ):
            raise TypeError(
                "derivation strategy must return an Iterator"
            )

        expected_sequence = 0

        for unit in units:
            self._validate_unit(
                content=content,
                strategy=strategy,
                unit=unit,
                expected_sequence=expected_sequence,
            )

            yield unit
            expected_sequence += 1

    @staticmethod
    def _validate_strategy(
        *,
        strategy: DerivationStrategy,
        content: CanonicalContent,
    ) -> None:
        """Validate registry output and strategy compatibility."""

        if not isinstance(
            strategy,
            DerivationStrategy,
        ):
            raise TypeError(
                "registry must return DerivationStrategy"
            )

        if not strategy.supports(
            content,
        ):
            raise ValueError(
                "resolved strategy does not support canonical content"
            )

    @staticmethod
    def _validate_unit(
        *,
        content: CanonicalContent,
        strategy: DerivationStrategy,
        unit: KnowledgeUnit,
        expected_sequence: int,
    ) -> None:
        """Validate one derived Knowledge Unit."""

        if not isinstance(
            unit,
            KnowledgeUnit,
        ):
            raise TypeError(
                "derivation strategy must yield KnowledgeUnit"
            )

        if unit.identity != content.identity:
            raise ValueError(
                "KnowledgeUnit identity must match canonical content"
            )

        if unit.sequence != expected_sequence:
            raise ValueError(
                "KnowledgeUnit sequence must be contiguous"
            )

        if unit.content_kind != content.content_kind:
            raise ValueError(
                "KnowledgeUnit content kind must match canonical content"
            )

        if unit.strategy_ref != strategy.strategy_ref:
            raise ValueError(
                "KnowledgeUnit strategy_ref must match strategy"
            )

        if unit.strategy_version != strategy.strategy_version:
            raise ValueError(
                "KnowledgeUnit strategy_version must match strategy"
            )
