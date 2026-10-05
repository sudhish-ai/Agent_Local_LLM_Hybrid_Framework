# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for ExecutionDecision.

import unittest

from alhf.multi_agent_orchestrator.contracts.execution_action import (
    ExecutionAction,
)
from alhf.multi_agent_orchestrator.contracts.execution_decision import (
    ExecutionDecision,
)


class TestExecutionDecision(unittest.TestCase):

    def test_create_allow_decision(self) -> None:
        decision = ExecutionDecision(
            action=ExecutionAction.ALLOW,
        )

        self.assertEqual(
            decision.action,
            ExecutionAction.ALLOW,
        )

        self.assertIsNone(
            decision.reason,
        )

        self.assertIsNone(
            decision.metadata,
        )

    def test_create_block_decision(self) -> None:
        decision = ExecutionDecision(
            action=ExecutionAction.BLOCK,
            reason="workflow disabled",
        )

        self.assertEqual(
            decision.action,
            ExecutionAction.BLOCK,
        )

        self.assertEqual(
            decision.reason,
            "workflow disabled",
        )

        self.assertIsNone(
            decision.metadata,
        )

