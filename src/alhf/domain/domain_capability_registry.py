# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides the canonical ALHF domain-capability
# relationship registry.
#
# Responsibilities:
# - Register domain-capability mappings.
# - Retrieve domain-capability mappings.
# - Verify mapping existence.
# - Enumerate registered mappings.
#
# Must Not:
# - Perform capability resolution.
# - Perform planning.
# - Perform orchestration.
# - Perform execution.
# - Contain domain business logic.
#
# Architectural Position:
# - Relationship registry.
# - Stores DomainCapabilityMapping instances.
# - Bridges domains and capabilities.
#
# Reuse Value:
# - Travel -> Hotel Search
# - Travel -> Flight Search
# - Healthcare -> Provider Search
#
# Future Extensibility:
# - Mapping validation policies.
# - Version-aware mappings.
# - Context-aware mappings.
#
# Design Principle:
# Think Hard Once. Implement Many Times.

from __future__ import annotations

from alhf.core.registry.base_registry import (
    BaseRegistry,
)
from alhf.domain.contracts.domain_capability_mapping import (
    DomainCapabilityMapping,
)


class DomainCapabilityRegistry(
    BaseRegistry[
        DomainCapabilityMapping,
        str,
    ]
):
    """
    Registry for domain-capability mappings.
    """

    def __init__(
        self,
    ) -> None:
        super().__init__(
            key_resolver=lambda mapping:
            mapping.domain_id,
        )

    def _validate_registration(
        self,
        entity: DomainCapabilityMapping,
        identifier: str,
    ) -> None:
        """
        Registry-specific validation hook.
        """

        if not identifier.strip():
            raise ValueError(
                "Domain identifier cannot be empty."
            )
