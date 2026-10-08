# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Compose capability intelligence components into
# a single capability selection runtime.
#
# Responsibilities:
# - Resolve intent capabilities.
# - Resolve domain capability mappings.
# - Invoke capability selection engine.
# - Return selected capabilities.
#
# Must Not:
# - Perform workflow planning.
# - Execute agents.
# - Perform orchestration.
# - Perform workflow generation.
# - Contain domain business logic.
#
# Architectural Position:
# - Capability intelligence composition layer.
# - Consumed by WorkflowPlanner.
# - Bridges intent/domain knowledge and
#   capability selection.
#
# Future Extensibility:
# - Dynamic domain loading.
# - Capability ranking.
# - Semantic expansion.
# - Outcome optimization.
#
# Design Principle:
# Think Hard Once. Implement Many Times.

from __future__ import annotations

from src.alhf.capability.capability_selection_engine import (
    CapabilitySelectionEngine,
)
from src.alhf.capability.contracts.capability_definition import (
    CapabilityDefinition,
)
from src.alhf.domain.domain_capability_resolver import (
    DomainCapabilityResolver,
)
from src.alhf.intent.intent_capability_resolver import (
    IntentCapabilityResolver,
)


class CapabilityRuntime:
    """
    Entry point for capability intelligence.

    Combines:

    Intent -> Capabilities

    Domain -> Capability Mapping

    Capability Selection Engine

    into a single runtime-facing service.
    """

    def __init__(
        self,
        intent_capability_resolver: (
            IntentCapabilityResolver
        ),
        domain_capability_resolver: (
            DomainCapabilityResolver
        ),
        capability_selection_engine: (
            CapabilitySelectionEngine
        ),
    ) -> None:
        self._intent_capability_resolver = (
            intent_capability_resolver
        )

        self._domain_capability_resolver = (
            domain_capability_resolver
        )

        self._capability_selection_engine = (
            capability_selection_engine
        )

    def select_capabilities(
        self,
        intent_id: str,
        domain_id: str,
    ) -> tuple[
        CapabilityDefinition,
        ...
    ]:
        """
        Select capabilities required for an outcome.

        Flow:

        Intent
        ↓
        Intent Capabilities

        Domain
        ↓
        Domain Mapping

        ↓

        Capability Selection Engine

        ↓

        Selected Capabilities
        """

        intent_capabilities = (
            self._intent_capability_resolver
            .resolve(
                intent_id,
            )
        )

        domain_mapping = (
            self._domain_capability_resolver
            .resolve(
                domain_id,
            )
        )

        domain_capabilities = (
            self._domain_capability_resolver
            .resolve_capabilities(
                domain_id,
            )
        )

        return (
            self._capability_selection_engine
            .select(
                intent_capabilities=(
                    intent_capabilities
                ),
                domain_mapping=(
                    domain_mapping
                ),
                domain_capabilities=(
                    domain_capabilities
                ),
            )
        )
