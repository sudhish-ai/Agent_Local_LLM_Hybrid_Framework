# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides the canonical ALHF capability contract.
#
# Responsibilities:
# - Represent a reusable capability.
# - Provide a stable capability identifier.
# - Provide capability metadata.
# - Act as the registration unit for CapabilityRegistry.
#
# Must Not:
# - Contain execution logic.
# - Contain workflow logic.
# - Contain planning logic.
# - Contain domain detection logic.
# - Contain orchestration logic.
#
# Architectural Position:
# - Core capability contract.
# - Registered by CapabilityRegistry.
# - Selected by capability selection logic.
# - Consumed by workflow planning.
#
# Reuse Value:
# - Travel capabilities.
# - Healthcare capabilities.
# - Finance capabilities.
# - Future domains.
#
# Future Extensibility:
# - Capability tags.
# - Capability permissions.
# - Capability dependencies.
# - Capability versioning.
#
# Design Principle:
# Think Hard Once. Implement Many Times.

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Mapping


@dataclass(
    frozen=True,
    slots=True,
)
class CapabilityDefinition:
    """
    Canonical ALHF capability definition.

    Examples:

    Hotel Search

    Flight Search

    Provider Search

    Appointment Scheduling
    """

    capability_id: str

    capability_name: str

    description: str

    version: str = "1.0"

    metadata: Mapping[str, Any] = field(
        default_factory=dict,
    )

    def __post_init__(self) -> None:
        """
        Validate capability contract.
        """

        if not self.capability_id.strip():
            raise ValueError(
                "capability_id cannot be empty."
            )

        if not self.capability_name.strip():
            raise ValueError(
                "capability_name cannot be empty."
            )

        if not self.description.strip():
            raise ValueError(
                "description cannot be empty."
            )
