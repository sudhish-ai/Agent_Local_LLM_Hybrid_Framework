# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Selects capabilities required to achieve
# a customer outcome.
#
# Responsibilities:
# - Select intent-required capabilities.
# - Add domain-mandatory capabilities.
# - Remove duplicates.
# - Preserve capability ordering.
# - Return selected CapabilityDefinitions.
#
# Must Not:
# - Perform workflow planning.
# - Perform orchestration.
# - Perform execution.
# - Perform routing.
# - Perform semantic ranking.
# - Perform AI-based reasoning.
#
# Architectural Position:
# - First capability intelligence layer.
# - Consumes intent/domain knowledge.
# - Produces selected capabilities for planning.
#
# V2 Behavior:
# Selected Capabilities =
# Intent Capabilities +
# Domain Mandatory Capabilities
#
# Future Extensibility:
# - Semantic capability expansion.
# - Capability ranking.
# - Historical outcome optimization.
# - Learning-based recommendations.
#
# Design Principle:
# Think Hard Once. Implement Many Times.

from __future__ import annotations

from src.alhf.capability.contracts.capability_definition import (
    CapabilityDefinition,
)
from src.alhf.domain.contracts.domain_capability_mapping import (
    DomainCapabilityMapping,
)


class CapabilitySelectionEngine:
    """
    Select capabilities required
    for planning.
    """

    def select(
        self,
        intent_capabilities: tuple[
            CapabilityDefinition,
            ...
        ],
        domain_mapping: (
            DomainCapabilityMapping
        ),
        domain_capabilities: tuple[
            CapabilityDefinition,
            ...
        ],
    ) -> tuple[
        CapabilityDefinition,
        ...
    ]:
        """
        Select capabilities for planning.

        V2:
        Intent Capabilities
        +
        Domain Mandatory Capabilities
        """

        selected: list[
            CapabilityDefinition
        ] = []

        selected_ids: set[str] = set()

        for capability in (
            intent_capabilities
        ):
            if (
                capability.capability_id
                not in selected_ids
            ):
                selected.append(
                    capability
                )

                selected_ids.add(
                    capability.capability_id
                )

        domain_capability_lookup = {
            capability.capability_id:
            capability
            for capability in (
                domain_capabilities
            )
        }

        for capability_id in (
            domain_mapping
            .mandatory_capability_ids
        ):
            capability = (
                domain_capability_lookup.get(
                    capability_id
                )
            )

            if capability is None:
                raise ValueError(
                    "Mandatory capability "
                    f"'{capability_id}' "
                    "not found in domain "
                    "capability definitions."
                )

            if (
                capability.capability_id
                not in selected_ids
            ):
                selected.append(
                    capability
                )

                selected_ids.add(
                    capability.capability_id
                )

        return tuple(
            selected
        )
