from src.alhf.domain.contracts.domain_capability_mapping import (
    DomainCapabilityMapping,
)


def test_domain_capability_mapping_supports_empty_mandatory_capabilities(
) -> None:

    mapping = DomainCapabilityMapping(
        domain_id="travel",
        capability_ids=(
            "hotel_search",
            "flight_search",
        ),
        mandatory_capability_ids=(),
    )

    assert (
        mapping.mandatory_capability_count
        == 0
    )


def test_domain_capability_mapping_supports_mandatory_capabilities(
) -> None:

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

    assert mapping.is_mandatory(
        "fraud_validation"
    )

    assert mapping.is_mandatory(
        "compliance_validation"
    )


def test_mandatory_capability_must_exist_in_domain_capabilities(
) -> None:

    try:
        DomainCapabilityMapping(
            domain_id="banking",
            capability_ids=(
                "api_contract_design",
            ),
            mandatory_capability_ids=(
                "fraud_validation",
            ),
        )

        assert False

    except ValueError:
        assert True
