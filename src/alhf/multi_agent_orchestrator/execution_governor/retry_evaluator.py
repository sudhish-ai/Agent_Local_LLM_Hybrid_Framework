# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Evaluates retry eligibility for task execution.
#
# Responsibilities:
# - Validate retry attempts.
# - Apply retry governance rules.
# - Trigger escalation when retry limits are exceeded.
#
# Must Not:
# - Execute tasks.
# - Execute retries.
# - Execute escalation.
# - Modify task state.
#
# Design Philosophy:
# Design For V5.
# Implement For V1.
#
# Notes:
# Governance decides.
#
# Runtime executes.
#
# RetryEvaluator ensures execution attempts
# do not exceed configured retry limits.

from alhf.multi_agent_orchestrator.contracts.execution_action import (
    ExecutionAction,
)
from alhf.multi_agent_orchestrator.contracts.execution_decision import (
    ExecutionDecision,
)
from alhf.multi_agent_orchestrator.contracts.governor_policy import (
    GovernorPolicy,
)
from alhf.multi_agent_orchestrator.contracts.task_context import (
    TaskContext,
)
from alhf.multi_agent_orchestrator.interfaces.i_execution_evaluator import (
    IExecutionEvaluator,
)


class RetryEvaluator(
    IExecutionEvaluator,
):
    """
    Evaluates retry eligibility.
    """

    def __init__(
        self,
        policy: GovernorPolicy,
    ) -> None:
        self._policy = policy

    def evaluate(
        self,
        context: TaskContext,
    ) -> ExecutionDecision:
        if (
            context.attempt_number
            <= self._policy.max_task_retries
        ):
            return ExecutionDecision(
                action=ExecutionAction.ALLOW,
                reason="retry threshold not exceeded",
            )

        if self._policy.escalation_enabled:
            return ExecutionDecision(
                action=ExecutionAction.ESCALATE,
                reason="maximum retry threshold exceeded",
            )

        return ExecutionDecision(
            action=ExecutionAction.TERMINATE,
            reason="maximum retry threshold exceeded",
        )
