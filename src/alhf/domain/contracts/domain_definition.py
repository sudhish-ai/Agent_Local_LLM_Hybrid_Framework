# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides the canonical ALHF domain contract.
#
# Responsibilities:
# - Represent a domain definition.
# - Provide a stable domain identifier.
# - Provide human-readable domain metadata.
# - Act as the registration unit for DomainRegistry.
#
# Must Not:
# - Contain domain execution logic.
# - Contain planning logic.
# - Contain workflow definitions.
# - Contain capability resolution logic.
# - Contain persistence logic.
#
# Architectural Position:
# - Core domain contract.
# - Registered by DomainRegistry.
# - Consumed by planners.
# - Consumed by outcome runtime components.
#
# Reuse Value:
# - Common domain representation across ALHF.
# - Prevents domain-specific implementations.
# - Reduces future contract proliferation.
#
# Future Extensibility:
# - Supports metadata expansion.
# - Supports version-aware domain evolution.
# - Supports future domain-pack loading.
#
# Design Principle:
# Think Hard Once. Implement Many Times.

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Mapping


@dataclass(frozen=True, slots=True)
class DomainDefinition:
    """
    Canonical ALHF domain definition.

    Examples:
        Software Engineering
        Travel
        Healthcare
        Finance
        Insurance
    """

    domain_id: str
    domain_name: str
    description: str
    version: str = "1.0"

    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        """
        Validate required fields.
        """

        if not self.domain_id.strip():
            raise ValueError(
                "domain_id cannot be empty."
            )

        if not self.domain_name.strip():
            raise ValueError(
                "domain_name cannot be empty."
            )

        if not self.description.strip():
            raise ValueError(
                "description cannot be empty."
            )
