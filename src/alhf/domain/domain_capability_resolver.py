# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Resolves capabilities belonging to a domain.
#
# Responsibilities:
# - Resolve capabilities for a domain.
# - Translate relationships into runtime objects.
# - Provide capability lookup services.
#
# Must Not:
# - Perform capability selection.
# - Perform workflow planning.
# - Perform orchestration.
# - Perform execution.
#
# Architectural Position:
# - Runtime intelligence layer.
# - Consumes relationship registries.
# - Produces capability definitions.
#
# Design Principle:
# Think Hard Once. Implement Many Times.

from __future__ import annotations

from src.alhf.capability.capability_registry import (
    CapabilityRegistry,
)
from src.alhf.capability.contracts.capability_definition import (
    CapabilityDefinition,
)
from src.alhf.domain.domain_capability_registry import (
    DomainCapabilityRegistry,
)


class DomainCapabilityResolver:
    """
    Resolves capabilities for a domain.
    """

    def __init__(
        self,
        capability_registry: CapabilityRegistry,
        domain_capability_registry: (
            DomainCapabilityRegistry
        ),
    ) -> None:
        self._capability_registry = (
            capability_registry
        )
        self._domain_capability_registry = (
            domain_capability_registry
        )

    def resolve(
        self,
        domain_id: str,
    ) -> tuple[
        CapabilityDefinition,
        ...
    ]:
        """
        Resolve capabilities associated
        with a domain.
        """

        mapping = (
            self._domain_capability_registry.get(
                domain_id
            )
        )

        resolved_capabilities = []

        for capability_id in (
            mapping.capability_ids
        ):
            capability = (
                self._capability_registry.get(
                    capability_id
                )
            )

            resolved_capabilities.append(
                capability
            )

        return tuple(
            resolved_capabilities
        )
