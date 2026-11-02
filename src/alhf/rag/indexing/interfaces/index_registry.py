# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the index-registry boundary used by the ALHF Knowledge
# Foundation indexing layer.
#
# Problem Solved:
# Knowledge representations may require different index providers while
# common indexing orchestration must remain independent from physical
# stores, deployment technologies, retrieval modes, and external tools.
#
# Responsibilities:
# - Resolve an index provider by stable index reference.
# - Report whether an index provider is registered.
# - Keep provider discovery independent from concrete implementations.
# - Support multiple configured indexes behind one stable boundary.
# - Preserve provider-neutral indexing orchestration.
#
# Must Not:
# - Create or mutate indexes directly.
# - Generate Knowledge representations.
# - Perform retrieval or reranking.
# - Contain vector-store-specific records or identifiers.
# - Assume dense vector indexing is the only indexing mechanism.
# - Implement index selection intelligence.
# - Implement concurrency, batching, or NFT execution policy.
# - Expose LangChain, LangGraph, or external framework types.
#
# Architectural Position:
# - Universal discovery boundary for ALHF index providers.
# - Separates logical index resolution from physical index technology.
# - Allows local, cloud, hybrid, graph, lexical, and future providers.
#
# Reuse Value:
# - Dense vector indexes.
# - Sparse and lexical indexes.
# - Structured indexes.
# - Graph indexes.
# - Local and cloud index providers.
# - Future hybrid retrieval foundations.
#
# Future Extensibility:
# - Multiple index versions may coexist during migration.
# - Candidate and active indexes can evolve behind provider boundaries.
# - Knowledge Intelligence can select governed indexes above this layer.
# - External tools can implement index providers without contaminating
#   stable ALHF Knowledge contracts.
# - Distributed and sharded providers can evolve independently.

from __future__ import annotations

from abc import ABC, abstractmethod


class IndexRegistry(ABC):
    """
    Universal discovery boundary for configured ALHF index providers.

    Index references are logical ALHF identifiers. Physical collection,
    table, namespace, shard, or provider identifiers remain behind the
    concrete index-provider boundary.
    """

    @abstractmethod
    def resolve(
        self,
        index_ref: str,
    ) -> object:
        """
        Resolve the provider registered for one logical index reference.

        Args:
            index_ref:
                Stable logical ALHF index reference.

        Returns:
            Registered index provider.

        Raises:
            LookupError:
                When the requested index reference is not registered.
        """

        raise NotImplementedError

    @abstractmethod
    def contains(
        self,
        index_ref: str,
    ) -> bool:
        """
        Return whether an index provider is registered for the reference.

        This permits orchestration to validate index availability before
        beginning indexing or retrieval operations.
        """

        raise NotImplementedError
