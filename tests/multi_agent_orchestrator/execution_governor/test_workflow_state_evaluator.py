# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh

import unittest

from alhf.multi_agent_orchestrator.contracts.execution_action import (
    ExecutionAction,
)
from alhf.multi_agent_orchestrator.contracts.workflow_context import (
    WorkflowContext,
)
from alhf.multi_agent_orchestrator.enums.workflow_execution_status import (
    WorkflowExecutionStatus,
)
from alhf.multi_agent_orchestrator.execution_governor.workflow_state_evaluator import (
    WorkflowStateEvaluator,
)


class TestWorkflowStateEvaluator(
    unittest.TestCase,
):

    def setUp(
        self,
    ) -> None:
        self.evaluator = (
            WorkflowStateEvaluator()
        )

    def test_ready_workflow_allowed(
        self,
    ) -> None:
        context = WorkflowContext(
            workflow_id="wf-1",
            workflow_type="analysis",
            workflow_state=WorkflowExecutionStatus.READY,
        )

        decision = self.evaluator.evaluate(
            context
        )

        self.assertEqual(
            decision.action,
            ExecutionAction.ALLOW,
        )

    def test_running_workflow_allowed(
        self,
    ) -> None:
        context = WorkflowContext(
            workflow_id="wf-1",
            workflow_type="analysis",
            workflow_state=WorkflowExecutionStatus.RUNNING,
        )

        decision = self.evaluator.evaluate(
            context
        )

        self.assertEqual(
            decision.action,
            ExecutionAction.ALLOW,
        )

    def test_completed_workflow_blocked(
        self,
    ) -> None:
        context = WorkflowContext(
            workflow_id="wf-1",
            workflow_type="analysis",
            workflow_state=WorkflowExecutionStatus.COMPLETED,
        )

        decision = self.evaluator.evaluate(
            context
        )

        self.assertEqual(
            decision.action,
            ExecutionAction.BLOCK,
        )

    def test_failed_workflow_blocked(
        self,
    ) -> None:
        context = WorkflowContext(
            workflow_id="wf-1",
            workflow_type="analysis",
            workflow_state=WorkflowExecutionStatus.FAILED,
        )

        decision = self.evaluator.evaluate(
            context
        )

        self.assertEqual(
            decision.action,
            ExecutionAction.BLOCK,
        )

    def test_cancelled_workflow_blocked(
        self,
    ) -> None:
        context = WorkflowContext(
            workflow_id="wf-1",
            workflow_type="analysis",
            workflow_state=WorkflowExecutionStatus.CANCELLED,
        )

        decision = self.evaluator.evaluate(
            context
        )

        self.assertEqual(
            decision.action,
            ExecutionAction.BLOCK,
        )

    def test_missing_workflow_state_blocked(
        self,
    ) -> None:
        context = object()

        decision = self.evaluator.evaluate(
            context
        )

        self.assertEqual(
            decision.action,
            ExecutionAction.BLOCK,
        )


if __name__ == "__main__":
    unittest.main()
