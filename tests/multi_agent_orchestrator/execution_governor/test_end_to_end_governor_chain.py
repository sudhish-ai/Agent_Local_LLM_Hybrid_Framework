# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# End-to-end tests for the complete governor chain.
#
# Responsibilities:
# - Validate evaluator ordering.
# - Validate fail-fast execution.
# - Validate final governance decisions.
# - Validate governor pipeline behavior.
#
# Must Not:
# - Mock governor behavior.
# - Test evaluator internals.
# - Test workflow execution.

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


class TestEndToEndGovernorChain(
    unittest.TestCase,
):

    def test_workflow_state_allows_ready_workflow(
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

    def test_workflow_state_blocks_failed_workflow(
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

    def test_retry_evaluator_allows_first_attempt(
        self,
    ) -> None:
        policy = GovernorPolicy(
            max_task_retries=3,
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
            attempt_number=1,
        )

        decision = governor.pre_task_check(
            context,
        )

        self.assertEqual(
            decision.action,
            ExecutionAction.ALLOW,
        )
    def test_retry_evaluator_escalates_after_limit(
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

    def test_timeout_evaluator_escalates(
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

    def test_fail_fast_blocks_before_other_checks(
        self,
    ) -> None:
        policy = GovernorPolicy(
            workflow_timeout_seconds=3600,
            escalation_enabled=True,
        )

        governor = WorkflowExecutionGovernor(
            evaluators=[
                WorkflowStateEvaluator(),
                TimeoutEvaluator(
                    policy,
                ),
            ],
        )

        context = WorkflowContext(
            workflow_id="wf-1",
            workflow_type="analysis",
            workflow_state=WorkflowExecutionStatus.FAILED,
            execution_start_time_utc=(
                datetime.now(UTC)
                - timedelta(hours=10)
            ),
        )

        decision = governor.pre_workflow_check(
            context,
        )

        self.assertEqual(
            decision.action,
            ExecutionAction.BLOCK,
        )


if __name__ == "__main__":
    unittest.main()
