# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Validates workflow execution state before
# workflow execution proceeds.
#
# Responsibilities:
# - Ensure workflow is executable.
# - Block invalid workflow states.
# - Return governance decisions.
#
# Must Not:
# - Execute workflows.
# - Change workflow state.
# - Manage retries.
# - Manage timeouts.
#
# Design Philosophy:
# Design For V5.
# Implement For V1.

from alhf.multi_agent_orchestrator.contracts.execution_action import (
    ExecutionAction,
)
from alhf.multi_agent_orchestrator.contracts.execution_decision import (
    ExecutionDecision,
)
from alhf.multi_agent_orchestrator.enums.workflow_execution_status import (
    WorkflowExecutionStatus,
)
from alhf.multi_agent_orchestrator.interfaces.i_execution_evaluator import (
    IExecutionEvaluator,
)


class WorkflowStateEvaluator(
    IExecutionEvaluator,
):
    """
    Validates workflow execution state.
    """

    ALLOWED_STATES = {
        WorkflowExecutionStatus.READY,
        WorkflowExecutionStatus.RUNNING,
    }

    def evaluate(
        self,
        context: object,
    ) -> ExecutionDecision:
        workflow_state = getattr(
            context,
            "workflow_state",
            None,
        )

        if workflow_state in self.ALLOWED_STATES:
            return ExecutionDecision(
                action=ExecutionAction.ALLOW,
                reason=(
                    "workflow state allows execution"
                ),
            )

        return ExecutionDecision(
            action=ExecutionAction.BLOCK,
            reason=(
                f"workflow state "
                f"'{workflow_state}' "
                f"does not allow execution"
            ),
        )
