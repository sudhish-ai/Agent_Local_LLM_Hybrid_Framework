# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Resolves capabilities associated with an intent.
#
# Responsibilities:
# - Resolve capabilities for an intent.
# - Query IntentCapabilityRegistry.
# - Translate capability identifiers into
#   CapabilityDefinition objects.
# - Return runtime-ready capabilities.
#
# Must Not:
# - Perform capability selection.
# - Perform planning.
# - Perform orchestration.
# - Perform execution.
#
# Architectural Position:
# - Knowledge resolution layer.
# - Consumed by CapabilityRuntime.
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
from src.alhf.intent.intent_capability_registry import (
    IntentCapabilityRegistry,
)


class IntentCapabilityResolver:
    """
    Resolves capabilities from intent mappings.
    """

    def __init__(
        self,
        capability_registry: CapabilityRegistry,
        intent_capability_registry: (
            IntentCapabilityRegistry
        ),
    ) -> None:
        self._capability_registry = (
            capability_registry
        )

        self._intent_capability_registry = (
            intent_capability_registry
        )

    def resolve(
        self,
        intent_id: str,
    ) -> tuple[
        CapabilityDefinition,
        ...
    ]:
        """
        Resolve capabilities for an intent.
        """

        mapping = (
            self._intent_capability_registry
            .get(
                intent_id,
            )
        )

        resolved_capabilities: list[
            CapabilityDefinition
        ] = []

        for capability_id in (
            mapping.capability_ids
        ):
            capability = (
                self._capability_registry
                .get(
                    capability_id,
                )
            )

            resolved_capabilities.append(
                capability,
            )

        return tuple(
            resolved_capabilities,
        )
