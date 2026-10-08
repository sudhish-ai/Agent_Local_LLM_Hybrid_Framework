# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides the reusable ALHF loader abstraction.
#
# Responsibilities:
# - Define a standard loading contract.
# - Return LoaderResult instances.
# - Establish consistent loader behavior.
# - Serve as the foundation for future loaders.
#
# Must Not:
# - Contain domain-specific logic.
# - Contain capability-specific logic.
# - Perform filesystem operations directly.
# - Perform orchestration.
# - Perform planning.
# - Depend on runtime components.
#
# Architectural Position:
# - Shared loading abstraction.
# - Parent for DomainLoader.
# - Parent for CapabilityLoader.
# - Parent for StrategyLoader.
# - Parent for KnowledgeLoader.
#
# Reuse Value:
# - Eliminates duplicated loader contracts.
# - Standardizes loading behavior across ALHF.
#
# Future Extensibility:
# - Filesystem loaders.
# - Database loaders.
# - Remote loaders.
# - Marketplace loaders.
#
# Design Principle:
# Think Hard Once. Implement Many Times.

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Generic
from typing import TypeVar

from alhf.core.contracts.loader_result import (
    LoaderResult,
)

TItem = TypeVar("TItem")
TSource = TypeVar("TSource")


class BaseLoader(
    ABC,
    Generic[TItem, TSource],
):
    """
    Generic ALHF loader abstraction.

    A loader transforms a source into
    a collection of loaded items.
    """

    @abstractmethod
    def load(
        self,
        source: TSource,
    ) -> LoaderResult[TItem]:
        """
        Load items from a source.

        Args:
            source:
                Loader-specific source.

        Returns:
            LoaderResult[TItem]
        """
        raise NotImplementedError
