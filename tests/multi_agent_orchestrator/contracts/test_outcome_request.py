# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Validate OutcomeRequest contract behavior.
#
# Responsibilities:
# - Validate required fields.
# - Validate default values.
# - Validate contract integrity.
#
# Must Not:
# - Test planner logic.
# - Test workflow execution.
# - Test orchestrator behavior.

from unittest import TestCase

from alhf.multi_agent_orchestrator.contracts.outcome_request import (
    OutcomeRequest,
)


class TestOutcomeRequest(TestCase):

    def test_required_fields(self) -> None:
        request = OutcomeRequest(
            request_id="req-001",
            goal="Analyze repository build failure",
        )

        self.assertEqual(
            "req-001",
            request.request_id,
        )

        self.assertEqual(
            "Analyze repository build failure",
            request.goal,
        )

    def test_default_constraints(self) -> None:
        request = OutcomeRequest(
            request_id="req-001",
            goal="Analyze repository",
        )

        self.assertEqual(
            {},
            request.constraints,
        )

    def test_default_preferences(self) -> None:
        request = OutcomeRequest(
            request_id="req-001",
            goal="Analyze repository",
        )

        self.assertEqual(
            {},
            request.preferences,
        )

    def test_default_metadata(self) -> None:
        request = OutcomeRequest(
            request_id="req-001",
            goal="Analyze repository",
        )

        self.assertEqual(
            {},
            request.metadata,
        )

    def test_custom_values(self) -> None:
        request = OutcomeRequest(
            request_id="req-001",
            goal="Analyze repository",
            constraints={
                "time_limit_minutes": 30,
            },
            preferences={
                "depth": "deep",
            },
            metadata={
                "source": "demo",
            },
        )

        self.assertEqual(
            30,
            request.constraints["time_limit_minutes"],
        )

        self.assertEqual(
            "deep",
            request.preferences["depth"],
        )

        self.assertEqual(
            "demo",
            request.metadata["source"],
        )
