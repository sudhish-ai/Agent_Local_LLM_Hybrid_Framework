# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides the canonical ALHF capability registry.
#
# Responsibilities:
# - Register capability definitions.
# - Retrieve capability definitions.
# - Verify capability existence.
# - Enumerate registered capabilities.
#
# Must Not:
# - Perform execution.
# - Perform planning.
# - Perform orchestration.
# - Contain domain-specific business logic.
# - Perform capability selection.
#
# Architectural Position:
# - Capability layer infrastructure.
# - Concrete implementation of BaseRegistry.
# - Consumed by selection and planning components.
#
# Reuse Value:
# - Travel capabilities.
# - Healthcare capabilities.
# - Finance capabilities.
# - Future domains.
#
# Future Extensibility:
# - Capability versioning.
# - Capability dependency tracking.
# - Capability access control.
#
# Design Principle:
# Think Hard Once. Implement Many Times.

from __future__ import annotations

from src.alhf.capability.contracts.capability_definition import (
    CapabilityDefinition,
)
from src.alhf.core.registry.base_registry import (
    BaseRegistry,
)


class CapabilityRegistry(
    BaseRegistry[
        CapabilityDefinition,
        str,
    ]
):
    """
    Registry for ALHF capabilities.
    """

    def __init__(
        self,
    ) -> None:
        super().__init__(
            key_resolver=lambda capability:
            capability.capability_id,
        )

    def _validate_registration(
        self,
        entity: CapabilityDefinition,
        identifier: str,
    ) -> None:
        """
        Capability-specific validation hook.

        Future validation rules may be
        added here.
        """

        if not identifier.strip():
            raise ValueError(
                "Capability identifier cannot be empty."
            )
