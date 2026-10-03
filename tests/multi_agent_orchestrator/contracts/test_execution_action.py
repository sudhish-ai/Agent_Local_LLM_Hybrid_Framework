# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for ExecutionAction.
#
# Responsibilities:
# - Validate enum values.
# - Validate future reserved actions.
# - Protect contract stability.
#
# Must Not:
# - Contain business logic.
# - Contain runtime logic.
# - Contain governance logic.

import unittest

from alhf.multi_agent_orchestrator.contracts.execution_action import (
    ExecutionAction,
)


class TestExecutionAction(unittest.TestCase):
    """
    Unit tests for ExecutionAction.
    """

    def test_allow_value(self) -> None:
        self.assertEqual(
            ExecutionAction.ALLOW.value,
            "ALLOW",
        )

    def test_block_value(self) -> None:
        self.assertEqual(
            ExecutionAction.BLOCK.value,
            "BLOCK",
        )

    def test_retry_value(self) -> None:
        self.assertEqual(
            ExecutionAction.RETRY.value,
            "RETRY",
        )

    def test_escalate_value(self) -> None:
        self.assertEqual(
            ExecutionAction.ESCALATE.value,
            "ESCALATE",
        )

    def test_terminate_value(self) -> None:
        self.assertEqual(
            ExecutionAction.TERMINATE.value,
            "TERMINATE",
        )

    def test_wait_for_approval_value(self) -> None:
        self.assertEqual(
            ExecutionAction.WAIT_FOR_APPROVAL.value,
            "WAIT_FOR_APPROVAL",
        )

    def test_pause_for_intent_review_value(
        self,
    ) -> None:
        self.assertEqual(
            ExecutionAction.PAUSE_FOR_INTENT_REVIEW.value,
            "PAUSE_FOR_INTENT_REVIEW",
        )

    def test_pause_for_outcome_review_value(
        self,
    ) -> None:
        self.assertEqual(
            ExecutionAction.PAUSE_FOR_OUTCOME_REVIEW.value,
            "PAUSE_FOR_OUTCOME_REVIEW",
        )


if __name__ == "__main__":
    unittest.main()
