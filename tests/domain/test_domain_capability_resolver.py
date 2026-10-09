# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for DomainCapabilityResolver.
#
# Responsibilities:
# - Validate domain capability resolution.
# - Validate integration between registries.
# - Validate relationship lookups.
#
# Must Not:
# - Test planning logic.
# - Test orchestration logic.
# - Test execution logic.
#
# Architectural Position:
# - First runtime intelligence validation.
# - Protects Domain -> Capability resolution.
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
from src.alhf.domain.contracts.domain_capability_mapping import (
    DomainCapabilityMapping,
)
from src.alhf.domain.domain_capability_registry import (
    DomainCapabilityRegistry,
)
from src.alhf.domain.domain_capability_resolver import (
    DomainCapabilityResolver,
)


def test_resolve_single_capability() -> None:
    capability_registry = CapabilityRegistry()
    mapping_registry = DomainCapabilityRegistry()

    capability = CapabilityDefinition(
        capability_id="hotel_search",
        capability_name="Hotel Search",
        description="Search hotels.",
    )

    capability_registry.register(
        capability
    )

    mapping_registry.register(
        DomainCapabilityMapping(
            domain_id="travel",
            capability_ids=(
                "hotel_search",
            ),
        )
    )

    resolver = DomainCapabilityResolver(
        capability_registry=
        capability_registry,
        domain_capability_registry=
        mapping_registry,
    )

    result = resolver.resolve(
        "travel"
    )

    assert len(result) == 1

    assert result[0] == capability


def test_resolve_multiple_capabilities() -> None:
    capability_registry = CapabilityRegistry()
    mapping_registry = DomainCapabilityRegistry()

    hotel_search = CapabilityDefinition(
        capability_id="hotel_search",
        capability_name="Hotel Search",
        description="Search hotels.",
    )

    flight_search = CapabilityDefinition(
        capability_id="flight_search",
        capability_name="Flight Search",
        description="Search flights.",
    )

    capability_registry.register(
        hotel_search
    )

    capability_registry.register(
        flight_search
    )

    mapping_registry.register(
        DomainCapabilityMapping(
            domain_id="travel",
            capability_ids=(
                "hotel_search",
                "flight_search",
            ),
        )
    )

    resolver = DomainCapabilityResolver(
        capability_registry=
        capability_registry,
        domain_capability_registry=
        mapping_registry,
    )

    result = resolver.resolve(
        "travel"
    )

    assert len(result) == 2

    assert hotel_search in result

    assert flight_search in result


def test_missing_domain_raises_error() -> None:
    capability_registry = CapabilityRegistry()
    mapping_registry = (
        DomainCapabilityRegistry()
    )

    resolver = DomainCapabilityResolver(
        capability_registry=
        capability_registry,
        domain_capability_registry=
        mapping_registry,
    )

    with pytest.raises(KeyError):
        resolver.resolve(
            "unknown_domain"
        )


def test_missing_capability_raises_error() -> None:
    capability_registry = CapabilityRegistry()
    mapping_registry = (
        DomainCapabilityRegistry()
    )

    mapping_registry.register(
        DomainCapabilityMapping(
            domain_id="travel",
            capability_ids=(
                "hotel_search",
            ),
        )
    )

    resolver = DomainCapabilityResolver(
        capability_registry=
        capability_registry,
        domain_capability_registry=
        mapping_registry,
    )

    with pytest.raises(KeyError):
        resolver.resolve(
            "travel"
        )


def test_preserves_capability_order() -> None:
    capability_registry = CapabilityRegistry()
    mapping_registry = (
        DomainCapabilityRegistry()
    )

    capability_registry.register(
        CapabilityDefinition(
            capability_id="hotel_search",
            capability_name="Hotel Search",
            description="Search hotels.",
        )
    )

    capability_registry.register(
        CapabilityDefinition(
            capability_id="flight_search",
            capability_name="Flight Search",
            description="Search flights.",
        )
    )

    mapping_registry.register(
        DomainCapabilityMapping(
            domain_id="travel",
            capability_ids=(
                "hotel_search",
                "flight_search",
            ),
        )
    )

    resolver = DomainCapabilityResolver(
        capability_registry=
        capability_registry,
        domain_capability_registry=
        mapping_registry,
    )

    result = resolver.resolve(
        "travel"
    )

    assert (
        result[0].capability_id
        == "hotel_search"
    )

    assert (
        result[1].capability_id
        == "flight_search"
    )


def test_empty_resolution_not_possible() -> None:
    capability_registry = CapabilityRegistry()
    mapping_registry = (
        DomainCapabilityRegistry()
    )

    capability_registry.register(
        CapabilityDefinition(
            capability_id="hotel_search",
            capability_name="Hotel Search",
            description="Search hotels.",
        )
    )

    mapping_registry.register(
        DomainCapabilityMapping(
            domain_id="travel",
            capability_ids=(
                "hotel_search",
            ),
        )
    )

    resolver = DomainCapabilityResolver(
        capability_registry=
        capability_registry,
        domain_capability_registry=
        mapping_registry,
    )

    result = resolver.resolve(
        "travel"
    )

    assert len(result) > 0
