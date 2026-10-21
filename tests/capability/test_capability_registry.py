# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for CapabilityRegistry.
#
# Responsibilities:
# - Validate capability registration.
# - Validate capability retrieval.
# - Validate capability uniqueness.
# - Validate registry lifecycle operations.
#
# Must Not:
# - Test BaseRegistry implementation details.
# - Test capability selection logic.
# - Test workflow planning logic.
# - Test runtime execution logic.
#
# Architectural Position:
# - Protects capability registry behavior.
# - Validates the capability onboarding layer.
#
# Reuse Value:
# - Travel capabilities.
# - Healthcare capabilities.
# - Finance capabilities.
# - Future domains.
#
# Design Principle:
# Think Hard Once. Implement Many Times.

import pytest

from src.alhf.capability.capability_registry import (
    CapabilityRegistry,
)
from src.alhf.capability.contracts.capability_definition import (
    CapabilityDefinition,
)


def test_register_capability_success() -> None:
    registry = CapabilityRegistry()

    capability = CapabilityDefinition(
        capability_id="hotel_search",
        capability_name="Hotel Search",
        description="Search hotels.",
    )

    registry.register(
        capability
    )

    assert registry.exists(
        "hotel_search"
    )


def test_get_registered_capability() -> None:
    registry = CapabilityRegistry()

    capability = CapabilityDefinition(
        capability_id="hotel_search",
        capability_name="Hotel Search",
        description="Search hotels.",
    )

    registry.register(
        capability
    )

    result = registry.get(
        "hotel_search"
    )

    assert result == capability


def test_duplicate_capability_registration_raises_error(
) -> None:
    registry = CapabilityRegistry()

    first = CapabilityDefinition(
        capability_id="hotel_search",
        capability_name="Hotel Search",
        description="Search hotels.",
    )

    duplicate = CapabilityDefinition(
        capability_id="hotel_search",
        capability_name="Duplicate",
        description="Duplicate capability.",
    )

    registry.register(
        first
    )

    with pytest.raises(
        ValueError
    ):
        registry.register(
            duplicate
        )


def test_missing_capability_raises_error(
) -> None:
    registry = CapabilityRegistry()

    with pytest.raises(
        KeyError
    ):
        registry.get(
            "missing_capability"
        )


def test_list_identifiers_returns_registered_capabilities(
) -> None:
    registry = CapabilityRegistry()

    registry.register(
        CapabilityDefinition(
            capability_id="hotel_search",
            capability_name="Hotel Search",
            description="Search hotels.",
        )
    )

    registry.register(
        CapabilityDefinition(
            capability_id="provider_search",
            capability_name="Provider Search",
            description="Search providers.",
        )
    )

    identifiers = (
        registry.list_identifiers()
    )

    assert set(
        identifiers
    ) == {
        "hotel_search",
        "provider_search",
    }


def test_list_entities_returns_registered_capabilities(
) -> None:
    registry = CapabilityRegistry()

    hotel_search = (
        CapabilityDefinition(
            capability_id="hotel_search",
            capability_name="Hotel Search",
            description="Search hotels.",
        )
    )

    provider_search = (
        CapabilityDefinition(
            capability_id="provider_search",
            capability_name="Provider Search",
            description="Search providers.",
        )
    )

    registry.register(
        hotel_search
    )

    registry.register(
        provider_search
    )

    capabilities = (
        registry.list_entities()
    )

    assert len(
        capabilities
    ) == 2

    assert hotel_search in capabilities

    assert provider_search in capabilities


def test_unregister_removes_capability(
) -> None:
    registry = CapabilityRegistry()

    registry.register(
        CapabilityDefinition(
            capability_id="hotel_search",
            capability_name="Hotel Search",
            description="Search hotels.",
        )
    )

    registry.unregister(
        "hotel_search"
    )

    assert (
        registry.exists(
            "hotel_search"
        )
        is False
    )


def test_unregister_missing_capability_raises_error(
) -> None:
    registry = CapabilityRegistry()

    with pytest.raises(
        KeyError
    ):
        registry.unregister(
            "unknown"
        )


def test_count_returns_registered_capability_count(
) -> None:
    registry = CapabilityRegistry()

    registry.register(
        CapabilityDefinition(
            capability_id="hotel_search",
            capability_name="Hotel Search",
            description="Search hotels.",
        )
    )

    registry.register(
        CapabilityDefinition(
            capability_id="provider_search",
            capability_name="Provider Search",
            description="Search providers.",
        )
    )

    assert (
        registry.count()
        == 2
    )


def test_clear_removes_all_capabilities(
) -> None:
    registry = CapabilityRegistry()

    registry.register(
        CapabilityDefinition(
            capability_id="hotel_search",
            capability_name="Hotel Search",
            description="Search hotels.",
        )
    )

    registry.register(
        CapabilityDefinition(
            capability_id="provider_search",
            capability_name="Provider Search",
            description="Search providers.",
        )
    )

    registry.clear()

    assert (
        registry.count()
        == 0
    )


def test_capability_registry_uses_capability_id_as_identifier(
) -> None:
    registry = CapabilityRegistry()

    capability = (
        CapabilityDefinition(
            capability_id="appointment_booking",
            capability_name="Appointment Booking",
            description="Book appointments.",
        )
    )

    registry.register(
        capability
    )

    assert registry.exists(
        "appointment_booking"
    )

    assert (
        registry.get(
            "appointment_booking"
        )
        == capability
    )
