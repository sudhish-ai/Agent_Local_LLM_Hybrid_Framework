# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Bootstrap capability intelligence components
# into a reusable capability intelligence
# context.
#
# Responsibilities:
# - Load capability definitions.
# - Load intent mappings.
# - Load domain mappings.
# - Populate registries.
# - Build CapabilityRuntime.
# - Return CapabilityIntelligenceContext.
#
# Must Not:
# - Execute workflows.
# - Execute agents.
# - Perform orchestration.
# - Contain domain-specific logic.
# - Print runtime information.
#
# Architectural Position:
# - Composition layer bootstrap.
# - Creates capability intelligence graph.
# - Consumed by demos and future runtimes.
#
# Reuse Value:
# - Travel domain.
# - Healthcare domain.
# - Finance domain.
# - Future worker runtime.
#
# Future Extensibility:
# - Dynamic domain loading.
# - Remote metadata sources.
# - Capability intelligence caching.
#
# Design Principle:
# Think Hard Once. Implement Many Times.

from __future__ import annotations

from pathlib import Path

from alhf.capability.capability_registry import (
    CapabilityRegistry,
)
from alhf.capability.capability_runtime import (
    CapabilityRuntime,
)
from alhf.capability.capability_selection_engine import (
    CapabilitySelectionEngine,
)
from alhf.capability.json_capability_definition_loader import (
    JsonCapabilityDefinitionLoader,
)

from alhf.composition.capability_intelligence_context import (
    CapabilityIntelligenceContext,
)

from alhf.domain.domain_capability_registry import (
    DomainCapabilityRegistry,
)
from alhf.domain.domain_capability_resolver import (
    DomainCapabilityResolver,
)
from alhf.domain.json_domain_capability_loader import (
    JsonDomainCapabilityLoader,
)

from alhf.intent.intent_capability_registry import (
    IntentCapabilityRegistry,
)
from alhf.intent.intent_capability_resolver import (
    IntentCapabilityResolver,
)
from alhf.intent.json_intent_capability_loader import (
    JsonIntentCapabilityLoader,
)


class CapabilityIntelligenceBootstrap:
    """
    Creates capability intelligence context.
    """

    def build(
        self,
        capability_definitions_path: Path,
        domain_capabilities_path: Path,
        intent_mappings_path: Path,
    ) -> CapabilityIntelligenceContext:
        capability_registry = (
            CapabilityRegistry()
        )

        intent_registry = (
            IntentCapabilityRegistry()
        )

        domain_registry = (
            DomainCapabilityRegistry()
        )

        capability_result = (
            JsonCapabilityDefinitionLoader()
            .load(
                capability_definitions_path
            )
        )

        for capability in (
            capability_result.loaded_items
        ):
            capability_registry.register(
                capability
            )

        domain_result = (
            JsonDomainCapabilityLoader()
            .load(
                domain_capabilities_path
            )
        )

        for mapping in (
            domain_result.loaded_items
        ):
            domain_registry.register(
                mapping
            )

        intent_result = (
            JsonIntentCapabilityLoader()
            .load(
                intent_mappings_path
            )
        )

        for mapping in (
            intent_result.loaded_items
        ):
            intent_registry.register(
                mapping
            )

        capability_runtime = (
            CapabilityRuntime(
                intent_capability_resolver=(
                    IntentCapabilityResolver(
                        capability_registry=(
                            capability_registry
                        ),
                        intent_capability_registry=(
                            intent_registry
                        ),
                    )
                ),
                domain_capability_resolver=(
                    DomainCapabilityResolver(
                        capability_registry=(
                            capability_registry
                        ),
                        domain_capability_registry=(
                            domain_registry
                        ),
                    )
                ),
                domain_capability_registry=(
                    domain_registry
                ),
                capability_selection_engine=(
                    CapabilitySelectionEngine()
                ),
            )
        )

        return (
            CapabilityIntelligenceContext(
                capability_registry=(
                    capability_registry
                ),
                intent_registry=(
                    intent_registry
                ),
                domain_registry=(
                    domain_registry
                ),
                capability_runtime=(
                    capability_runtime
                ),
                capability_count=(
                    capability_result.loaded_count
                ),
                intent_mapping_count=(
                    intent_result.loaded_count
                ),
                domain_mapping_count=(
                    domain_result.loaded_count
                ),
            )
        )
