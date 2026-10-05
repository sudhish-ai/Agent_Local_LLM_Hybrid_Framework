# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Evaluates workflow execution timeout governance.
#
# Responsibilities:
# - Detect workflow timeout violations.
# - Trigger escalation when timeout limits are exceeded.
# - Allow execution when timeout limits are respected.
#
# Must Not:
# - Execute workflows.
# - Change workflow state.
# - Execute escalation.
# - Execute termination.
#
# Design Philosophy:
# Design For V5.
# Implement For V1.

from datetime import UTC
from datetime import datetime

from alhf.multi_agent_orchestrator.contracts.execution_action import (
    ExecutionAction,
)
from alhf.multi_agent_orchestrator.contracts.execution_decision import (
    ExecutionDecision,
)
from alhf.multi_agent_orchestrator.contracts.governor_policy import (
    GovernorPolicy,
)
from alhf.multi_agent_orchestrator.contracts.workflow_context import (
    WorkflowContext,
)
from alhf.multi_agent_orchestrator.interfaces.i_execution_evaluator import (
    IExecutionEvaluator,
)


class TimeoutEvaluator(
    IExecutionEvaluator,
):
    """
    Evaluates workflow timeout limits.
    """

    def __init__(
        self,
        policy: GovernorPolicy,
    ) -> None:
        self._policy = policy

    def evaluate(
        self,
        context: WorkflowContext,
    ) -> ExecutionDecision:

        if (
            context.execution_start_time_utc
            is None
        ):
            return ExecutionDecision(
                action=ExecutionAction.ALLOW,
                reason=(
                    "workflow has not started"
                ),
            )

        elapsed_seconds = (
            datetime.now(UTC)
            - context.execution_start_time_utc
        ).total_seconds()

        if (
            elapsed_seconds
            <= self._policy.workflow_timeout_seconds
        ):
            return ExecutionDecision(
                action=ExecutionAction.ALLOW,
                reason=(
                    "workflow within timeout limit"
                ),
            )

        if self._policy.escalation_enabled:
            return ExecutionDecision(
                action=ExecutionAction.ESCALATE,
                reason=(
                    "workflow timeout exceeded"
                ),
            )

        return ExecutionDecision(
            action=ExecutionAction.TERMINATE,
            reason=(
                "workflow timeout exceeded"
            ),
        )
