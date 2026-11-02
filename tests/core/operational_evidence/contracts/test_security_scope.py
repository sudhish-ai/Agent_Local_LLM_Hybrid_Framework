# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the universal ALHF SecurityScope contract.
#
# Responsibilities:
# - Validate security-scope identity preservation.
# - Validate security-policy reference preservation.
# - Validate security-scope normalization.
# - Validate security-policy reference normalization.
# - Validate invalid security-scope values.
# - Validate invalid security-policy references.
# - Validate immutability.
#
# Must Not:
# - Test authorization or access-control decisions.
# - Test security-policy evaluation.
# - Test credentials, secrets, or authentication tokens.
# - Test organization-specific classification schemes.
# - Test RAG or Knowledge-specific security semantics.
# - Test persistence, JSON, or JSONL behavior.
# - Test provider-specific authorization behavior.

from dataclasses import FrozenInstanceError

import pytest

from alhf.core.operational_evidence.contracts.security_scope import (
    SecurityScope,
)


def test_create_security_scope() -> None:
    security_scope = SecurityScope(
        scope_id="enterprise-scope-001",
        policy_ref="operational-evidence-policy-v1",
    )

    assert security_scope.scope_id == "enterprise-scope-001"
    assert (
        security_scope.policy_ref
        == "operational-evidence-policy-v1"
    )


def test_security_scope_values_are_whitespace_normalized() -> None:
    security_scope = SecurityScope(
        scope_id="  enterprise-scope-001  ",
        policy_ref="  operational-evidence-policy-v1  ",
    )

    assert security_scope.scope_id == "enterprise-scope-001"
    assert (
        security_scope.policy_ref
        == "operational-evidence-policy-v1"
    )


@pytest.mark.parametrize(
    "scope_id",
    (
        "",
        "   ",
    ),
)
def test_scope_id_rejects_empty_value(
    scope_id: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="scope_id cannot be empty",
    ):
        SecurityScope(
            scope_id=scope_id,
            policy_ref="operational-evidence-policy-v1",
        )


def test_scope_id_rejects_non_string_value() -> None:
    with pytest.raises(
        TypeError,
        match="scope_id must be a string",
    ):
        SecurityScope(
            scope_id=123,
            policy_ref="operational-evidence-policy-v1",
        )


@pytest.mark.parametrize(
    "policy_ref",
    (
        "",
        "   ",
    ),
)
def test_policy_ref_rejects_empty_value(
    policy_ref: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="policy_ref cannot be empty",
    ):
        SecurityScope(
            scope_id="enterprise-scope-001",
            policy_ref=policy_ref,
        )


def test_policy_ref_rejects_non_string_value() -> None:
    with pytest.raises(
        TypeError,
        match="policy_ref must be a string",
    ):
        SecurityScope(
            scope_id="enterprise-scope-001",
            policy_ref=123,
        )


def test_different_scopes_can_reference_same_policy() -> None:
    first_scope = SecurityScope(
        scope_id="enterprise-scope-001",
        policy_ref="operational-evidence-policy-v1",
    )
    second_scope = SecurityScope(
        scope_id="enterprise-scope-002",
        policy_ref="operational-evidence-policy-v1",
    )

    assert first_scope.scope_id != second_scope.scope_id
    assert first_scope.policy_ref == second_scope.policy_ref


def test_same_scope_can_reference_different_policy_versions() -> None:
    first_scope = SecurityScope(
        scope_id="enterprise-scope-001",
        policy_ref="operational-evidence-policy-v1",
    )
    second_scope = SecurityScope(
        scope_id="enterprise-scope-001",
        policy_ref="operational-evidence-policy-v2",
    )

    assert first_scope.scope_id == second_scope.scope_id
    assert first_scope.policy_ref != second_scope.policy_ref


def test_security_scope_equality_uses_scope_and_policy() -> None:
    first_scope = SecurityScope(
        scope_id="enterprise-scope-001",
        policy_ref="operational-evidence-policy-v1",
    )
    second_scope = SecurityScope(
        scope_id="enterprise-scope-001",
        policy_ref="operational-evidence-policy-v1",
    )

    assert first_scope == second_scope


def test_security_scope_is_immutable() -> None:
    security_scope = SecurityScope(
        scope_id="enterprise-scope-001",
        policy_ref="operational-evidence-policy-v1",
    )

    with pytest.raises(FrozenInstanceError):
        security_scope.policy_ref = "different-policy"
