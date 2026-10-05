# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Validate IntentDefinition contract behavior.
#
# Responsibilities:
# - Validate required fields.
# - Validate default confidence handling.
# - Validate custom confidence handling.
# - Validate default metadata handling.
# - Validate custom metadata handling.
#
# Must Not:
# - Test intent detection logic.
# - Test planner logic.
# - Test workflow generation.
# - Test orchestration behavior.

from unittest import TestCase

from alhf.multi_agent_orchestrator.contracts.intent_definition import (
    IntentDefinition,
)


class TestIntentDefinition(TestCase):

    def test_required_fields(self) -> None:
        intent = IntentDefinition(
            intent="repository_analysis",
        )

        self.assertEqual(
            "repository_analysis",
            intent.intent,
        )

    def test_default_confidence(self) -> None:
        intent = IntentDefinition(
            intent="repository_analysis",
        )

        self.assertEqual(
            1.0,
            intent.confidence,
        )

    def test_custom_confidence(self) -> None:
        intent = IntentDefinition(
            intent="repository_analysis",
            confidence=0.85,
        )

        self.assertEqual(
            0.85,
            intent.confidence,
        )

    def test_default_metadata(self) -> None:
        intent = IntentDefinition(
            intent="repository_analysis",
        )

        self.assertEqual(
            {},
            intent.metadata,
        )

    def test_custom_metadata(self) -> None:
        metadata = {
            "source": "keyword_match",
            "version": "v1",
        }

        intent = IntentDefinition(
            intent="repository_analysis",
            metadata=metadata,
        )

        self.assertEqual(
            metadata,
            intent.metadata,
        )
