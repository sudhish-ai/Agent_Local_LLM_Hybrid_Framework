# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT

import pytest

from src.alhf.capability.capability_registry import (
    CapabilityRegistry,
)
from src.alhf.capability.contracts.capability_definition import (
    CapabilityDefinition,
)
from src.alhf.intent.contracts.intent_capability_mapping import (
    IntentCapabilityMapping,
)
from src.alhf.intent.intent_capability_registry import (
    IntentCapabilityRegistry,
)
from src.alhf.intent.intent_capability_resolver import (
    IntentCapabilityResolver,
)


def test_resolve_capabilities() -> None:
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

    resolver = (
        IntentCapabilityResolver(
            capability_registry,
            intent_registry,
        )
    )

    result = resolver.resolve(
        "hotel_booking",
    )

    assert len(result) == 2

    assert (
        result[0].capability_id
        == "hotel_search"
    )

    assert (
        result[1].capability_id
        == "hotel_booking"
    )


def test_unknown_intent_raises_error(
) -> None:
    capability_registry = (
        CapabilityRegistry()
    )

    intent_registry = (
        IntentCapabilityRegistry()
    )

    resolver = (
        IntentCapabilityResolver(
            capability_registry,
            intent_registry,
        )
    )

    with pytest.raises(
        KeyError,
    ):
        resolver.resolve(
            "unknown_intent",
        )


def test_missing_capability_definition_raises_error(
) -> None:
    capability_registry = (
        CapabilityRegistry()
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

    resolver = (
        IntentCapabilityResolver(
            capability_registry,
            intent_registry,
        )
    )

    with pytest.raises(
        KeyError,
    ):
        resolver.resolve(
            "hotel_booking",
        )
