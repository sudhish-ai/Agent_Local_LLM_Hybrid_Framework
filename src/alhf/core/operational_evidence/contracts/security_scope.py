# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the universal security-scope contract used by the
# ALHF Operational Evidence Foundation.
#
# Problem Solved:
# Operational Evidence can contain sensitive execution identities,
# governed references, failure information, measurements, and diagnostic
# relationships.
#
# Evidence consumers must therefore be able to determine the governed
# security scope and applicable protection policy without coupling the
# universal Operational Evidence Foundation to a tenant model, domain,
# identity provider, or infrastructure-specific authorization system.
#
# Responsibilities:
# - Identify the governed security scope associated with evidence.
# - Preserve the applicable security-policy reference.
# - Normalize and validate security-scope identifiers.
# - Provide immutable, storage-independent security-scope semantics.
# - Support future authorization-aware evidence persistence and queries.
#
# Must Not:
# - Authorize or deny evidence access.
# - Evaluate security policies.
# - Contain user credentials or authentication tokens.
# - Contain secrets or connection information.
# - Hard-code tenant, customer, organization, or domain semantics.
# - Define an organization-specific data-classification taxonomy.
# - Contain RAG or Knowledge-specific semantics.
# - Contain provider-specific authorization behavior.
# - Contain persistence, JSON, or JSONL behavior.
# - Contain arbitrary metadata or diagnostic payloads.
#
# Architectural Position:
# - Universal ALHF Operational Evidence contract.
# - Carries security-scope references without implementing authorization.
# - Independent from identity providers and persistence providers.
#
# Reuse Value:
# - Knowledge Foundation operational evidence.
# - Multi-agent operational evidence.
# - V3 operational evidence.
# - Authorization-aware failure analysis and RCA.
# - Governed corrective-action recommendations.
# - Human-in-the-loop remediation.
# - Post-remediation validation.
#
# Future Extensibility:
# - Concrete policy evaluation remains outside this contract.
# - Provider-specific access-control mechanisms remain behind adapters.
# - Organizational classification schemes remain independently governed.
# - Derived findings, predictions, recommendations, and actions can reuse
#   the same scope semantics without weakening access controls.

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SecurityScope:
    """
    Immutable security scope for ALHF Operational Evidence.

    scope_id:
        Stable identifier of the governed security boundary associated
        with the evidence.

    policy_ref:
        Stable reference to the security or disclosure policy applicable
        to the evidence.

    The contract identifies governance context only. It does not evaluate
    authorization, disclose protected information, or define how policies
    are implemented.
    """

    scope_id: str
    policy_ref: str

    def __post_init__(self) -> None:
        scope_id = self._normalize_required_text(
            value=self.scope_id,
            field_name="scope_id",
        )
        policy_ref = self._normalize_required_text(
            value=self.policy_ref,
            field_name="policy_ref",
        )

        object.__setattr__(
            self,
            "scope_id",
            scope_id,
        )
        object.__setattr__(
            self,
            "policy_ref",
            policy_ref,
        )

    @staticmethod
    def _normalize_required_text(
        *,
        value: str,
        field_name: str,
    ) -> str:
        """Validate and normalize a required security-scope value."""

        if not isinstance(value, str):
            raise TypeError(
                f"{field_name} must be a string"
            )

        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError(
                f"{field_name} cannot be empty"
            )

        return normalized_value
