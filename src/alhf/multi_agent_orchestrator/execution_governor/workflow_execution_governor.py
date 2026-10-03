# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Coordinates execution governance evaluation for
# the Multi-Agent Orchestrator Runtime.
#
# Responsibilities:
# - Execute governance evaluators.
# - Apply fail-fast evaluation.
# - Return the first non-ALLOW decision.
# - Return ALLOW when all evaluators approve.
#
# Must Not:
# - Implement retry logic.
# - Implement timeout logic.
# - Implement workflow-state logic.
# - Implement policy logic.
# - Execute workflows.
# - Execute tasks.
#
# Design Philosophy:
# Design For V5.
# Implement For V1.
#
# Notes:
# Governance Logic
#      ↓
# Evaluators
#
# Coordination Logic
#      ↓
# WorkflowExecutionGovernor

from collections.abc import Sequence

from alhf.multi_agent_orchestrator.contracts.execution_action import (
    ExecutionAction,
)
from alhf.multi_agent_orchestrator.contracts.execution_decision import (
    ExecutionDecision,
)
from alhf.multi_agent_orchestrator.interfaces.i_execution_evaluator import (
    IExecutionEvaluator,
)
from alhf.multi_agent_orchestrator.interfaces.i_execution_governor import (
    IExecutionGovernor,
)


class WorkflowExecutionGovernor(
    IExecutionGovernor,
):
    """
    Coordinates execution governance evaluation.
    """

    def __init__(
        self,
        evaluators: Sequence[
            IExecutionEvaluator
        ],
    ) -> None:
        self._evaluators = tuple(
            evaluators
        )

    def pre_workflow_check(
        self,
        workflow_context,
    ) -> ExecutionDecision:
        return self._evaluate(
            workflow_context,
        )

    def pre_task_check(
        self,
        task_context,
    ) -> ExecutionDecision:
        return self._evaluate(
            task_context,
        )

    def post_task_check(
        self,
        task_context,
    ) -> ExecutionDecision:
        return self._evaluate(
            task_context,
        )

    def _evaluate(
        self,
        context: object,
    ) -> ExecutionDecision:
        """
        Execute evaluators using fail-fast
        governance evaluation.

        First non-ALLOW decision wins.
        """

        for evaluator in self._evaluators:
            decision = evaluator.evaluate(
                context,
            )

            if (
                decision.action
                != ExecutionAction.ALLOW
            ):
                return decision

        return ExecutionDecision(
            action=ExecutionAction.ALLOW,
            reason="all evaluators passed",
        )
