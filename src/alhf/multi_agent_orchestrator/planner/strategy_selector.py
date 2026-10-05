# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Select planning strategy from detected intent
# and domain knowledge.
#
# Responsibilities:
# - Analyze detected intent.
# - Consult domain knowledge.
# - Select planning strategy.
# - Produce StrategyDefinition.
#
# Must Not:
# - Contain workflow generation logic.
# - Contain execution logic.
# - Contain persistence logic.
# - Contain orchestration logic.

from alhf.multi_agent_orchestrator.contracts.intent_definition import (
    IntentDefinition,
)
from alhf.multi_agent_orchestrator.contracts.strategy_definition import (
    StrategyDefinition,
)
from alhf.multi_agent_orchestrator.planner.domain_packs.domain_pack_registry import (
    DomainPackRegistry,
)


class StrategySelector:
    """
    V1 deterministic strategy selector.
    """

    def __init__(
        self,
        registry: DomainPackRegistry,
    ) -> None:
        self._registry = registry

    def select(
        self,
        intent_definition: IntentDefinition,
        domain: str,
    ) -> StrategyDefinition:
        domain_pack = self._registry.get_domain_pack(
            domain,
        )

        if domain_pack is None:
            raise ValueError(
                f"Unsupported domain: {domain}"
            )

        strategy = domain_pack.workflow_templates.get(
            intent_definition.intent,
            "repository_inspection",
        )

        return StrategyDefinition(
            strategy=strategy,
        )
