# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Detect domain from planner intent.
#
# Responsibilities:
# - Analyze detected intent.
# - Determine planner domain.
# - Provide domain classification.
#
# Must Not:
# - Contain workflow logic.
# - Contain orchestration logic.
# - Contain execution logic.
# - Contain persistence logic.

from alhf.multi_agent_orchestrator.contracts.intent_definition import (
    IntentDefinition,
)


class DomainDetector:
    """
    V1 deterministic domain detector.
    """

    def detect(
        self,
        intent_definition: IntentDefinition,
    ) -> str:
        return "software_engineering"
