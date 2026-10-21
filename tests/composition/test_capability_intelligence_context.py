# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for CapabilityIntelligenceContext.
#
# Responsibilities:
# - Validate context creation.
# - Validate dependency preservation.
# - Validate count preservation.
# - Validate immutability.
#
# Must Not:
# - Test capability resolution.
# - Test orchestration.
# - Test execution.
# - Test workflow planning.
#
# Architectural Position:
# - Protects composition layer contracts.
# - Guards capability intelligence transport.
#
# Design Principle:
# Think Hard Once. Implement Many Times.

from dataclasses import FrozenInstanceError

import pytest

from alhf.capability.capability_registry import (
    CapabilityRegistry,
)
from alhf.capability.capability_runtime import (
    CapabilityRuntime,
)
from alhf.capability.capability_selection_engine import (
    CapabilitySelectionEngine,
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
from alhf.intent.intent_capability_registry import (
    IntentCapabilityRegistry,
)
from alhf.intent.intent_capability_resolver import (
    IntentCapabilityResolver,
)


def _build_runtime() -> CapabilityRuntime:
    capability_registry = (
        CapabilityRegistry()
    )

    intent_registry = (
        IntentCapabilityRegistry()
    )

    domain_registry = (
        DomainCapabilityRegistry()
    )

    return CapabilityRuntime(
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


def test_context_preserves_dependencies(
) -> None:
    capability_registry = (
        CapabilityRegistry()
    )

    intent_registry = (
        IntentCapabilityRegistry()
    )

    domain_registry = (
        DomainCapabilityRegistry()
    )

    runtime = (
        _build_runtime()
    )

    context = (
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
                runtime
            ),
            capability_count=6,
            intent_mapping_count=1,
            domain_mapping_count=1,
        )
    )

    assert (
        context.capability_registry
        is capability_registry
    )

    assert (
        context.intent_registry
        is intent_registry
    )

    assert (
        context.domain_registry
        is domain_registry
    )

    assert (
        context.capability_runtime
        is runtime
    )


def test_context_preserves_counts(
) -> None:
    runtime = (
        _build_runtime()
    )

    context = (
        CapabilityIntelligenceContext(
            capability_registry=(
                CapabilityRegistry()
            ),
            intent_registry=(
                IntentCapabilityRegistry()
            ),
            domain_registry=(
                DomainCapabilityRegistry()
            ),
            capability_runtime=(
                runtime
            ),
            capability_count=6,
            intent_mapping_count=2,
            domain_mapping_count=1,
        )
    )

    assert (
        context.capability_count
        == 6
    )

    assert (
        context.intent_mapping_count
        == 2
    )

    assert (
        context.domain_mapping_count
        == 1
    )


def test_context_is_immutable(
) -> None:
    runtime = (
        _build_runtime()
    )

    context = (
        CapabilityIntelligenceContext(
            capability_registry=(
                CapabilityRegistry()
            ),
            intent_registry=(
                IntentCapabilityRegistry()
            ),
            domain_registry=(
                DomainCapabilityRegistry()
            ),
            capability_runtime=(
                runtime
            ),
            capability_count=6,
            intent_mapping_count=2,
            domain_mapping_count=1,
        )
    )

    with pytest.raises(
        FrozenInstanceError
    ):
        context.capability_count = 99
