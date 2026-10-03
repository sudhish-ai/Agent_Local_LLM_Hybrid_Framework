# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for WorkflowExecutionGovernor.
#
# Responsibilities:
# - Verify evaluator coordination.
# - Verify fail-fast behavior.
# - Verify decision propagation.
#
# Must Not:
# - Test evaluator logic.
# - Test workflow execution.
# - Test task execution.

import unittest

from alhf.multi_agent_orchestrator.contracts.execution_action import (
    ExecutionAction,
)
from alhf.multi_agent_orchestrator.contracts.execution_decision import (
    ExecutionDecision,
)
from alhf.multi_agent_orchestrator.execution_governor.workflow_execution_governor import (
    WorkflowExecutionGovernor,
)
from alhf.multi_agent_orchestrator.interfaces.i_execution_evaluator import (
    IExecutionEvaluator,
)


class AllowEvaluator(
    IExecutionEvaluator,
):

    def evaluate(
        self,
        context: object,
    ) -> ExecutionDecision:
        return ExecutionDecision(
            action=ExecutionAction.ALLOW,
        )


class BlockEvaluator(
    IExecutionEvaluator,
):

    def evaluate(
        self,
        context: object,
    ) -> ExecutionDecision:
        return ExecutionDecision(
            action=ExecutionAction.BLOCK,
            reason="blocked",
        )


class RetryEvaluator(
    IExecutionEvaluator,
):

    def evaluate(
        self,
        context: object,
    ) -> ExecutionDecision:
        return ExecutionDecision(
            action=ExecutionAction.RETRY,
            reason="retry required",
        )


class TestWorkflowExecutionGovernor(
    unittest.TestCase
):

    def test_empty_evaluators_returns_allow(
        self,
    ) -> None:
        governor = WorkflowExecutionGovernor(
            evaluators=[],
        )

        decision = governor.pre_task_check(
            object(),
        )

        self.assertEqual(
            decision.action,
            ExecutionAction.ALLOW,
        )

    def test_all_evaluators_allow(
        self,
    ) -> None:
        governor = WorkflowExecutionGovernor(
            evaluators=[
                AllowEvaluator(),
                AllowEvaluator(),
            ],
        )

        decision = governor.pre_task_check(
            object(),
        )

        self.assertEqual(
            decision.action,
            ExecutionAction.ALLOW,
        )

    def test_block_stops_evaluation(
        self,
    ) -> None:
        governor = WorkflowExecutionGovernor(
            evaluators=[
                AllowEvaluator(),
                BlockEvaluator(),
                AllowEvaluator(),
            ],
        )

        decision = governor.pre_task_check(
            object(),
        )

        self.assertEqual(
            decision.action,
            ExecutionAction.BLOCK,
        )

        self.assertEqual(
            decision.reason,
            "blocked",
        )

    def test_retry_decision_propagates(
        self,
    ) -> None:
        governor = WorkflowExecutionGovernor(
            evaluators=[
                RetryEvaluator(),
            ],
        )

        decision = governor.pre_task_check(
            object(),
        )

        self.assertEqual(
            decision.action,
            ExecutionAction.RETRY,
        )

    def test_workflow_check_uses_evaluators(
        self,
    ) -> None:
        governor = WorkflowExecutionGovernor(
            evaluators=[
                BlockEvaluator(),
            ],
        )

        decision = governor.pre_workflow_check(
            object(),
        )

        self.assertEqual(
            decision.action,
            ExecutionAction.BLOCK,
        )

    def test_post_task_check_uses_evaluators(
        self,
    ) -> None:
        governor = WorkflowExecutionGovernor(
            evaluators=[
                RetryEvaluator(),
            ],
        )

        decision = governor.post_task_check(
            object(),
        )

        self.assertEqual(
            decision.action,
            ExecutionAction.RETRY,
        )


if __name__ == "__main__":
    unittest.main()
