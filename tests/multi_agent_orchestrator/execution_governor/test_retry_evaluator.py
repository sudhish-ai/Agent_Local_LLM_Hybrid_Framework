# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for RetryEvaluator.
#
# Responsibilities:
# - Validate retry governance decisions.
# - Validate escalation behavior.
# - Validate termination behavior.
#
# Must Not:
# - Execute retries.
# - Execute escalation.
# - Execute tasks.

import unittest

from alhf.multi_agent_orchestrator.contracts.execution_action import (
    ExecutionAction,
)
from alhf.multi_agent_orchestrator.contracts.governor_policy import (
    GovernorPolicy,
)
from alhf.multi_agent_orchestrator.contracts.task_context import (
    TaskContext,
)
from alhf.multi_agent_orchestrator.execution_governor.retry_evaluator import (
    RetryEvaluator,
)


class TestRetryEvaluator(
    unittest.TestCase,
):

    def test_attempt_below_limit_allowed(
        self,
    ) -> None:
        policy = GovernorPolicy(
            max_task_retries=3,
        )

        evaluator = RetryEvaluator(
            policy,
        )

        context = TaskContext(
            task_id="task-1",
            workflow_id="wf-1",
            capability="analysis",
            attempt_number=1,
        )

        decision = evaluator.evaluate(
            context,
        )

        self.assertEqual(
            decision.action,
            ExecutionAction.ALLOW,
        )

    def test_attempt_equal_limit_allowed(
        self,
    ) -> None:
        policy = GovernorPolicy(
            max_task_retries=3,
        )

        evaluator = RetryEvaluator(
            policy,
        )

        context = TaskContext(
            task_id="task-1",
            workflow_id="wf-1",
            capability="analysis",
            attempt_number=3,
        )

        decision = evaluator.evaluate(
            context,
        )

        self.assertEqual(
            decision.action,
            ExecutionAction.ALLOW,
        )
    def test_attempt_above_limit_escalates(
        self,
    ) -> None:
        policy = GovernorPolicy(
            max_task_retries=3,
            escalation_enabled=True,
        )

        evaluator = RetryEvaluator(
            policy,
        )

        context = TaskContext(
            task_id="task-1",
            workflow_id="wf-1",
            capability="analysis",
            attempt_number=4,
        )

        decision = evaluator.evaluate(
            context,
        )

        self.assertEqual(
            decision.action,
            ExecutionAction.ESCALATE,
        )

    def test_attempt_above_limit_terminates(
        self,
    ) -> None:
        policy = GovernorPolicy(
            max_task_retries=3,
            escalation_enabled=False,
        )

        evaluator = RetryEvaluator(
            policy,
        )

        context = TaskContext(
            task_id="task-1",
            workflow_id="wf-1",
            capability="analysis",
            attempt_number=4,
        )

        decision = evaluator.evaluate(
            context,
        )

        self.assertEqual(
            decision.action,
            ExecutionAction.TERMINATE,
        )


if __name__ == "__main__":
    unittest.main()
