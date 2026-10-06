# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for DomainDefinition.
#
# Responsibilities:
# - Validate domain contract creation.
# - Validate field initialization.
# - Validate immutable behavior.
# - Validate contract validation rules.
#
# Must Not:
# - Test domain registry behavior.
# - Test planner behavior.
# - Test orchestration behavior.
# - Test domain-pack loading behavior.
#
# Architectural Position:
# - Protects ALHF domain contract.
# - Ensures consistency across all future domains.
#
# Reuse Value:
# - Shared validation suite for every future domain.
#
# Future Extensibility:
# - Supports new metadata fields.
# - Supports future version evolution.

import pytest

from src.alhf.domain.contracts.domain_definition import (
    DomainDefinition,
)


def test_create_domain_definition_success() -> None:
    domain = DomainDefinition(
        domain_id="software_engineering",
        domain_name="Software Engineering",
        description="Software engineering domain.",
    )

    assert domain.domain_id == "software_engineering"
    assert domain.domain_name == "Software Engineering"
    assert domain.description == "Software engineering domain."
    assert domain.version == "1.0"


def test_metadata_defaults_to_empty_mapping() -> None:
    domain = DomainDefinition(
        domain_id="travel",
        domain_name="Travel",
        description="Travel domain.",
    )

    assert domain.metadata == {}


def test_custom_metadata_is_supported() -> None:
    domain = DomainDefinition(
        domain_id="travel",
        domain_name="Travel",
        description="Travel domain.",
        metadata={
            "owner": "ALHF",
            "category": "consumer",
        },
    )

    assert domain.metadata["owner"] == "ALHF"
    assert domain.metadata["category"] == "consumer"


def test_empty_domain_id_raises_error() -> None:
    with pytest.raises(ValueError):
        DomainDefinition(
            domain_id="",
            domain_name="Travel",
            description="Travel domain.",
        )


def test_whitespace_domain_id_raises_error() -> None:
    with pytest.raises(ValueError):
        DomainDefinition(
            domain_id="   ",
            domain_name="Travel",
            description="Travel domain.",
        )


def test_empty_domain_name_raises_error() -> None:
    with pytest.raises(ValueError):
        DomainDefinition(
            domain_id="travel",
            domain_name="",
            description="Travel domain.",
        )


def test_whitespace_domain_name_raises_error() -> None:
    with pytest.raises(ValueError):
        DomainDefinition(
            domain_id="travel",
            domain_name="   ",
            description="Travel domain.",
        )


def test_empty_description_raises_error() -> None:
    with pytest.raises(ValueError):
        DomainDefinition(
            domain_id="travel",
            domain_name="Travel",
            description="",
        )


def test_whitespace_description_raises_error() -> None:
    with pytest.raises(ValueError):
        DomainDefinition(
            domain_id="travel",
            domain_name="Travel",
            description="   ",
        )


def test_default_version_is_assigned() -> None:
    domain = DomainDefinition(
        domain_id="finance",
        domain_name="Finance",
        description="Finance domain.",
    )

    assert domain.version == "1.0"


def test_custom_version_is_supported() -> None:
    domain = DomainDefinition(
        domain_id="finance",
        domain_name="Finance",
        description="Finance domain.",
        version="2.0",
    )

    assert domain.version == "2.0"


def test_domain_definition_is_immutable() -> None:
    domain = DomainDefinition(
        domain_id="travel",
        domain_name="Travel",
        description="Travel domain.",
    )

    with pytest.raises(AttributeError):
        domain.domain_name = "Modified Travel"
