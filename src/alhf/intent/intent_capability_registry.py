# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Registry for IntentCapabilityMapping objects.
#
# Responsibilities:
# - Register mappings.
# - Resolve mappings by intent.
# - Provide intent capability lookup.
#
# Must Not:
# - Contain planning logic.
# - Contain execution logic.
# - Contain orchestration logic.
# - Contain persistence logic.
#
# Architectural Position:
# - Knowledge layer registry.
# - Consumed by IntentCapabilityResolver.
#
# Design Principle:
# Think Hard Once. Implement Many Times.

from __future__ import annotations

from src.alhf.intent.contracts.intent_capability_mapping import (
    IntentCapabilityMapping,
)


class IntentCapabilityRegistry:
    """
    Registry for intent-capability mappings.
    """

    def __init__(
        self,
    ) -> None:
        self._mappings: dict[
            str,
            IntentCapabilityMapping,
        ] = {}

    def register(
        self,
        mapping: IntentCapabilityMapping,
    ) -> None:
        self._mappings[
            mapping.intent_id
        ] = mapping

    def get(
        self,
        intent_id: str,
    ) -> IntentCapabilityMapping:
        return self._mappings[
            intent_id
        ]

    def exists(
        self,
        intent_id: str,
    ) -> bool:
        return (
            intent_id
            in self._mappings
        )

    def all(
        self,
    ) -> tuple[
        IntentCapabilityMapping,
        ...
    ]:
        return tuple(
            self._mappings.values()
        )
