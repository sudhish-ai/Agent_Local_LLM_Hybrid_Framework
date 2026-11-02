# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the universal ALHF SchemaIdentity contract.
#
# Responsibilities:
# - Validate schema identity preservation.
# - Validate schema version preservation.
# - Validate schema identity normalization.
# - Validate schema version normalization.
# - Validate invalid schema identity rejection.
# - Validate invalid schema version rejection.
# - Validate immutability.
#
# Must Not:
# - Test ALHF product version behavior.
# - Test schema migration behavior.
# - Test schema compatibility behavior.
# - Test RAG or Knowledge-specific schemas.
# - Test persistence, JSON, or JSONL behavior.
# - Test provider-specific schema behavior.

from dataclasses import FrozenInstanceError

import pytest

from alhf.core.operational_evidence.contracts.schema_identity import (
    SchemaIdentity,
)


def test_create_schema_identity() -> None:
    schema_identity = SchemaIdentity(
        schema_id="operational-evidence-record",
        schema_version="1.0",
    )

    assert (
        schema_identity.schema_id
        == "operational-evidence-record"
    )
    assert schema_identity.schema_version == "1.0"


def test_schema_identity_values_are_whitespace_normalized() -> None:
    schema_identity = SchemaIdentity(
        schema_id="  operational-evidence-record  ",
        schema_version="  1.0  ",
    )

    assert (
        schema_identity.schema_id
        == "operational-evidence-record"
    )
    assert schema_identity.schema_version == "1.0"


@pytest.mark.parametrize(
    "schema_id",
    (
        "",
        "   ",
    ),
)
def test_schema_id_rejects_empty_value(
    schema_id: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="schema_id cannot be empty",
    ):
        SchemaIdentity(
            schema_id=schema_id,
            schema_version="1.0",
        )


def test_schema_id_rejects_non_string_value() -> None:
    with pytest.raises(
        TypeError,
        match="schema_id must be a string",
    ):
        SchemaIdentity(
            schema_id=123,
            schema_version="1.0",
        )


@pytest.mark.parametrize(
    "schema_version",
    (
        "",
        "   ",
    ),
)
def test_schema_version_rejects_empty_value(
    schema_version: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="schema_version cannot be empty",
    ):
        SchemaIdentity(
            schema_id="operational-evidence-record",
            schema_version=schema_version,
        )


def test_schema_version_rejects_non_string_value() -> None:
    with pytest.raises(
        TypeError,
        match="schema_version must be a string",
    ):
        SchemaIdentity(
            schema_id="operational-evidence-record",
            schema_version=1,
        )


@pytest.mark.parametrize(
    "schema_version",
    (
        "1",
        "1.0",
        "1.0.0",
        "v1",
        "2026-10",
        "custom-version",
    ),
)
def test_schema_version_is_not_restricted_to_one_versioning_scheme(
    schema_version: str,
) -> None:
    schema_identity = SchemaIdentity(
        schema_id="operational-evidence-record",
        schema_version=schema_version,
    )

    assert schema_identity.schema_version == schema_version


def test_different_schema_ids_can_share_a_version() -> None:
    first_schema = SchemaIdentity(
        schema_id="operational-evidence-record",
        schema_version="1.0",
    )
    second_schema = SchemaIdentity(
        schema_id="operational-measurement",
        schema_version="1.0",
    )

    assert first_schema.schema_id != second_schema.schema_id
    assert (
        first_schema.schema_version
        == second_schema.schema_version
    )


def test_same_schema_id_can_have_different_versions() -> None:
    first_schema = SchemaIdentity(
        schema_id="operational-evidence-record",
        schema_version="1.0",
    )
    second_schema = SchemaIdentity(
        schema_id="operational-evidence-record",
        schema_version="2.0",
    )

    assert first_schema.schema_id == second_schema.schema_id
    assert (
        first_schema.schema_version
        != second_schema.schema_version
    )


def test_schema_identity_equality_uses_id_and_version() -> None:
    first_schema = SchemaIdentity(
        schema_id="operational-evidence-record",
        schema_version="1.0",
    )
    second_schema = SchemaIdentity(
        schema_id="operational-evidence-record",
        schema_version="1.0",
    )

    assert first_schema == second_schema


def test_schema_identity_is_immutable() -> None:
    schema_identity = SchemaIdentity(
        schema_id="operational-evidence-record",
        schema_version="1.0",
    )

    with pytest.raises(FrozenInstanceError):
        schema_identity.schema_version = "2.0"
