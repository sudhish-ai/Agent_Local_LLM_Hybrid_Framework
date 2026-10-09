# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT

import pytest

from src.alhf.intent.contracts.intent_capability_mapping import (
    IntentCapabilityMapping,
)
from src.alhf.intent.intent_capability_registry import (
    IntentCapabilityRegistry,
)


def test_register_mapping() -> None:
    registry = (
        IntentCapabilityRegistry()
    )

    mapping = (
        IntentCapabilityMapping(
            intent_id="hotel_booking",
            capability_ids=(
                "hotel_search",
                "hotel_booking",
            ),
        )
    )

    registry.register(
        mapping,
    )

    result = registry.get(
        "hotel_booking",
    )

    assert result == mapping


def test_exists_returns_true() -> None:
    registry = (
        IntentCapabilityRegistry()
    )

    registry.register(
        IntentCapabilityMapping(
            intent_id="hotel_booking",
            capability_ids=(
                "hotel_search",
            ),
        )
    )

    assert registry.exists(
        "hotel_booking",
    )


def test_exists_returns_false() -> None:
    registry = (
        IntentCapabilityRegistry()
    )

    assert not registry.exists(
        "hotel_booking",
    )


def test_get_missing_mapping_raises_error(
) -> None:
    registry = (
        IntentCapabilityRegistry()
    )

    with pytest.raises(
        KeyError,
    ):
        registry.get(
            "unknown_intent",
        )


def test_all_returns_registered_mappings(
) -> None:
    registry = (
        IntentCapabilityRegistry()
    )

    mapping = (
        IntentCapabilityMapping(
            intent_id="hotel_booking",
            capability_ids=(
                "hotel_search",
            ),
        )
    )

    registry.register(
        mapping,
    )

    result = registry.all()

    assert len(result) == 1

    assert result[0] == mapping
