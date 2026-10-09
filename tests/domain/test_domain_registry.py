# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for DomainRegistry.
#
# Responsibilities:
# - Validate domain registration.
# - Validate domain retrieval.
# - Validate domain uniqueness enforcement.
# - Validate domain registry lifecycle operations.
#
# Must Not:
# - Test BaseRegistry implementation details.
# - Test planner behavior.
# - Test orchestration behavior.
# - Test domain pack loading.
#
# Architectural Position:
# - Protects the ALHF domain registry contract.
# - Verifies the first concrete BaseRegistry implementation.
#
# Reuse Value:
# - Ensures consistent domain registration behavior.
#
# Future Extensibility:
# - Supports future domain loader integration.
# - Supports future dynamic domain discovery.

import pytest

from src.alhf.domain.contracts.domain_definition import (
    DomainDefinition,
)
from src.alhf.domain.domain_registry import DomainRegistry


def test_register_domain_success() -> None:
    registry = DomainRegistry()

    domain = DomainDefinition(
        domain_id="travel",
        domain_name="Travel",
        description="Travel domain.",
    )

    registry.register(domain)

    assert registry.exists("travel")


def test_get_registered_domain() -> None:
    registry = DomainRegistry()

    domain = DomainDefinition(
        domain_id="travel",
        domain_name="Travel",
        description="Travel domain.",
    )

    registry.register(domain)

    result = registry.get("travel")

    assert result == domain


def test_duplicate_domain_registration_raises_error() -> None:
    registry = DomainRegistry()

    first_domain = DomainDefinition(
        domain_id="travel",
        domain_name="Travel",
        description="Travel domain.",
    )

    duplicate_domain = DomainDefinition(
        domain_id="travel",
        domain_name="Travel Duplicate",
        description="Duplicate domain.",
    )

    registry.register(first_domain)

    with pytest.raises(ValueError):
        registry.register(duplicate_domain)


def test_missing_domain_raises_error() -> None:
    registry = DomainRegistry()

    with pytest.raises(KeyError):
        registry.get("unknown")


def test_list_identifiers_returns_registered_domains() -> None:
    registry = DomainRegistry()

    registry.register(
        DomainDefinition(
            domain_id="travel",
            domain_name="Travel",
            description="Travel domain.",
        )
    )

    registry.register(
        DomainDefinition(
            domain_id="finance",
            domain_name="Finance",
            description="Finance domain.",
        )
    )

    identifiers = registry.list_identifiers()

    assert set(identifiers) == {
        "travel",
        "finance",
    }


def test_list_entities_returns_registered_domains() -> None:
    registry = DomainRegistry()

    travel = DomainDefinition(
        domain_id="travel",
        domain_name="Travel",
        description="Travel domain.",
    )

    finance = DomainDefinition(
        domain_id="finance",
        domain_name="Finance",
        description="Finance domain.",
    )

    registry.register(travel)
    registry.register(finance)

    domains = registry.list_entities()

    assert len(domains) == 2
    assert travel in domains
    assert finance in domains


def test_unregister_removes_domain() -> None:
    registry = DomainRegistry()

    registry.register(
        DomainDefinition(
            domain_id="travel",
            domain_name="Travel",
            description="Travel domain.",
        )
    )

    registry.unregister("travel")

    assert registry.exists("travel") is False


def test_unregister_missing_domain_raises_error() -> None:
    registry = DomainRegistry()

    with pytest.raises(KeyError):
        registry.unregister("unknown")


def test_count_returns_registered_domain_count() -> None:
    registry = DomainRegistry()

    registry.register(
        DomainDefinition(
            domain_id="travel",
            domain_name="Travel",
            description="Travel domain.",
        )
    )

    registry.register(
        DomainDefinition(
            domain_id="finance",
            domain_name="Finance",
            description="Finance domain.",
        )
    )

    assert registry.count() == 2


def test_clear_removes_all_domains() -> None:
    registry = DomainRegistry()

    registry.register(
        DomainDefinition(
            domain_id="travel",
            domain_name="Travel",
            description="Travel domain.",
        )
    )

    registry.register(
        DomainDefinition(
            domain_id="finance",
            domain_name="Finance",
            description="Finance domain.",
        )
    )

    registry.clear()

    assert registry.count() == 0


def test_domain_registry_uses_domain_id_as_identifier() -> None:
    registry = DomainRegistry()

    domain = DomainDefinition(
        domain_id="healthcare",
        domain_name="Healthcare",
        description="Healthcare domain.",
    )

    registry.register(domain)

    assert registry.exists("healthcare")
    assert registry.get("healthcare") == domain
