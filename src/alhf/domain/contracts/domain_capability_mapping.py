# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the relationship between domains
# and capabilities.
#
# Responsibilities:
# - Represent domain-to-capability mappings.
# - Define capability ownership per domain.
# - Provide immutable relationship metadata.
#
# Must Not:
# - Perform capability selection.
# - Perform planning.
# - Perform execution.
# - Perform orchestration.
# - Depend on runtime components.
#
# Architectural Position:
# - First intelligence relationship layer.
# - Connects domains to capabilities.
# - Acts as foundational knowledge structure.
#
# Reuse Value:
# - Travel → Hotel Search
# - Travel → Flight Search
# - Healthcare → Provider Search
# - Healthcare → Appointment Booking
# - Future domain onboarding
#
# Future Extensibility:
# - Confidence scoring.
# - Capability priorities.
# - Conditional routing.
# - Outcome-based ranking.
#
# Design Principle:
# Think Hard Once. Implement Many Times.

from __future__ import annotations

from dataclasses import dataclass


@dataclass(
    frozen=True,
    slots=True,
)
class DomainCapabilityMapping:
    """
    Defines which capabilities belong
    to a domain.
    """

    domain_id: str

    capability_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        """
        Validate mapping contract.
        """

        if not self.domain_id.strip():
            raise ValueError(
                "domain_id cannot be empty."
            )

        if not self.capability_ids:
            raise ValueError(
                "At least one capability "
                "must be provided."
            )

        for capability_id in self.capability_ids:

            if not capability_id.strip():
                raise ValueError(
                    "capability_id cannot be empty."
                )

    @property
    def capability_count(
        self,
    ) -> int:
        """
        Number of mapped capabilities.
        """

        return len(
            self.capability_ids
        )

    def contains_capability(
        self,
        capability_id: str,
    ) -> bool:
        """
        Determine whether a capability
        belongs to this domain.
        """

        return (
            capability_id
            in self.capability_ids
        )
