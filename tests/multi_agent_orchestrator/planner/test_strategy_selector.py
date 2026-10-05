# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Validate StrategySelector behavior.
#
# Responsibilities:
# - Validate strategy selection.
# - Validate repository analysis strategy.
# - Validate build failure strategy.
# - Validate release note strategy.
# - Validate test strategy generation strategy.
#
# Must Not:
# - Test workflow generation.
# - Test orchestration behavior.
# - Test execution behavior.

from unittest import TestCase

from alhf.multi_agent_orchestrator.contracts.intent_definition import (
    IntentDefinition,
)
from alhf.multi_agent_orchestrator.planner.domain_packs.domain_pack_registry import (
    DomainPackRegistry,
)
from alhf.multi_agent_orchestrator.planner.strategy_selector import (
    StrategySelector,
)


class TestStrategySelector(TestCase):

    def setUp(
        self,
    ) -> None:
        self.registry = DomainPackRegistry()
        self.selector = StrategySelector(
            self.registry,
        )

    def test_repository_analysis_strategy(
        self,
    ) -> None:
        intent = IntentDefinition(
            intent="repository_analysis",
        )

        strategy = self.selector.select(
            intent,
            "software_engineering",
        )

        self.assertEqual(
            "root_cause_analysis",
            strategy.strategy,
        )

    def test_build_failure_strategy(
        self,
    ) -> None:
        intent = IntentDefinition(
            intent="build_failure_analysis",
        )

        strategy = self.selector.select(
            intent,
            "software_engineering",
        )

        self.assertEqual(
            "root_cause_analysis",
            strategy.strategy,
        )

    def test_release_note_strategy(
        self,
    ) -> None:
        intent = IntentDefinition(
            intent="release_note_generation",
        )

        strategy = self.selector.select(
            intent,
            "software_engineering",
        )

        self.assertEqual(
            "release_note_generation",
            strategy.strategy,
        )

    def test_test_strategy_generation_strategy(
        self,
    ) -> None:
        intent = IntentDefinition(
            intent="test_strategy_generation",
        )

        strategy = self.selector.select(
            intent,
            "software_engineering",
        )

        self.assertEqual(
            "risk_based_test_strategy",
            strategy.strategy,
        )

    def test_returns_strategy_definition(
        self,
    ) -> None:
        intent = IntentDefinition(
            intent="repository_analysis",
        )

        strategy = self.selector.select(
            intent,
            "software_engineering",
        )

        self.assertEqual(
            1.0,
            strategy.confidence,
        )
