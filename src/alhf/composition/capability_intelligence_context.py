# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides a reusable capability intelligence
# context containing all assembled capability
# intelligence components required by runtime
# consumers.
#
# Responsibilities:
# - Hold capability registry.
# - Hold intent registry.
# - Hold domain registry.
# - Hold capability runtime.
# - Expose capability intelligence metadata.
#
# Must Not:
# - Load files.
# - Register entities.
# - Execute workflows.
# - Execute agents.
# - Perform orchestration.
# - Contain domain-specific logic.
#
# Architectural Position:
# - Composition layer context object.
# - Produced by composition builders.
# - Consumed by demos, planners and
#   future runtime components.
#
# Reuse Value:
# - Travel domain.
# - Healthcare domain.
# - Finance domain.
# - Insurance domain.
# - Future worker runtime.
#
# Future Extensibility:
# - Capability metrics.
# - Capability statistics.
# - Dynamic domain loading.
# - Runtime diagnostics.
#
# Design Principle:
# Think Hard Once. Implement Many Times.

from __future__ import annotations

from dataclasses import dataclass

from alhf.capability.capability_registry import (
    CapabilityRegistry,
)
from alhf.capability.capability_runtime import (
    CapabilityRuntime,
)
from alhf.domain.domain_capability_registry import (
    DomainCapabilityRegistry,
)
from alhf.intent.intent_capability_registry import (
    IntentCapabilityRegistry,
)


@dataclass(frozen=True)
class CapabilityIntelligenceContext:
    """
    Immutable capability intelligence context.

    Encapsulates all capability intelligence
    infrastructure required by runtime
    consumers.
    """

    capability_registry: (
        CapabilityRegistry
    )

    intent_registry: (
        IntentCapabilityRegistry
    )

    domain_registry: (
        DomainCapabilityRegistry
    )

    capability_runtime: (
        CapabilityRuntime
    )

    capability_count: int

    intent_mapping_count: int

    domain_mapping_count: int
