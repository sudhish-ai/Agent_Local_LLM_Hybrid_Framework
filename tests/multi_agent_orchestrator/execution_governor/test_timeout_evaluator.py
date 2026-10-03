# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh

import unittest

from datetime import UTC
from datetime import datetime
from datetime import timedelta

from alhf.multi_agent_orchestrator.contracts.execution_action import (
    ExecutionAction,
)
from alhf.multi_agent_orchestrator.contracts.governor_policy import (
    GovernorPolicy,
)
from alhf.multi_agent_orchestrator.contracts.workflow_context import (
    WorkflowContext,
)
from alhf.multi_agent_orchestrator.enums.workflow_execution_status import (
    WorkflowExecutionStatus,
)
from alhf.multi_agent_orchestrator.execution_governor.timeout_evaluator import (
    TimeoutEvaluator,
)


class TestTimeoutEvaluator(
    unittest.TestCase,
):

    def test_no_start_time_allowed(
        self,
    ) -> None:

        policy = GovernorPolicy()

        evaluator = TimeoutEvaluator(
            policy,
        )

        context = WorkflowContext(
            workflow_id="wf-1",
            workflow_type="analysis",
            workflow_state=WorkflowExecutionStatus.RUNNING,
        )

        decision = evaluator.evaluate(
            context,
        )

        self.assertEqual(
            decision.action,
            ExecutionAction.ALLOW,
        )

    def test_within_timeout_allowed(
        self,
    ) -> None:

        policy = GovernorPolicy(
            workflow_timeout_seconds=3600,
        )

        evaluator = TimeoutEvaluator(
            policy,
        )

        context = WorkflowContext(
            workflow_id="wf-1",
            workflow_type="analysis",
            workflow_state=WorkflowExecutionStatus.RUNNING,
            execution_start_time_utc=(
                datetime.now(UTC)
                - timedelta(minutes=5)
            ),
        )

        decision = evaluator.evaluate(
            context,
        )

        self.assertEqual(
            decision.action,
            ExecutionAction.ALLOW,
        )

    def test_timeout_exceeded_escalates(
        self,
    ) -> None:

        policy = GovernorPolicy(
            workflow_timeout_seconds=60,
            escalation_enabled=True,
        )

        evaluator = TimeoutEvaluator(
            policy,
        )

        context = WorkflowContext(
            workflow_id="wf-1",
            workflow_type="analysis",
            workflow_state=WorkflowExecutionStatus.RUNNING,
            execution_start_time_utc=(
                datetime.now(UTC)
                - timedelta(minutes=5)
            ),
        )

        decision = evaluator.evaluate(
            context,
        )

        self.assertEqual(
            decision.action,
            ExecutionAction.ESCALATE,
        )

    def test_timeout_exceeded_terminates(
        self,
    ) -> None:

        policy = GovernorPolicy(
            workflow_timeout_seconds=60,
            escalation_enabled=False,
        )

        evaluator = TimeoutEvaluator(
            policy,
        )

        context = WorkflowContext(
            workflow_id="wf-1",
            workflow_type="analysis",
            workflow_state=WorkflowExecutionStatus.RUNNING,
            execution_start_time_utc=(
                datetime.now(UTC)
                - timedelta(minutes=5)
            ),
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
