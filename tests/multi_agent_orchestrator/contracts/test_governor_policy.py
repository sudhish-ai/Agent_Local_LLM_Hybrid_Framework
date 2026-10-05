# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for GovernorPolicy.

import unittest

from alhf.multi_agent_orchestrator.contracts.governor_policy import (
    GovernorPolicy,
)


class TestGovernorPolicy(unittest.TestCase):

    def test_default_values(self) -> None:
        policy = GovernorPolicy()

        self.assertEqual(
            policy.max_task_retries,
            3,
        )

        self.assertEqual(
            policy.max_workflow_retries,
            1,
        )

        self.assertEqual(
            policy.task_timeout_seconds,
            300,
        )

        self.assertEqual(
            policy.workflow_timeout_seconds,
            3600,
        )

        self.assertTrue(
            policy.escalation_enabled,
        )

    def test_custom_values(self) -> None:
        policy = GovernorPolicy(
            max_task_retries=5,
            max_workflow_retries=2,
            task_timeout_seconds=600,
            workflow_timeout_seconds=7200,
            escalation_enabled=False,
        )

        self.assertEqual(
            policy.max_task_retries,
            5,
        )

        self.assertEqual(
            policy.max_workflow_retries,
            2,
        )

        self.assertEqual(
            policy.task_timeout_seconds,
            600,
        )

        self.assertEqual(
            policy.workflow_timeout_seconds,
            7200,
        )

        self.assertFalse(
            policy.escalation_enabled,
        )


if __name__ == "__main__":
    unittest.main()
