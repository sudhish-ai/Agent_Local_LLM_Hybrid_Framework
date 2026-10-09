# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides the reusable registry foundation across ALHF.
#
# Responsibilities:
# - Register entities.
# - Retrieve entities.
# - List entities.
# - Enforce uniqueness constraints.
# - Provide reusable registry behavior.
#
# Must Not:
# - Contain domain-specific logic.
# - Contain capability-specific logic.
# - Perform orchestration.
# - Perform planning.
# - Perform persistence.
# - Depend on higher-level ALHF modules.
#
# Architectural Position:
# - Foundational ALHF infrastructure.
# - Parent abstraction for all registry implementations.
# - Shared by DomainRegistry.
# - Shared by CapabilityRegistry.
# - Shared by StrategyRegistry.
# - Shared by SolutionRegistry.
#
# Reuse Value:
# - Eliminates duplicate registry implementations.
# - Standardizes ALHF registration behavior.
#
# Future Extensibility:
# - Validation hooks.
# - Persistence integration.
# - Registry events.
# - Metadata enrichment.
# - Version-aware registrations.
#
# Design Principle:
# Think Hard Once. Implement Many Times.

from __future__ import annotations

from abc import ABC
from typing import Callable
from typing import Dict
from typing import Generic
from typing import List
from typing import TypeVar


TEntity = TypeVar("TEntity")
TIdentifier = TypeVar("TIdentifier")


class BaseRegistry(
    Generic[TEntity, TIdentifier],
    ABC,
):
    """
    Generic ALHF registry.

    Stores entities and delegates identifier
    extraction to a caller-provided strategy.

    Example:

        registry = MyRegistry(
            key_resolver=lambda x: x.id
        )

        registry.register(entity)
    """

    def __init__(
        self,
        key_resolver: Callable[[TEntity], TIdentifier],
    ) -> None:
        self._key_resolver = key_resolver
        self._entities: Dict[TIdentifier, TEntity] = {}

    def register(
        self,
        entity: TEntity,
    ) -> None:
        """
        Register a new entity.

        Raises:
            ValueError:
                If entity already exists.
        """

        identifier = self._key_resolver(entity)

        self._validate_registration(
            entity=entity,
            identifier=identifier,
        )

        if identifier in self._entities:
            raise ValueError(
                f"Entity already registered: {identifier}"
            )

        self._entities[identifier] = entity

    def get(
        self,
        identifier: TIdentifier,
    ) -> TEntity:
        """
        Retrieve entity by identifier.
        """

        if identifier not in self._entities:
            raise KeyError(
                f"Entity not found: {identifier}"
            )

        return self._entities[identifier]

    def exists(
        self,
        identifier: TIdentifier,
    ) -> bool:
        """
        Check whether entity exists.
        """

        return identifier in self._entities

    def unregister(
        self,
        identifier: TIdentifier,
    ) -> None:
        """
        Remove an entity.
        """

        if identifier not in self._entities:
            raise KeyError(
                f"Entity not found: {identifier}"
            )

        del self._entities[identifier]

    def list_identifiers(
        self,
    ) -> List[TIdentifier]:
        """
        Return identifiers.

        Intentionally unsorted.
        Sorting belongs to callers.
        """

        return list(self._entities.keys())

    def list_entities(
        self,
    ) -> List[TEntity]:
        """
        Return entities.
        """

        return list(self._entities.values())

    def count(self) -> int:
        """
        Return number of registered entities.
        """

        return len(self._entities)

    def clear(self) -> None:
        """
        Clear registry contents.
        """

        self._entities.clear()

    def _validate_registration(
        self,
        entity: TEntity,
        identifier: TIdentifier,
    ) -> None:
        """
        Extension hook.

        Derived registries may override.
        """

        return
