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
# - Define mandatory domain capabilities.
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

    mandatory_capability_ids: tuple[
        str,
        ...
    ] = ()

    def __post_init__(
        self,
    ) -> None:
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

        for capability_id in (
            self.capability_ids
        ):
            if not capability_id.strip():
                raise ValueError(
                    "capability_id cannot be empty."
                )

        for capability_id in (
            self.mandatory_capability_ids
        ):
            if not capability_id.strip():
                raise ValueError(
                    "mandatory capability "
                    "cannot be empty."
                )

            if capability_id not in (
                self.capability_ids
            ):
                raise ValueError(
                    "Mandatory capability "
                    f"'{capability_id}' "
                    "must exist in "
                    "capability_ids."
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

    @property
    def mandatory_capability_count(
        self,
    ) -> int:
        """
        Number of mandatory capabilities.
        """

        return len(
            self.mandatory_capability_ids
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

    def is_mandatory(
        self,
        capability_id: str,
    ) -> bool:
        """
        Determine whether a capability
        is mandatory for the domain.
        """

        return (
            capability_id
            in self.mandatory_capability_ids
        )
