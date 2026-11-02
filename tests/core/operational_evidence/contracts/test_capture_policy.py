# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the universal ALHF CapturePolicy contract.
#
# Responsibilities:
# - Validate capture-policy identity and version semantics.
# - Validate all supported capture-completeness models.
# - Validate all supported evidence-detail levels.
# - Validate abnormal-detail configuration.
# - Validate text normalization.
# - Validate invalid identity and version values.
# - Validate invalid enum values.
# - Validate strict Boolean semantics.
# - Validate immutability.
#
# Must Not:
# - Test sampling or aggregation algorithms.
# - Test evidence quality or integrity.
# - Test retention or durability behavior.
# - Test RAG or Knowledge-specific behavior.
# - Test persistence, JSON, or JSONL behavior.
# - Test provider-specific capture mechanisms.

from dataclasses import FrozenInstanceError

import pytest

from alhf.core.operational_evidence.contracts.capture_policy import (
    CaptureCompleteness,
    CaptureDetailLevel,
    CapturePolicy,
)


def test_create_capture_policy() -> None:
    policy = CapturePolicy(
        policy_id="standard-production",
        policy_version="1.0",
        completeness=CaptureCompleteness.EXHAUSTIVE,
        detail_level=CaptureDetailLevel.BASELINE,
        abnormal_detail_enabled=True,
    )

    assert policy.policy_id == "standard-production"
    assert policy.policy_version == "1.0"
    assert policy.completeness == CaptureCompleteness.EXHAUSTIVE
    assert policy.detail_level == CaptureDetailLevel.BASELINE
    assert policy.abnormal_detail_enabled is True


def test_capture_policy_text_values_are_normalized() -> None:
    policy = CapturePolicy(
        policy_id="  standard-production  ",
        policy_version="  1.0  ",
        completeness=CaptureCompleteness.EXHAUSTIVE,
        detail_level=CaptureDetailLevel.BASELINE,
        abnormal_detail_enabled=True,
    )

    assert policy.policy_id == "standard-production"
    assert policy.policy_version == "1.0"


@pytest.mark.parametrize(
    "completeness",
    tuple(CaptureCompleteness),
)
def test_all_capture_completeness_models_are_supported(
    completeness: CaptureCompleteness,
) -> None:
    policy = CapturePolicy(
        policy_id="capture-policy",
        policy_version="1.0",
        completeness=completeness,
        detail_level=CaptureDetailLevel.BASELINE,
        abnormal_detail_enabled=False,
    )

    assert policy.completeness == completeness


@pytest.mark.parametrize(
    "detail_level",
    tuple(CaptureDetailLevel),
)
def test_all_capture_detail_levels_are_supported(
    detail_level: CaptureDetailLevel,
) -> None:
    policy = CapturePolicy(
        policy_id="capture-policy",
        policy_version="1.0",
        completeness=CaptureCompleteness.EXHAUSTIVE,
        detail_level=detail_level,
        abnormal_detail_enabled=False,
    )

    assert policy.detail_level == detail_level


def test_abnormal_detail_can_be_enabled() -> None:
    policy = CapturePolicy(
        policy_id="capture-policy",
        policy_version="1.0",
        completeness=CaptureCompleteness.EXHAUSTIVE,
        detail_level=CaptureDetailLevel.BASELINE,
        abnormal_detail_enabled=True,
    )

    assert policy.abnormal_detail_enabled is True


def test_abnormal_detail_can_be_disabled() -> None:
    policy = CapturePolicy(
        policy_id="capture-policy",
        policy_version="1.0",
        completeness=CaptureCompleteness.AGGREGATED,
        detail_level=CaptureDetailLevel.BASELINE,
        abnormal_detail_enabled=False,
    )

    assert policy.abnormal_detail_enabled is False


