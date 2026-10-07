# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for DomainCapabilityRegistry.
#
# Responsibilities:
# - Validate mapping registration.
# - Validate mapping retrieval.
# - Validate uniqueness enforcement.
# - Validate registry lifecycle operations.
#
# Must Not:
# - Test capability resolution.
# - Test planning.
# - Test orchestration.
# - Test execution.
#
# Architectural Position:
# - Protects relationship registry behavior.
# - Validates DomainCapabilityMapping storage.
#
# Design Principle:
# Think Hard Once. Implement Many Times.

import pytest

from src.alhf.domain.contracts.domain_capability_mapping import (
    DomainCapabilityMapping,
)
from src.alhf.domain.domain_capability_registry import (
    DomainCapabilityRegistry,
)


def test_register_mapping_success() -> None:
    registry = DomainCapabilityRegistry()

    mapping = DomainCapabilityMapping(
        domain_id="travel",
        capability_ids=(
            "hotel_search",
            "flight_search",
        ),
    )

    registry.register(mapping)

    assert registry.exists("travel")


def test_get_registered_mapping() -> None:
    registry = DomainCapabilityRegistry()

    mapping = DomainCapabilityMapping(
        domain_id="travel",
        capability_ids=(
            "hotel_search",
            "flight_search",
        ),
    )

    registry.register(mapping)

    result = registry.get("travel")

    assert result == mapping


def test_duplicate_mapping_registration_raises_error() -> None:
    registry = DomainCapabilityRegistry()

    first_mapping = DomainCapabilityMapping(
        domain_id="travel",
        capability_ids=("hotel_search",),
    )

    duplicate_mapping = DomainCapabilityMapping(
        domain_id="travel",
        capability_ids=("flight_search",),
    )

    registry.register(first_mapping)

    with pytest.raises(ValueError):
        registry.register(
            duplicate_mapping
        )


def test_missing_mapping_raises_error() -> None:
    registry = DomainCapabilityRegistry()

    with pytest.raises(KeyError):
        registry.get("unknown")


def test_list_identifiers_returns_registered_domains() -> None:
    registry = DomainCapabilityRegistry()

    registry.register(
        DomainCapabilityMapping(
            domain_id="travel",
            capability_ids=("hotel_search",),
        )
    )

    registry.register(
        DomainCapabilityMapping(
            domain_id="healthcare",
            capability_ids=("provider_search",),
        )
    )

    identifiers = registry.list_identifiers()

    assert set(
        identifiers
    ) == {
        "travel",
        "healthcare",
    }


def test_list_entities_returns_registered_mappings() -> None:
    registry = DomainCapabilityRegistry()

    travel_mapping = DomainCapabilityMapping(
        domain_id="travel",
        capability_ids=("hotel_search",),
    )

    healthcare_mapping = DomainCapabilityMapping(
        domain_id="healthcare",
        capability_ids=("provider_search",),
    )

    registry.register(
        travel_mapping
    )

    registry.register(
        healthcare_mapping
    )

    mappings = registry.list_entities()

    assert len(mappings) == 2

    assert travel_mapping in mappings

    assert healthcare_mapping in mappings


def test_unregister_removes_mapping() -> None:
    registry = DomainCapabilityRegistry()

    registry.register(
        DomainCapabilityMapping(
            domain_id="travel",
            capability_ids=("hotel_search",),
        )
    )

    registry.unregister("travel")

    assert (
        registry.exists("travel")
        is False
    )


def test_unregister_missing_mapping_raises_error() -> None:
    registry = DomainCapabilityRegistry()

    with pytest.raises(KeyError):
        registry.unregister("unknown")


def test_count_returns_registered_mapping_count() -> None:
    registry = DomainCapabilityRegistry()

    registry.register(
        DomainCapabilityMapping(
            domain_id="travel",
            capability_ids=("hotel_search",),
        )
    )

    registry.register(
        DomainCapabilityMapping(
            domain_id="healthcare",
            capability_ids=("provider_search",),
        )
    )

    assert registry.count() == 2


def test_clear_removes_all_mappings() -> None:
    registry = DomainCapabilityRegistry()

    registry.register(
        DomainCapabilityMapping(
            domain_id="travel",
            capability_ids=("hotel_search",),
        )
    )

    registry.register(
        DomainCapabilityMapping(
            domain_id="healthcare",
            capability_ids=("provider_search",),
        )
    )

    registry.clear()

    assert registry.count() == 0


def test_registry_uses_domain_id_as_identifier() -> None:
    registry = DomainCapabilityRegistry()

    mapping = DomainCapabilityMapping(
        domain_id="travel",
        capability_ids=(
            "hotel_search",
            "flight_search",
        ),
    )

    registry.register(mapping)

    assert registry.exists("travel")

    assert registry.get("travel") == mapping
