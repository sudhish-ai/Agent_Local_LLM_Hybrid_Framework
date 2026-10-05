# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Detect planner intent from customer outcomes.
#
# Responsibilities:
# - Analyze outcome requests.
# - Detect planner intent.
# - Produce IntentDefinition.
#
# Must Not:
# - Contain workflow logic.
# - Contain orchestration logic.
# - Contain execution logic.
# - Contain persistence logic.

from alhf.multi_agent_orchestrator.contracts.intent_definition import (
    IntentDefinition,
)
from alhf.multi_agent_orchestrator.contracts.outcome_request import (
    OutcomeRequest,
)


class IntentDetector:
    """
    V1 deterministic intent detector.
    """

    def detect(
        self,
        outcome_request: OutcomeRequest,
    ) -> IntentDefinition:
        goal = outcome_request.goal.lower()

        if "build failure" in goal:
            intent = "build_failure_analysis"
        elif "release notes" in goal:
            intent = "release_note_generation"
        elif "test strategy" in goal:
            intent = "test_strategy_generation"
        else:
            intent = "repository_analysis"

        return IntentDefinition(
            intent=intent,
        )
