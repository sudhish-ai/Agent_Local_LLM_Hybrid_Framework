# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for CapabilitySelectionEngine.
#
# Responsibilities:
# - Validate capability selection.
# - Validate mandatory capability inclusion.
# - Validate deduplication behavior.
# - Validate ordering behavior.
# - Validate failure handling.
#
# Must Not:
# - Test workflow planning.
# - Test orchestration.
# - Test execution.
#
# Architectural Position:
# - Protects capability selection logic.
# - Guards domain knowledge integration.
#
# Design Principle:
# Think Hard Once. Implement Many Times.

from src.alhf.capability.capability_selection_engine import (
    CapabilitySelectionEngine,
)
from src.alhf.capability.contracts.capability_definition import (
    CapabilityDefinition,
)
from src.alhf.domain.contracts.domain_capability_mapping import (
    DomainCapabilityMapping,
)


def test_select_returns_intent_capabilities_when_no_mandatory_capabilities(
) -> None:

    engine = CapabilitySelectionEngine()

    hotel_search = CapabilityDefinition(
        capability_id="hotel_search",
        capability_name="Hotel Search",
        description="Search hotels.",
    )

    hotel_booking = CapabilityDefinition(
        capability_id="hotel_booking",
        capability_name="Hotel Booking",
        description="Book hotels.",
    )

    mapping = DomainCapabilityMapping(
        domain_id="travel",
        capability_ids=(
            "hotel_search",
            "hotel_booking",
        ),
        mandatory_capability_ids=(),
    )

    result = engine.select(
        intent_capabilities=(
            hotel_search,
            hotel_booking,
        ),
        domain_mapping=mapping,
        domain_capabilities=(
            hotel_search,
            hotel_booking,
        ),
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


def test_select_adds_domain_mandatory_capabilities(
) -> None:

    engine = CapabilitySelectionEngine()

    api_design = CapabilityDefinition(
        capability_id="api_contract_design",
        capability_name="API Contract Design",
        description="Design API contracts.",
    )

    fraud_validation = CapabilityDefinition(
        capability_id="fraud_validation",
        capability_name="Fraud Validation",
        description="Validate fraud rules.",
    )

    mapping = DomainCapabilityMapping(
        domain_id="banking",
        capability_ids=(
            "api_contract_design",
            "fraud_validation",
        ),
        mandatory_capability_ids=(
            "fraud_validation",
        ),
    )

    result = engine.select(
        intent_capabilities=(
            api_design,
        ),
        domain_mapping=mapping,
        domain_capabilities=(
            api_design,
            fraud_validation,
        ),
    )

    assert len(result) == 2

    assert (
        result[0].capability_id
        == "api_contract_design"
    )

    assert (
        result[1].capability_id
        == "fraud_validation"
    )


def test_duplicate_capabilities_are_removed(
) -> None:

    engine = CapabilitySelectionEngine()

    fraud_validation = CapabilityDefinition(
        capability_id="fraud_validation",
        capability_name="Fraud Validation",
        description="Validate fraud rules.",
    )

    mapping = DomainCapabilityMapping(
        domain_id="banking",
        capability_ids=(
            "fraud_validation",
        ),
        mandatory_capability_ids=(
            "fraud_validation",
        ),
    )

    result = engine.select(
        intent_capabilities=(
            fraud_validation,
        ),
        domain_mapping=mapping,
        domain_capabilities=(
            fraud_validation,
        ),
    )

    assert len(result) == 1

    assert (
        result[0].capability_id
        == "fraud_validation"
    )


def test_selection_order_is_preserved(
) -> None:

    engine = CapabilitySelectionEngine()

    capability_a = CapabilityDefinition(
        capability_id="a",
        capability_name="A",
        description="A",
    )

    capability_b = CapabilityDefinition(
        capability_id="b",
        capability_name="B",
        description="B",
    )

    capability_c = CapabilityDefinition(
        capability_id="c",
        capability_name="C",
        description="C",
    )

    mapping = DomainCapabilityMapping(
        domain_id="test",
        capability_ids=(
            "a",
            "b",
            "c",
        ),
        mandatory_capability_ids=(
            "c",
        ),
    )

    result = engine.select(
        intent_capabilities=(
            capability_a,
            capability_b,
        ),
        domain_mapping=mapping,
        domain_capabilities=(
            capability_a,
            capability_b,
            capability_c,
        ),
    )

    assert (
        result[0].capability_id
        == "a"
    )

    assert (
        result[1].capability_id
        == "b"
    )

    assert (
        result[2].capability_id
        == "c"
    )


def test_missing_mandatory_capability_raises_error(
) -> None:

    engine = CapabilitySelectionEngine()

    api_design = CapabilityDefinition(
        capability_id="api_contract_design",
        capability_name="API Contract Design",
        description="Design API contracts.",
    )

    mapping = DomainCapabilityMapping(
        domain_id="banking",
        capability_ids=(
            "api_contract_design",
            "fraud_validation",
        ),
        mandatory_capability_ids=(
            "fraud_validation",
        ),
    )

    try:
        engine.select(
            intent_capabilities=(
                api_design,
            ),
            domain_mapping=mapping,
            domain_capabilities=(
                api_design,
            ),
        )

        assert False

    except ValueError:
        assert True


def test_multiple_mandatory_capabilities_are_added(
) -> None:

    engine = CapabilitySelectionEngine()

    api_design = CapabilityDefinition(
        capability_id="api_contract_design",
        capability_name="API Contract Design",
        description="Design API contracts.",
    )

    fraud_validation = CapabilityDefinition(
        capability_id="fraud_validation",
        capability_name="Fraud Validation",
        description="Validate fraud rules.",
    )

    compliance_validation = CapabilityDefinition(
        capability_id="compliance_validation",
        capability_name="Compliance Validation",
        description="Validate compliance.",
    )

    mapping = DomainCapabilityMapping(
        domain_id="banking",
        capability_ids=(
            "api_contract_design",
            "fraud_validation",
            "compliance_validation",
        ),
        mandatory_capability_ids=(
            "fraud_validation",
            "compliance_validation",
        ),
    )

    result = engine.select(
        intent_capabilities=(
            api_design,
        ),
        domain_mapping=mapping,
        domain_capabilities=(
            api_design,
            fraud_validation,
            compliance_validation,
        ),
    )

    assert len(result) == 3

    assert (
        result[1].capability_id
        == "fraud_validation"
    )

    assert (
        result[2].capability_id
        == "compliance_validation"
    )
