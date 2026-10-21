# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for CapabilityIntelligenceBootstrap.
#
# Responsibilities:
# - Validate capability intelligence bootstrap.
# - Validate registry population.
# - Validate runtime construction.
# - Validate context creation.
#
# Must Not:
# - Test workflow execution.
# - Test orchestration.
# - Test agent execution.
# - Test scheduler behavior.
#
# Architectural Position:
# - Protects composition layer bootstrap.
# - Validates capability intelligence assembly.
#
# Design Principle:
# Think Hard Once. Implement Many Times.

from pathlib import Path

from alhf.composition.capability_intelligence_bootstrap import (
    CapabilityIntelligenceBootstrap,
)
from alhf.composition.capability_intelligence_context import (
    CapabilityIntelligenceContext,
)


def test_build_creates_capability_intelligence_context(
) -> None:
    bootstrap = (
        CapabilityIntelligenceBootstrap()
    )

    context = (
        bootstrap.build(
            capability_definitions_path=(
                Path(
                    "capabilities/"
                    "capability_definitions.json"
                )
            ),
            domain_capabilities_path=(
                Path(
                    "domains/travel/"
                    "capabilities.json"
                )
            ),
            intent_mappings_path=(
                Path(
                    "domains/travel/"
                    "intents.json"
                )
            ),
        )
    )

    assert isinstance(
        context,
        CapabilityIntelligenceContext,
    )


def test_build_populates_registries(
) -> None:
    bootstrap = (
        CapabilityIntelligenceBootstrap()
    )

    context = (
        bootstrap.build(
            capability_definitions_path=(
                Path(
                    "capabilities/"
                    "capability_definitions.json"
                )
            ),
            domain_capabilities_path=(
                Path(
                    "domains/travel/"
                    "capabilities.json"
                )
            ),
            intent_mappings_path=(
                Path(
                    "domains/travel/"
                    "intents.json"
                )
            ),
        )
    )

    assert (
        context.capability_registry.count()
        > 0
    )

    assert (
        len(
            context.intent_registry.all()
        )
        > 0
    )

    assert (
        context.domain_registry.exists(
            "travel"
        )
    )


def test_build_creates_capability_runtime(
) -> None:
    bootstrap = (
        CapabilityIntelligenceBootstrap()
    )

    context = (
        bootstrap.build(
            capability_definitions_path=(
                Path(
                    "capabilities/"
                    "capability_definitions.json"
                )
            ),
            domain_capabilities_path=(
                Path(
                    "domains/travel/"
                    "capabilities.json"
                )
            ),
            intent_mappings_path=(
                Path(
                    "domains/travel/"
                    "intents.json"
                )
            ),
        )
    )

    selected = (
        context.capability_runtime
        .select_capabilities(
            intent_id="hotel_booking",
            domain_id="travel",
        )
    )

    assert len(
        selected
    ) > 0


def test_build_populates_counts(
) -> None:
    bootstrap = (
        CapabilityIntelligenceBootstrap()
    )

    context = (
        bootstrap.build(
            capability_definitions_path=(
                Path(
                    "capabilities/"
                    "capability_definitions.json"
                )
            ),
            domain_capabilities_path=(
                Path(
                    "domains/travel/"
                    "capabilities.json"
                )
            ),
            intent_mappings_path=(
                Path(
                    "domains/travel/"
                    "intents.json"
                )
            ),
        )
    )

    assert (
        context.capability_count
        > 0
    )

    assert (
        context.intent_mapping_count
        > 0
    )

    assert (
        context.domain_mapping_count
        > 0
    )
