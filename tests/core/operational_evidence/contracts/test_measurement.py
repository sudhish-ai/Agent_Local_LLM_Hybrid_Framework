# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the universal ALHF OperationalMeasurement contract.
#
# Responsibilities:
# - Validate measurement identity and value preservation.
# - Validate explicit measurement units.
# - Validate methodology identity and version semantics.
# - Validate text normalization.
# - Validate invalid identifier and unit rejection.
# - Validate numeric-value constraints.
# - Validate non-finite numeric-value rejection.
# - Validate methodology pairing invariants.
# - Validate immutability.
#
# Must Not:
# - Test measurement aggregation.
# - Test statistical or predictive analysis.
# - Test RAG or Knowledge-specific measurements.
# - Test MetricsRegistry behavior.
# - Test persistence, JSON, or JSONL behavior.
# - Test sampling or retention behavior.

from dataclasses import FrozenInstanceError
from math import inf, nan

import pytest

from alhf.core.operational_evidence.contracts.measurement import (
    OperationalMeasurement,
)


def test_create_measurement_without_methodology() -> None:
    measurement = OperationalMeasurement(
        measurement_id="operation_duration",
        value=125.5,
        unit="milliseconds",
    )

    assert measurement.measurement_id == "operation_duration"
    assert measurement.value == 125.5
    assert measurement.unit == "milliseconds"
    assert measurement.methodology_id is None
    assert measurement.methodology_version is None


def test_create_measurement_with_methodology() -> None:
    measurement = OperationalMeasurement(
        measurement_id="retrieval_quality",
        value=0.92,
        unit="ratio",
        methodology_id="retrieval_quality_evaluator",
        methodology_version="1.0",
    )

    assert measurement.measurement_id == "retrieval_quality"
    assert measurement.value == 0.92
    assert measurement.unit == "ratio"
    assert (
        measurement.methodology_id
        == "retrieval_quality_evaluator"
    )
    assert measurement.methodology_version == "1.0"


def test_integer_measurement_value_is_supported() -> None:
    measurement = OperationalMeasurement(
        measurement_id="processed_items",
        value=1000,
        unit="count",
    )

    assert measurement.value == 1000


def test_negative_measurement_value_is_supported() -> None:
    measurement = OperationalMeasurement(
        measurement_id="temperature_delta",
        value=-2.5,
        unit="degrees",
    )

    assert measurement.value == -2.5


def test_zero_measurement_value_is_supported() -> None:
    measurement = OperationalMeasurement(
        measurement_id="failure_count",
        value=0,
        unit="count",
    )

    assert measurement.value == 0


def test_text_values_are_whitespace_normalized() -> None:
    measurement = OperationalMeasurement(
        measurement_id="  retrieval_quality  ",
        value=0.92,
        unit="  ratio  ",
        methodology_id="  evaluator  ",
        methodology_version="  1.0  ",
    )

    assert measurement.measurement_id == "retrieval_quality"
    assert measurement.unit == "ratio"
    assert measurement.methodology_id == "evaluator"
    assert measurement.methodology_version == "1.0"


@pytest.mark.parametrize(
    "measurement_id",
    (
        "",
        "   ",
    ),
)
def test_measurement_id_rejects_empty_value(
    measurement_id: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="measurement_id cannot be empty",
    ):
        OperationalMeasurement(
            measurement_id=measurement_id,
            value=1,
            unit="count",
        )


def test_measurement_id_rejects_non_string_value() -> None:
    with pytest.raises(
        TypeError,
        match="measurement_id must be a string",
    ):
        OperationalMeasurement(
            measurement_id=123,
            value=1,
            unit="count",
        )


@pytest.mark.parametrize(
    "unit",
    (
        "",
        "   ",
    ),
)
def test_unit_rejects_empty_value(
    unit: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="unit cannot be empty",
    ):
        OperationalMeasurement(
            measurement_id="processed_items",
            value=1,
            unit=unit,
        )


def test_unit_rejects_non_string_value() -> None:
    with pytest.raises(
        TypeError,
        match="unit must be a string",
    ):
        OperationalMeasurement(
            measurement_id="processed_items",
            value=1,
            unit=123,
        )


@pytest.mark.parametrize(
    "value",
    (
        "1",
        None,
        object(),
    ),
)
def test_measurement_value_rejects_non_numeric_value(
    value: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="value must be an int or float",
    ):
        OperationalMeasurement(
            measurement_id="processed_items",
            value=value,
            unit="count",
        )


@pytest.mark.parametrize(
    "value",
    (
        True,
        False,
    ),
)
def test_measurement_value_rejects_boolean(
    value: bool,
) -> None:
    with pytest.raises(
        TypeError,
        match="value must be an int or float",
    ):
        OperationalMeasurement(
            measurement_id="processed_items",
            value=value,
            unit="count",
        )


@pytest.mark.parametrize(
    "value",
    (
        nan,
        inf,
        -inf,
    ),
)
def test_measurement_value_rejects_non_finite_value(
    value: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="value must be finite",
    ):
        OperationalMeasurement(
            measurement_id="operation_duration",
            value=value,
            unit="milliseconds",
        )


def test_methodology_version_requires_methodology_id() -> None:
    with pytest.raises(
        ValueError,
        match="methodology_version requires methodology_id",
    ):
        OperationalMeasurement(
            measurement_id="retrieval_quality",
            value=0.92,
            unit="ratio",
            methodology_version="1.0",
        )


def test_methodology_id_requires_methodology_version() -> None:
    with pytest.raises(
        ValueError,
        match="methodology_id requires methodology_version",
    ):
        OperationalMeasurement(
            measurement_id="retrieval_quality",
            value=0.92,
            unit="ratio",
            methodology_id="retrieval_quality_evaluator",
        )


def test_methodology_id_rejects_empty_value() -> None:
    with pytest.raises(
        ValueError,
        match="methodology_id cannot be empty when provided",
    ):
        OperationalMeasurement(
            measurement_id="retrieval_quality",
            value=0.92,
            unit="ratio",
            methodology_id="   ",
            methodology_version="1.0",
        )


def test_methodology_version_rejects_empty_value() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "methodology_version cannot be empty when provided"
        ),
    ):
        OperationalMeasurement(
            measurement_id="retrieval_quality",
            value=0.92,
            unit="ratio",
            methodology_id="retrieval_quality_evaluator",
            methodology_version="   ",
        )


def test_methodology_id_rejects_non_string_value() -> None:
    with pytest.raises(
        TypeError,
        match="methodology_id must be a string or None",
    ):
        OperationalMeasurement(
            measurement_id="retrieval_quality",
            value=0.92,
            unit="ratio",
            methodology_id=123,
            methodology_version="1.0",
        )


def test_methodology_version_rejects_non_string_value() -> None:
    with pytest.raises(
        TypeError,
        match="methodology_version must be a string or None",
    ):
        OperationalMeasurement(
            measurement_id="retrieval_quality",
            value=0.92,
            unit="ratio",
            methodology_id="retrieval_quality_evaluator",
            methodology_version=1,
        )


def test_measurement_is_immutable() -> None:
    measurement = OperationalMeasurement(
        measurement_id="operation_duration",
        value=125.5,
        unit="milliseconds",
    )

    with pytest.raises(FrozenInstanceError):
        measurement.value = 200.0
