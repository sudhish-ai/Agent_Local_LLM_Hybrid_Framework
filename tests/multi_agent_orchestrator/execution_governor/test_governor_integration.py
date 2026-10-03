# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Integration tests for WorkflowExecutionGovernor.
#
# Responsibilities:
# - Validate evaluator chain execution.
# - Validate fail-fast governance.
# - Validate end-to-end decision flow.
#
# Must Not:
# - Test internal evaluator implementation.
# - Test workflow execution.
# - Test task execution.

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
from alhf.multi_agent_orchestrator.contracts.task_context import (
    TaskContext,
)
from alhf.multi_agent_orchestrator.contracts.workflow_context import (
    WorkflowContext,
)
from alhf.multi_agent_orchestrator.enums.workflow_execution_status import (
    WorkflowExecutionStatus,
)
from alhf.multi_agent_orchestrator.execution_governor.retry_evaluator import (
    RetryEvaluator,
)
from alhf.multi_agent_orchestrator.execution_governor.timeout_evaluator import (
    TimeoutEvaluator,
)
from alhf.multi_agent_orchestrator.execution_governor.workflow_execution_governor import (
    WorkflowExecutionGovernor,
)
from alhf.multi_agent_orchestrator.execution_governor.workflow_state_evaluator import (
    WorkflowStateEvaluator,
)


class TestWorkflowExecutionGovernorIntegration(
    unittest.TestCase,
):

    def test_valid_workflow_allows_execution(
        self,
    ) -> None:
        governor = WorkflowExecutionGovernor(
            evaluators=[
                WorkflowStateEvaluator(),
            ],
        )

        context = WorkflowContext(
            workflow_id="wf-1",
            workflow_type="analysis",
            workflow_state=WorkflowExecutionStatus.READY,
        )

        decision = governor.pre_workflow_check(
            context,
        )

        self.assertEqual(
            decision.action,
            ExecutionAction.ALLOW,
        )

    def test_failed_workflow_blocks_execution(
        self,
    ) -> None:
        governor = WorkflowExecutionGovernor(
            evaluators=[
                WorkflowStateEvaluator(),
            ],
        )

        context = WorkflowContext(
            workflow_id="wf-1",
            workflow_type="analysis",
            workflow_state=WorkflowExecutionStatus.FAILED,
        )

        decision = governor.pre_workflow_check(
            context,
        )

        self.assertEqual(
            decision.action,
            ExecutionAction.BLOCK,
        )

    def test_retry_limit_exceeded_escalates(
        self,
    ) -> None:
        policy = GovernorPolicy(
            max_task_retries=3,
            escalation_enabled=True,
        )

        governor = WorkflowExecutionGovernor(
            evaluators=[
                RetryEvaluator(
                    policy,
                ),
            ],
        )

        context = TaskContext(
            task_id="task-1",
            workflow_id="wf-1",
            capability="analysis",
            attempt_number=4,
        )

        decision = governor.pre_task_check(
            context,
        )

        self.assertEqual(
            decision.action,
            ExecutionAction.ESCALATE,
        )
    def test_retry_limit_exceeded_terminates(
        self,
    ) -> None:
        policy = GovernorPolicy(
            max_task_retries=3,
            escalation_enabled=False,
        )

        governor = WorkflowExecutionGovernor(
            evaluators=[
                RetryEvaluator(
                    policy,
                ),
            ],
        )

        context = TaskContext(
            task_id="task-1",
            workflow_id="wf-1",
            capability="analysis",
            attempt_number=4,
        )

        decision = governor.pre_task_check(
            context,
        )

        self.assertEqual(
            decision.action,
            ExecutionAction.TERMINATE,
        )

    def test_timeout_exceeded_escalates(
        self,
    ) -> None:
        policy = GovernorPolicy(
            workflow_timeout_seconds=60,
            escalation_enabled=True,
        )

        governor = WorkflowExecutionGovernor(
            evaluators=[
                TimeoutEvaluator(
                    policy,
                ),
            ],
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

        decision = governor.pre_workflow_check(
            context,
        )

        self.assertEqual(
            decision.action,
            ExecutionAction.ESCALATE,
        )

    def test_fail_fast_returns_first_non_allow(
        self,
    ) -> None:
        policy = GovernorPolicy(
            max_task_retries=3,
            escalation_enabled=True,
        )

        governor = WorkflowExecutionGovernor(
            evaluators=[
                RetryEvaluator(
                    policy,
                ),
            ],
        )

        context = TaskContext(
            task_id="task-1",
            workflow_id="wf-1",
            capability="analysis",
            attempt_number=5,
        )

        decision = governor.pre_task_check(
            context,
        )

        self.assertEqual(
            decision.action,
            ExecutionAction.ESCALATE,
        )


if __name__ == "__main__":
    unittest.main()
