# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides the in-memory derivation-strategy registry used by the
# ALHF Knowledge Foundation chunking layer.
#
# Problem Solved:
# Derivation orchestration must resolve compatible Knowledge derivation
# strategies without hard-coded strategy selection in common chunking
# logic or downstream Knowledge Foundation layers.
#
# Responsibilities:
# - Register configured DerivationStrategy implementations.
# - Preserve deterministic registration order.
# - Resolve a compatible strategy for CanonicalContent.
# - Report whether compatible derivation behavior is available.
# - Reject duplicate strategy references.
# - Validate strategy identity and version during registration.
#
# Must Not:
# - Derive Knowledge Units directly.
# - Acquire, parse, or normalize Knowledge content.
# - Contain source-specific or file-format-specific behavior.
# - Hard-code chunk size, overlap, or derivation selection.
# - Implement Derivation Intelligence or adaptive strategy selection.
# - Generate representations or embeddings.
# - Perform indexing, retrieval, reranking, or context construction.
# - Load external frameworks or plugins directly.
# - Implement concurrency or NFT execution policy.
#
# Architectural Position:
# - Concrete V1 implementation of DerivationRegistry.
# - Composition mechanism for configured derivation strategies.
# - Keeps derivation mechanisms replaceable behind stable ALHF contracts.
#
# Reuse Value:
# - Fixed-size derivation.
# - Recursive and semantic derivation.
# - Hierarchical and structure-aware derivation.
# - Future GraphRAG and Agentic RAG derivation strategies.
# - Native and future externally backed strategy implementations.
#
# Future Extensibility:
# - Knowledge Intelligence can select among registered strategies.
# - Evidence-driven Derivation Plans can resolve through this boundary.
# - Plugin-backed registries can implement DerivationRegistry separately.
# - External framework adapters can implement DerivationStrategy without
#   changing common ALHF Knowledge contracts.
# - Parallel derivation can evolve outside semantic registry behavior.

from __future__ import annotations

from alhf.rag.chunking.interfaces.derivation_registry import (
    DerivationRegistry,
)
from alhf.rag.chunking.interfaces.derivation_strategy import (
    DerivationStrategy,
)
from alhf.rag.ingestion.contracts.canonical_content import (
    CanonicalContent,
)


class InMemoryDerivationRegistry(DerivationRegistry):
    """In-memory registry of configured derivation strategies."""

    def __init__(self) -> None:
        self._strategies: dict[str, DerivationStrategy] = {}

    def register(
        self,
        strategy: DerivationStrategy,
    ) -> None:
        """Register one configured derivation strategy."""

        if not isinstance(
            strategy,
            DerivationStrategy,
        ):
            raise TypeError(
                "strategy must be an instance of DerivationStrategy"
            )

        strategy_ref = self._required_text(
            value=strategy.strategy_ref,
            field_name="strategy_ref",
        )

        self._required_text(
            value=strategy.strategy_version,
            field_name="strategy_version",
        )

        if strategy_ref in self._strategies:
            raise ValueError(
                f"strategy already registered: {strategy_ref}"
            )

        self._strategies[strategy_ref] = strategy

    def resolve(
        self,
        content: CanonicalContent,
    ) -> DerivationStrategy:
        """Resolve the first compatible registered strategy."""

        self._validate_content(
            content,
        )

        for strategy in self._strategies.values():
            if strategy.supports(
                content,
            ):
                return strategy

        raise LookupError(
            "derivation strategy not found for canonical content"
        )

    def contains(
        self,
        content: CanonicalContent,
    ) -> bool:
        """Return whether a compatible strategy is registered."""

        self._validate_content(
            content,
        )

        return any(
            strategy.supports(
                content,
            )
            for strategy in self._strategies.values()
        )

    def __contains__(
        self,
        strategy_ref: object,
    ) -> bool:
        """Return whether a strategy reference is registered."""

        if not isinstance(
            strategy_ref,
            str,
        ):
            return False

        normalized_ref = strategy_ref.strip()

        if not normalized_ref:
            return False

        return normalized_ref in self._strategies

    def __len__(self) -> int:
        """Return the number of registered strategies."""

        return len(
            self._strategies,
        )

    @staticmethod
    def _validate_content(
        content: CanonicalContent,
    ) -> None:
        """Validate canonical content supplied for resolution."""

        if not isinstance(
            content,
            CanonicalContent,
        ):
            raise TypeError(
                "content must be an instance of CanonicalContent"
            )

    @staticmethod
    def _required_text(
        *,
        value: str,
        field_name: str,
    ) -> str:
        """Validate and normalize required registry text."""

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
