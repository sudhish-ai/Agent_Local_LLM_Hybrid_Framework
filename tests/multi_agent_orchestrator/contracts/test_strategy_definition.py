# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Validate StrategyDefinition contract behavior.
#
# Responsibilities:
# - Validate required fields.
# - Validate default confidence handling.
# - Validate custom confidence handling.
# - Validate default metadata handling.
# - Validate custom metadata handling.
#
# Must Not:
# - Test strategy selection logic.
# - Test planner logic.
# - Test workflow generation.
# - Test orchestration behavior.

from unittest import TestCase

from alhf.multi_agent_orchestrator.contracts.strategy_definition import (
    StrategyDefinition,
)


class TestStrategyDefinition(TestCase):

    def test_required_fields(self) -> None:
        strategy = StrategyDefinition(
            strategy="root_cause_analysis",
        )

        self.assertEqual(
            "root_cause_analysis",
            strategy.strategy,
        )

    def test_default_confidence(self) -> None:
        strategy = StrategyDefinition(
            strategy="root_cause_analysis",
        )

        self.assertEqual(
            1.0,
            strategy.confidence,
        )

    def test_custom_confidence(self) -> None:
        strategy = StrategyDefinition(
            strategy="root_cause_analysis",
            confidence=0.85,
        )

        self.assertEqual(
            0.85,
            strategy.confidence,
        )

    def test_default_metadata(self) -> None:
        strategy = StrategyDefinition(
            strategy="root_cause_analysis",
        )

        self.assertEqual(
            {},
            strategy.metadata,
        )

    def test_custom_metadata(self) -> None:
        metadata = {
            "source": "repository_domain_pack",
            "version": "v1",
        }

        strategy = StrategyDefinition(
            strategy="root_cause_analysis",
            metadata=metadata,
        )

        self.assertEqual(
            metadata,
            strategy.metadata,
        )
