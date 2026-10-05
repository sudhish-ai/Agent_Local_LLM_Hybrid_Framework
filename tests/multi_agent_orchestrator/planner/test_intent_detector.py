# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Validate IntentDetector behavior.
#
# Responsibilities:
# - Validate repository intent detection.
# - Validate build failure detection.
# - Validate release note detection.
# - Validate test strategy detection.
# - Validate fallback behavior.
#
# Must Not:
# - Test workflow generation.
# - Test orchestration logic.
# - Test execution logic.

from unittest import TestCase

from alhf.multi_agent_orchestrator.contracts.outcome_request import (
    OutcomeRequest,
)
from alhf.multi_agent_orchestrator.planner.intent_detector import (
    IntentDetector,
)


class TestIntentDetector(TestCase):

    def setUp(self) -> None:
        self.detector = IntentDetector()

    def test_build_failure_intent(self) -> None:
        request = OutcomeRequest(
            request_id="req-001",
            goal="Analyze repository build failure",
        )

        result = self.detector.detect(
            request,
        )

        self.assertEqual(
            "build_failure_analysis",
            result.intent,
        )

    def test_release_note_intent(self) -> None:
        request = OutcomeRequest(
            request_id="req-002",
            goal="Generate release notes",
        )

        result = self.detector.detect(
            request,
        )

        self.assertEqual(
            "release_note_generation",
            result.intent,
        )

    def test_test_strategy_intent(self) -> None:
        request = OutcomeRequest(
            request_id="req-003",
            goal="Create test strategy",
        )

        result = self.detector.detect(
            request,
        )

        self.assertEqual(
            "test_strategy_generation",
            result.intent,
        )

    def test_repository_intent_fallback(self) -> None:
        request = OutcomeRequest(
            request_id="req-004",
            goal="Analyze repository",
        )

        result = self.detector.detect(
            request,
        )

        self.assertEqual(
            "repository_analysis",
            result.intent,
        )

    def test_returns_intent_definition(self) -> None:
        request = OutcomeRequest(
            request_id="req-005",
            goal="Analyze repository",
        )

        result = self.detector.detect(
            request,
        )

        self.assertEqual(
            "repository_analysis",
            result.intent,
        )

        self.assertEqual(
            1.0,
            result.confidence,
        )
