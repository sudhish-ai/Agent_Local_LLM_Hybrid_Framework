# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for BaseRegistry.
#
# Responsibilities:
# - Validate generic registry behavior.
# - Validate entity registration.
# - Validate lookup operations.
# - Validate uniqueness enforcement.
# - Validate registry lifecycle operations.
#
# Must Not:
# - Test domain-specific logic.
# - Test capability-specific logic.
# - Depend on orchestrator components.
# - Depend on planner components.
#
# Architectural Position:
# - Protects ALHF registry foundation.
# - Protects future DomainRegistry implementations.
# - Protects future CapabilityRegistry implementations.
# - Protects future StrategyRegistry implementations.
#
# Reuse Value:
# - Shared validation suite for all derived registries.
#
# Future Extensibility:
# - Additional registry implementations should inherit
#   behavior validated by these tests.

from dataclasses import dataclass

import pytest

from src.alhf.core.registry.base_registry import BaseRegistry


@dataclass(frozen=True)
class DummyEntity:
    """
    Test entity used to validate BaseRegistry.
    """

    identifier: str
    name: str


class ConcreteRegistry(
    BaseRegistry[DummyEntity, str]
):
    """
    Minimal concrete registry implementation
    used for BaseRegistry testing.
    """

    def __init__(self) -> None:
        super().__init__(
            key_resolver=lambda entity: entity.identifier,
        )


def test_register_entity_success() -> None:
    registry = ConcreteRegistry()

    entity = DummyEntity(
        identifier="travel",
        name="Travel",
    )

    registry.register(entity)

    assert registry.exists("travel")


def test_get_registered_entity() -> None:
    registry = ConcreteRegistry()

    entity = DummyEntity(
        identifier="travel",
        name="Travel",
    )

    registry.register(entity)

    result = registry.get("travel")

    assert result == entity


def test_duplicate_registration_raises_error() -> None:
    registry = ConcreteRegistry()

    registry.register(
        DummyEntity(
            identifier="travel",
            name="Travel",
        )
    )

    with pytest.raises(ValueError):
        registry.register(
            DummyEntity(
                identifier="travel",
                name="Duplicate Travel",
            )
        )


def test_missing_entity_raises_error() -> None:
    registry = ConcreteRegistry()

    with pytest.raises(KeyError):
        registry.get("unknown")


def test_exists_returns_false_for_unknown_identifier() -> None:
    registry = ConcreteRegistry()

    assert registry.exists("unknown") is False


def test_list_identifiers_returns_registered_identifiers() -> None:
    registry = ConcreteRegistry()

    registry.register(
        DummyEntity(
            identifier="travel",
            name="Travel",
        )
    )

    registry.register(
        DummyEntity(
            identifier="finance",
            name="Finance",
        )
    )

    identifiers = registry.list_identifiers()

    assert set(identifiers) == {
        "travel",
        "finance",
    }


def test_list_entities_returns_registered_entities() -> None:
    registry = ConcreteRegistry()

    travel = DummyEntity(
        identifier="travel",
        name="Travel",
    )

    finance = DummyEntity(
        identifier="finance",
        name="Finance",
    )

    registry.register(travel)
    registry.register(finance)

    entities = registry.list_entities()

    assert len(entities) == 2
    assert travel in entities
    assert finance in entities


def test_count_returns_number_of_registered_entities() -> None:
    registry = ConcreteRegistry()

    registry.register(
        DummyEntity(
            identifier="travel",
            name="Travel",
        )
    )

    registry.register(
        DummyEntity(
            identifier="finance",
            name="Finance",
        )
    )

    assert registry.count() == 2


def test_unregister_removes_entity() -> None:
    registry = ConcreteRegistry()

    registry.register(
        DummyEntity(
            identifier="travel",
            name="Travel",
        )
    )

    registry.unregister("travel")

    assert registry.exists("travel") is False


def test_unregister_missing_entity_raises_error() -> None:
    registry = ConcreteRegistry()

    with pytest.raises(KeyError):
        registry.unregister("unknown")


def test_clear_removes_all_entities() -> None:
    registry = ConcreteRegistry()

    registry.register(
        DummyEntity(
            identifier="travel",
            name="Travel",
        )
    )

    registry.register(
        DummyEntity(
            identifier="finance",
            name="Finance",
        )
    )

    registry.clear()

    assert registry.count() == 0


def test_validation_hook_can_be_overridden() -> None:
    class ValidatingRegistry(
        BaseRegistry[DummyEntity, str]
    ):
        def __init__(self) -> None:
            super().__init__(
                key_resolver=lambda entity: entity.identifier,
            )

        def _validate_registration(
            self,
            entity: DummyEntity,
            identifier: str,
        ) -> None:
            if not entity.name:
                raise ValueError(
                    "Name is mandatory."
                )

    registry = ValidatingRegistry()

    with pytest.raises(ValueError):
        registry.register(
            DummyEntity(
                identifier="travel",
                name="",
            )
        )
