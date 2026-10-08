# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides the canonical ALHF domain registry.
#
# Responsibilities:
# - Register domain definitions.
# - Retrieve domain definitions.
# - Verify domain existence.
# - Provide domain enumeration.
#
# Must Not:
# - Perform planning.
# - Perform orchestration.
# - Perform capability resolution.
# - Load domains from files.
# - Contain domain-specific business logic.
#
# Architectural Position:
# - Domain layer infrastructure.
# - First concrete implementation of BaseRegistry.
# - Consumed by planners, loaders, and runtime components.
#
# Reuse Value:
# - Centralized domain registration.
# - Prevents duplicate domain management logic.
#
# Future Extensibility:
# - Domain loaders.
# - Dynamic domain discovery.
# - Domain version management.
# - Domain validation policies.
#
# Design Principle:
# Think Hard Once. Implement Many Times.

from __future__ import annotations

from alhf.core.registry.base_registry import BaseRegistry
from alhf.domain.contracts.domain_definition import (
    DomainDefinition,
)


class DomainRegistry(
    BaseRegistry[
        DomainDefinition,
        str,
    ]
):
    """
    Registry for ALHF domains.
    """

    def __init__(self) -> None:
        super().__init__(
            key_resolver=lambda domain: domain.domain_id,
        )

    def _validate_registration(
        self,
        entity: DomainDefinition,
        identifier: str,
    ) -> None:
        """
        Domain-specific validation hook.

        Future validation rules can be added here.
        """

        if not identifier.strip():
            raise ValueError(
                "Domain identifier cannot be empty."
            )
