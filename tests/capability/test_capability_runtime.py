# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for CapabilityRuntime.
#
# Responsibilities:
# - Validate end-to-end capability resolution.
# - Validate intent capability resolution.
# - Validate domain capability resolution.
# - Validate capability selection engine integration.
# - Validate mandatory capability inclusion.
#
# Must Not:
# - Test workflow planning.
# - Test orchestration.
# - Test execution.
# - Test runtime scheduling.
#
# Architectural Position:
# - Protects capability intelligence runtime.
# - Validates resolver composition.
# - Guards capability selection behavior.
#
# Design Principle:
# Think Hard Once. Implement Many Times.

from alhf.capability.capability_registry import (
    CapabilityRegistry,
)
from alhf.capability.capability_runtime import (
    CapabilityRuntime,
)
from alhf.capability.capability_selection_engine import (
    CapabilitySelectionEngine,
)
from alhf.capability.contracts.capability_definition import (
    CapabilityDefinition,
)

from alhf.domain.contracts.domain_capability_mapping import (
    DomainCapabilityMapping,
)
from alhf.domain.domain_capability_registry import (
    DomainCapabilityRegistry,
)
from alhf.domain.domain_capability_resolver import (
    DomainCapabilityResolver,
)

from alhf.intent.contracts.intent_capability_mapping import (
    IntentCapabilityMapping,
)
from alhf.intent.intent_capability_registry import (
    IntentCapabilityRegistry,
)
from alhf.intent.intent_capability_resolver import (
    IntentCapabilityResolver,
)


def test_select_capabilities_for_hotel_booking(
) -> None:
    capability_registry = (
        CapabilityRegistry()
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
            capability_id="hotel_booking",
            capability_name="Hotel Booking",
            description="Book hotels.",
        )
    )

    capability_registry.register(
        CapabilityDefinition(
            capability_id="trip_planning",
            capability_name="Trip Planning",
            description="Generate itinerary.",
        )
    )

    intent_registry = (
        IntentCapabilityRegistry()
    )

    intent_registry.register(
        IntentCapabilityMapping(
            intent_id="hotel_booking",
            capability_ids=(
                "hotel_search",
                "hotel_booking",
            ),
        )
    )

    domain_registry = (
        DomainCapabilityRegistry()
    )

    domain_registry.register(
        DomainCapabilityMapping(
            domain_id="travel",
            capability_ids=(
                "hotel_search",
                "hotel_booking",
                "trip_planning",
            ),
            mandatory_capability_ids=(),
        )
    )

    runtime = CapabilityRuntime(
        intent_capability_resolver=(
            IntentCapabilityResolver(
                capability_registry=(
                    capability_registry
                ),
                intent_capability_registry=(
                    intent_registry
                ),
            )
        ),
        domain_capability_resolver=(
            DomainCapabilityResolver(
                capability_registry=(
                    capability_registry
                ),
                domain_capability_registry=(
                    domain_registry
                ),
            )
        ),
        domain_capability_registry=(
            domain_registry
        ),
        capability_selection_engine=(
            CapabilitySelectionEngine()
        ),
    )

    selected = (
        runtime.select_capabilities(
            intent_id="hotel_booking",
            domain_id="travel",
        )
    )

    assert len(selected) == 2

    assert (
        selected[0].capability_id
        == "hotel_search"
    )

    assert (
        selected[1].capability_id
        == "hotel_booking"
    )


def test_mandatory_capability_added(
) -> None:
    capability_registry = (
        CapabilityRegistry()
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
            capability_id="fraud_validation",
            capability_name=(
                "Fraud Validation"
            ),
            description=(
                "Perform fraud checks."
            ),
        )
    )

    intent_registry = (
        IntentCapabilityRegistry()
    )

    intent_registry.register(
        IntentCapabilityMapping(
            intent_id="hotel_booking",
            capability_ids=(
                "hotel_search",
            ),
        )
    )

    domain_registry = (
        DomainCapabilityRegistry()
    )

    domain_registry.register(
        DomainCapabilityMapping(
            domain_id="travel",
            capability_ids=(
                "hotel_search",
                "fraud_validation",
            ),
            mandatory_capability_ids=(
                "fraud_validation",
            ),
        )
    )

    runtime = CapabilityRuntime(
        intent_capability_resolver=(
            IntentCapabilityResolver(
                capability_registry=(
                    capability_registry
                ),
                intent_capability_registry=(
                    intent_registry
                ),
            )
        ),
        domain_capability_resolver=(
            DomainCapabilityResolver(
                capability_registry=(
                    capability_registry
                ),
                domain_capability_registry=(
                    domain_registry
                ),
            )
        ),
        domain_capability_registry=(
            domain_registry
        ),
        capability_selection_engine=(
            CapabilitySelectionEngine()
        ),
    )

    selected = (
        runtime.select_capabilities(
            intent_id="hotel_booking",
            domain_id="travel",
        )
    )

    assert len(selected) == 2

    assert (
        selected[0].capability_id
        == "hotel_search"
    )

    assert (
        selected[1].capability_id
        == "fraud_validation"
    )
