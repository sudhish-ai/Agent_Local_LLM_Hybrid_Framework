# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the universal ALHF DiagnosticReference contract.
#
# Responsibilities:
# - Validate diagnostic artifact identity.
# - Validate all supported diagnostic kinds.
# - Validate producer identity.
# - Validate optional media-type semantics.
# - Validate text normalization.
# - Validate invalid required values.
# - Validate invalid diagnostic kinds.
# - Validate optional media-type constraints.
# - Validate immutability.
#
# Must Not:
# - Test diagnostic artifact contents.
# - Test physical diagnostic storage locations.
# - Test RAG or Knowledge-specific diagnostics.
# - Test persistence, JSON, or JSONL behavior.
# - Test authorization or retention behavior.
# - Test failure analysis or root-cause analysis.

from dataclasses import FrozenInstanceError

import pytest

from alhf.core.operational_evidence.contracts.diagnostic_reference import (
    DiagnosticKind,
    DiagnosticReference,
)


def test_create_diagnostic_reference_without_media_type() -> None:
    reference = DiagnosticReference(
        diagnostic_id="diagnostic-001",
        diagnostic_kind=DiagnosticKind.ERROR_DETAIL,
        producer="test-component",
    )

    assert reference.diagnostic_id == "diagnostic-001"
    assert reference.diagnostic_kind == DiagnosticKind.ERROR_DETAIL
    assert reference.producer == "test-component"
    assert reference.media_type is None


def test_create_diagnostic_reference_with_media_type() -> None:
    reference = DiagnosticReference(
        diagnostic_id="diagnostic-001",
        diagnostic_kind=DiagnosticKind.ERROR_DETAIL,
        producer="test-component",
        media_type="text/plain",
    )

    assert reference.diagnostic_id == "diagnostic-001"
    assert reference.diagnostic_kind == DiagnosticKind.ERROR_DETAIL
    assert reference.producer == "test-component"
    assert reference.media_type == "text/plain"


@pytest.mark.parametrize(
    "diagnostic_kind",
    tuple(DiagnosticKind),
)
def test_all_diagnostic_kinds_are_supported(
    diagnostic_kind: DiagnosticKind,
) -> None:
    reference = DiagnosticReference(
        diagnostic_id="diagnostic-001",
        diagnostic_kind=diagnostic_kind,
        producer="test-component",
    )

    assert reference.diagnostic_kind == diagnostic_kind


def test_required_text_values_are_whitespace_normalized() -> None:
    reference = DiagnosticReference(
        diagnostic_id="  diagnostic-001  ",
        diagnostic_kind=DiagnosticKind.PROVIDER_DETAIL,
        producer="  provider-adapter  ",
    )

    assert reference.diagnostic_id == "diagnostic-001"
    assert reference.producer == "provider-adapter"


def test_media_type_is_whitespace_normalized() -> None:
    reference = DiagnosticReference(
        diagnostic_id="diagnostic-001",
        diagnostic_kind=DiagnosticKind.OUTPUT_SAMPLE,
        producer="test-component",
        media_type="  application/json  ",
    )

    assert reference.media_type == "application/json"


@pytest.mark.parametrize(
    "diagnostic_id",
    (
        "",
        "   ",
    ),
)
def test_diagnostic_id_rejects_empty_value(
    diagnostic_id: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="diagnostic_id cannot be empty",
    ):
        DiagnosticReference(
            diagnostic_id=diagnostic_id,
            diagnostic_kind=DiagnosticKind.ERROR_DETAIL,
            producer="test-component",
        )


def test_diagnostic_id_rejects_non_string_value() -> None:
    with pytest.raises(
        TypeError,
        match="diagnostic_id must be a string",
    ):
        DiagnosticReference(
            diagnostic_id=123,
            diagnostic_kind=DiagnosticKind.ERROR_DETAIL,
            producer="test-component",
        )


@pytest.mark.parametrize(
    "producer",
    (
        "",
        "   ",
    ),
)
def test_producer_rejects_empty_value(
    producer: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="producer cannot be empty",
    ):
        DiagnosticReference(
            diagnostic_id="diagnostic-001",
            diagnostic_kind=DiagnosticKind.ERROR_DETAIL,
            producer=producer,
        )


def test_producer_rejects_non_string_value() -> None:
    with pytest.raises(
        TypeError,
        match="producer must be a string",
    ):
        DiagnosticReference(
            diagnostic_id="diagnostic-001",
            diagnostic_kind=DiagnosticKind.ERROR_DETAIL,
            producer=123,
        )


def test_diagnostic_kind_rejects_non_enum_value() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "diagnostic_kind must be an instance of DiagnosticKind"
        ),
    ):
        DiagnosticReference(
            diagnostic_id="diagnostic-001",
            diagnostic_kind="ERROR_DETAIL",
            producer="test-component",
        )


@pytest.mark.parametrize(
    "media_type",
    (
        "",
        "   ",
    ),
)
def test_media_type_rejects_empty_value_when_provided(
    media_type: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="media_type cannot be empty when provided",
    ):
        DiagnosticReference(
            diagnostic_id="diagnostic-001",
            diagnostic_kind=DiagnosticKind.ERROR_DETAIL,
            producer="test-component",
            media_type=media_type,
        )


def test_media_type_rejects_non_string_value() -> None:
    with pytest.raises(
        TypeError,
        match="media_type must be a string or None",
    ):
        DiagnosticReference(
            diagnostic_id="diagnostic-001",
            diagnostic_kind=DiagnosticKind.ERROR_DETAIL,
            producer="test-component",
            media_type=123,
        )


def test_different_diagnostic_kinds_preserve_same_identity() -> None:
    error_reference = DiagnosticReference(
        diagnostic_id="diagnostic-001",
        diagnostic_kind=DiagnosticKind.ERROR_DETAIL,
        producer="test-component",
    )
    performance_reference = DiagnosticReference(
        diagnostic_id="diagnostic-001",
        diagnostic_kind=DiagnosticKind.PERFORMANCE_DETAIL,
        producer="test-component",
    )

    assert (
        error_reference.diagnostic_id
        == performance_reference.diagnostic_id
    )
    assert (
        error_reference.diagnostic_kind
        != performance_reference.diagnostic_kind
    )


def test_diagnostic_reference_equality_uses_all_fields() -> None:
    first_reference = DiagnosticReference(
        diagnostic_id="diagnostic-001",
        diagnostic_kind=DiagnosticKind.ERROR_DETAIL,
        producer="test-component",
        media_type="text/plain",
    )
    second_reference = DiagnosticReference(
        diagnostic_id="diagnostic-001",
        diagnostic_kind=DiagnosticKind.ERROR_DETAIL,
        producer="test-component",
        media_type="text/plain",
    )

    assert first_reference == second_reference


def test_diagnostic_reference_is_immutable() -> None:
    reference = DiagnosticReference(
        diagnostic_id="diagnostic-001",
        diagnostic_kind=DiagnosticKind.ERROR_DETAIL,
        producer="test-component",
    )

    with pytest.raises(FrozenInstanceError):
        reference.producer = "changed-component"
