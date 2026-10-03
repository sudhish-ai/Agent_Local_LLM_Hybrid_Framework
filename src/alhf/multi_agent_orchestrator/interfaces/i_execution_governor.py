# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the execution governance contract for the
# Multi-Agent Orchestrator Runtime.
#
# Responsibilities:
# - Validate workflow execution.
# - Validate task execution.
# - Evaluate post-execution state.
# - Produce execution decisions.
# - Act as the governance boundary for runtime execution.
#
# Must Not:
# - Execute workflows.
# - Execute tasks.
# - Apply retry logic directly.
# - Apply escalation logic directly.
# - Apply termination logic directly.
#
# Design Philosophy:
# Design For V5.
# Implement For V1.
#
# Notes:
# Governor decides.
#
# Runtime components execute decisions.
#
# Future governance capabilities must be implemented
# through evaluation logic rather than interface changes.

from abc import ABC
from abc import abstractmethod

from alhf.multi_agent_orchestrator.contracts.execution_decision import (
    ExecutionDecision,
)
from alhf.multi_agent_orchestrator.contracts.task_context import (
    TaskContext,
)
from alhf.multi_agent_orchestrator.contracts.workflow_context import (
    WorkflowContext,
)


class IExecutionGovernor(ABC):
    """
    Runtime governance contract.

    Implementations decide whether execution
    should proceed, pause, retry, escalate,
    or terminate.
    """

    @abstractmethod
    def pre_workflow_check(
        self,
        workflow_context: WorkflowContext,
    ) -> ExecutionDecision:
        """
        Evaluate workflow before execution starts.
        """
        raise NotImplementedError

    @abstractmethod
    def pre_task_check(
        self,
        task_context: TaskContext,
    ) -> ExecutionDecision:
        """
        Evaluate task before execution starts.
        """
        raise NotImplementedError

    @abstractmethod
    def post_task_check(
        self,
        task_context: TaskContext,
    ) -> ExecutionDecision:
        """
        Evaluate task after execution finishes.
        """
        raise NotImplementedError
