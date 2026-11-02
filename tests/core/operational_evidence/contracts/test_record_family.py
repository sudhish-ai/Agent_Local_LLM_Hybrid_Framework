# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the universal ALHF OperationalRecordFamily contract.
#
# Responsibilities:
# - Validate all supported operational-evidence record families.
# - Validate stable serialization-friendly values.
# - Validate enum string compatibility.
# - Validate semantic separation between record families.
# - Protect the universal record-family taxonomy from regression.
#
# Must Not:
# - Test workflow, task, or agent event types.
# - Test RAG or Knowledge-specific event semantics.
# - Test failure, retry, severity, or outcome semantics.
# - Test persistence, JSON, or JSONL behavior.
# - Test logging or metrics behavior.
# - Test analytical algorithms.
# - Test recommendation or remediation behavior.
#
# Architectural Position:
# - Protects the universal ALHF Operational Evidence record taxonomy.
# - Ensures operational facts and derived intelligence remain explicitly
#   distinguishable at the contract level.

from enum import Enum

import pytest

from alhf.core.operational_evidence.contracts.record_family import (
    OperationalRecordFamily,
)


def test_operational_record_family_inherits_from_string() -> None:
    assert issubclass(
        OperationalRecordFamily,
        str,
    )


def test_operational_record_family_inherits_from_enum() -> None:
    assert issubclass(
        OperationalRecordFamily,
        Enum,
    )


@pytest.mark.parametrize(
    ("record_family", "expected_value"),
    (
        (
            OperationalRecordFamily.OPERATIONAL_EVENT,
            "OPERATIONAL_EVENT",
        ),
        (
            OperationalRecordFamily.MEASUREMENT,
            "MEASUREMENT",
        ),
        (
            OperationalRecordFamily.FINDING,
            "FINDING",
        ),
        (
            OperationalRecordFamily.PREDICTION,
            "PREDICTION",
        ),
        (
            OperationalRecordFamily.RECOMMENDATION,
            "RECOMMENDATION",
        ),
        (
            OperationalRecordFamily.HUMAN_DECISION,
            "HUMAN_DECISION",
        ),
        (
            OperationalRecordFamily.ACTION,
            "ACTION",
        ),
        (
            OperationalRecordFamily.VALIDATION,
            "VALIDATION",
        ),
    ),
)
def test_record_family_has_stable_value(
    record_family: OperationalRecordFamily,
    expected_value: str,
) -> None:
    assert record_family.value == expected_value


def test_record_family_values_are_unique() -> None:
    values = tuple(
        record_family.value
        for record_family in OperationalRecordFamily
    )

    assert len(values) == len(set(values))


def test_all_expected_record_families_exist() -> None:
    assert set(OperationalRecordFamily) == {
        OperationalRecordFamily.OPERATIONAL_EVENT,
        OperationalRecordFamily.MEASUREMENT,
        OperationalRecordFamily.FINDING,
        OperationalRecordFamily.PREDICTION,
        OperationalRecordFamily.RECOMMENDATION,
        OperationalRecordFamily.HUMAN_DECISION,
        OperationalRecordFamily.ACTION,
        OperationalRecordFamily.VALIDATION,
    }


def test_operational_event_is_distinct_from_measurement() -> None:
    assert (
        OperationalRecordFamily.OPERATIONAL_EVENT
        != OperationalRecordFamily.MEASUREMENT
    )


def test_finding_is_distinct_from_prediction() -> None:
    assert (
        OperationalRecordFamily.FINDING
        != OperationalRecordFamily.PREDICTION
    )


def test_prediction_is_distinct_from_recommendation() -> None:
    assert (
        OperationalRecordFamily.PREDICTION
        != OperationalRecordFamily.RECOMMENDATION
    )


def test_recommendation_is_distinct_from_human_decision() -> None:
    assert (
        OperationalRecordFamily.RECOMMENDATION
        != OperationalRecordFamily.HUMAN_DECISION
    )


def test_human_decision_is_distinct_from_action() -> None:
    assert (
        OperationalRecordFamily.HUMAN_DECISION
        != OperationalRecordFamily.ACTION
    )


def test_action_is_distinct_from_validation() -> None:
    assert (
        OperationalRecordFamily.ACTION
        != OperationalRecordFamily.VALIDATION
    )


def test_record_family_can_be_created_from_stable_value() -> None:
    record_family = OperationalRecordFamily(
        "OPERATIONAL_EVENT"
    )

    assert record_family is OperationalRecordFamily.OPERATIONAL_EVENT


def test_unknown_record_family_value_is_rejected() -> None:
    with pytest.raises(
        ValueError,
    ):
        OperationalRecordFamily(
            "UNKNOWN_RECORD_FAMILY"
        )


def test_record_family_values_are_string_compatible() -> None:
    record_family = OperationalRecordFamily.MEASUREMENT

    assert isinstance(
        record_family,
        str,
    )
    assert record_family.value == "MEASUREMENT"