@pytest.mark.parametrize(
    "policy_id",
    (
        "",
        "   ",
    ),
)
def test_policy_id_rejects_empty_value(
    policy_id: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="policy_id cannot be empty",
    ):
        CapturePolicy(
            policy_id=policy_id,
            policy_version="1.0",
            completeness=CaptureCompleteness.EXHAUSTIVE,
            detail_level=CaptureDetailLevel.BASELINE,
            abnormal_detail_enabled=True,
        )


def test_policy_id_rejects_non_string_value() -> None:
    with pytest.raises(
        TypeError,
        match="policy_id must be a string",
    ):
        CapturePolicy(
            policy_id=123,
            policy_version="1.0",
            completeness=CaptureCompleteness.EXHAUSTIVE,
            detail_level=CaptureDetailLevel.BASELINE,
            abnormal_detail_enabled=True,
        )


@pytest.mark.parametrize(
    "policy_version",
    (
        "",
        "   ",
    ),
)
def test_policy_version_rejects_empty_value(
    policy_version: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="policy_version cannot be empty",
    ):
        CapturePolicy(
            policy_id="capture-policy",
            policy_version=policy_version,
            completeness=CaptureCompleteness.EXHAUSTIVE,
            detail_level=CaptureDetailLevel.BASELINE,
            abnormal_detail_enabled=True,
        )


def test_policy_version_rejects_non_string_value() -> None:
    with pytest.raises(
        TypeError,
        match="policy_version must be a string",
    ):
        CapturePolicy(
            policy_id="capture-policy",
            policy_version=1,
            completeness=CaptureCompleteness.EXHAUSTIVE,
            detail_level=CaptureDetailLevel.BASELINE,
            abnormal_detail_enabled=True,
        )


def test_completeness_rejects_non_enum_value() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "completeness must be an instance of "
            "CaptureCompleteness"
        ),
    ):
        CapturePolicy(
            policy_id="capture-policy",
            policy_version="1.0",
            completeness="EXHAUSTIVE",
            detail_level=CaptureDetailLevel.BASELINE,
            abnormal_detail_enabled=True,
        )


def test_detail_level_rejects_non_enum_value() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "detail_level must be an instance of "
            "CaptureDetailLevel"
        ),
    ):
        CapturePolicy(
            policy_id="capture-policy",
            policy_version="1.0",
            completeness=CaptureCompleteness.EXHAUSTIVE,
            detail_level="BASELINE",
            abnormal_detail_enabled=True,
        )


@pytest.mark.parametrize(
    "invalid_value",
    (
        0,
        1,
        "true",
        "false",
        None,
    ),
)
def test_abnormal_detail_enabled_requires_boolean(
    invalid_value: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="abnormal_detail_enabled must be a bool",
    ):
        CapturePolicy(
            policy_id="capture-policy",
            policy_version="1.0",
            completeness=CaptureCompleteness.EXHAUSTIVE,
            detail_level=CaptureDetailLevel.BASELINE,
            abnormal_detail_enabled=invalid_value,
        )


@pytest.mark.parametrize(
    "policy_version",
    (
        "1",
        "1.0",
        "1.0.0",
        "v1",
        "2026-10",
        "custom-version",
    ),
)
def test_policy_version_is_not_restricted_to_one_versioning_scheme(
    policy_version: str,
) -> None:
    policy = CapturePolicy(
        policy_id="capture-policy",
        policy_version=policy_version,
        completeness=CaptureCompleteness.EXHAUSTIVE,
        detail_level=CaptureDetailLevel.BASELINE,
        abnormal_detail_enabled=False,
    )

    assert policy.policy_version == policy_version


def test_capture_policy_is_immutable() -> None:
    policy = CapturePolicy(
        policy_id="capture-policy",
        policy_version="1.0",
        completeness=CaptureCompleteness.EXHAUSTIVE,
        detail_level=CaptureDetailLevel.BASELINE,
        abnormal_detail_enabled=True,
    )

    with pytest.raises(FrozenInstanceError):
        policy.detail_level = CaptureDetailLevel.DIAGNOSTIC
