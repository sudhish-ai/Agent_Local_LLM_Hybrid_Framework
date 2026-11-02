# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for universal ALHF Operational Evidence quality semantics.
#
# Responsibilities:
# - Validate evidence completeness states.
# - Validate evidence integrity states.
# - Validate completeness and integrity independence.
# - Validate unknown evidence-quality semantics.
# - Validate invalid enum-value rejection.
# - Validate evidence-quality helper properties.
# - Validate immutability.
#
# Must Not:
# - Test observed workload outcomes.
# - Test OperationalOutcome behavior.
# - Test evidence validation algorithms.
# - Test repository-health diagnostics.
# - Test failure analysis or root-cause analysis.
# - Test RAG or Knowledge-specific semantics.
# - Test persistence, JSON, or JSONL behavior.

from dataclasses import FrozenInstanceError

import pytest

from alhf.core.operational_evidence.contracts.evidence_quality import (
    EvidenceCompleteness,
    EvidenceIntegrity,
    EvidenceQuality,
)


def test_create_complete_intact_evidence_quality() -> None:
    quality = EvidenceQuality(
        completeness=EvidenceCompleteness.COMPLETE,
        integrity=EvidenceIntegrity.INTACT,
    )

    assert quality.completeness == EvidenceCompleteness.COMPLETE
    assert quality.integrity == EvidenceIntegrity.INTACT


@pytest.mark.parametrize(
    "completeness",
    tuple(EvidenceCompleteness),
)
def test_all_completeness_states_are_supported(
    completeness: EvidenceCompleteness,
) -> None:
    quality = EvidenceQuality(
        completeness=completeness,
        integrity=EvidenceIntegrity.INTACT,
    )

    assert quality.completeness == completeness


@pytest.mark.parametrize(
    "integrity",
    tuple(EvidenceIntegrity),
)
def test_all_integrity_states_are_supported(
    integrity: EvidenceIntegrity,
) -> None:
    quality = EvidenceQuality(
        completeness=EvidenceCompleteness.COMPLETE,
        integrity=integrity,
    )

    assert quality.integrity == integrity


def test_complete_evidence_reports_is_complete() -> None:
    quality = EvidenceQuality(
        completeness=EvidenceCompleteness.COMPLETE,
        integrity=EvidenceIntegrity.INTACT,
    )

    assert quality.is_complete is True


@pytest.mark.parametrize(
    "completeness",
    (
        EvidenceCompleteness.PARTIAL,
        EvidenceCompleteness.UNKNOWN,
    ),
)
def test_non_complete_evidence_reports_not_complete(
    completeness: EvidenceCompleteness,
) -> None:
    quality = EvidenceQuality(
        completeness=completeness,
        integrity=EvidenceIntegrity.INTACT,
    )

    assert quality.is_complete is False


def test_partial_evidence_reports_is_partial() -> None:
    quality = EvidenceQuality(
        completeness=EvidenceCompleteness.PARTIAL,
        integrity=EvidenceIntegrity.INTACT,
    )

    assert quality.is_partial is True


@pytest.mark.parametrize(
    "completeness",
    (
        EvidenceCompleteness.COMPLETE,
        EvidenceCompleteness.UNKNOWN,
    ),
)
def test_non_partial_evidence_reports_not_partial(
    completeness: EvidenceCompleteness,
) -> None:
    quality = EvidenceQuality(
        completeness=completeness,
        integrity=EvidenceIntegrity.INTACT,
    )

    assert quality.is_partial is False


def test_intact_evidence_reports_is_intact() -> None:
    quality = EvidenceQuality(
        completeness=EvidenceCompleteness.COMPLETE,
        integrity=EvidenceIntegrity.INTACT,
    )

    assert quality.is_intact is True


@pytest.mark.parametrize(
    "integrity",
    (
        EvidenceIntegrity.DEGRADED,
        EvidenceIntegrity.UNKNOWN,
    ),
)
def test_non_intact_evidence_reports_not_intact(
    integrity: EvidenceIntegrity,
) -> None:
    quality = EvidenceQuality(
        completeness=EvidenceCompleteness.COMPLETE,
        integrity=integrity,
    )

    assert quality.is_intact is False


def test_degraded_evidence_reports_is_degraded() -> None:
    quality = EvidenceQuality(
        completeness=EvidenceCompleteness.COMPLETE,
        integrity=EvidenceIntegrity.DEGRADED,
    )

    assert quality.is_degraded is True


@pytest.mark.parametrize(
    "integrity",
    (
        EvidenceIntegrity.INTACT,
        EvidenceIntegrity.UNKNOWN,
    ),
)
def test_non_degraded_evidence_reports_not_degraded(
    integrity: EvidenceIntegrity,
) -> None:
    quality = EvidenceQuality(
        completeness=EvidenceCompleteness.COMPLETE,
        integrity=integrity,
    )

    assert quality.is_degraded is False


def test_complete_but_degraded_evidence_is_supported() -> None:
    quality = EvidenceQuality(
        completeness=EvidenceCompleteness.COMPLETE,
        integrity=EvidenceIntegrity.DEGRADED,
    )

    assert quality.is_complete is True
    assert quality.is_degraded is True
    assert quality.has_unknown_quality is False


def test_partial_but_intact_evidence_is_supported() -> None:
    quality = EvidenceQuality(
        completeness=EvidenceCompleteness.PARTIAL,
        integrity=EvidenceIntegrity.INTACT,
    )

    assert quality.is_partial is True
    assert quality.is_intact is True
    assert quality.has_unknown_quality is False


def test_unknown_completeness_reports_unknown_quality() -> None:
    quality = EvidenceQuality(
        completeness=EvidenceCompleteness.UNKNOWN,
        integrity=EvidenceIntegrity.INTACT,
    )

    assert quality.has_unknown_quality is True


def test_unknown_integrity_reports_unknown_quality() -> None:
    quality = EvidenceQuality(
        completeness=EvidenceCompleteness.COMPLETE,
        integrity=EvidenceIntegrity.UNKNOWN,
    )

    assert quality.has_unknown_quality is True


def test_both_unknown_dimensions_report_unknown_quality() -> None:
    quality = EvidenceQuality(
        completeness=EvidenceCompleteness.UNKNOWN,
        integrity=EvidenceIntegrity.UNKNOWN,
    )

    assert quality.has_unknown_quality is True


def test_known_quality_reports_no_unknown_quality() -> None:
    quality = EvidenceQuality(
        completeness=EvidenceCompleteness.COMPLETE,
        integrity=EvidenceIntegrity.INTACT,
    )

    assert quality.has_unknown_quality is False


def test_completeness_rejects_non_enum_value() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "completeness must be an instance of "
            "EvidenceCompleteness"
        ),
    ):
        EvidenceQuality(
            completeness="COMPLETE",
            integrity=EvidenceIntegrity.INTACT,
        )


def test_integrity_rejects_non_enum_value() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "integrity must be an instance of "
            "EvidenceIntegrity"
        ),
    ):
        EvidenceQuality(
            completeness=EvidenceCompleteness.COMPLETE,
            integrity="INTACT",
        )


def test_evidence_quality_is_immutable() -> None:
    quality = EvidenceQuality(
        completeness=EvidenceCompleteness.COMPLETE,
        integrity=EvidenceIntegrity.INTACT,
    )

    with pytest.raises(FrozenInstanceError):
        quality.integrity = EvidenceIntegrity.DEGRADED
