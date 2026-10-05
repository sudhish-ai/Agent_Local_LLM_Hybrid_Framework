# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Reusable base implementation for Outcome Driven Agents.
#
# Responsibilities:
# - Provide standard AgentResponse creation.
# - Provide common metadata generation.
# - Provide common evidence generation.
# - Standardize success handling.
# - Minimize duplicated agent code.
#
# Must Not:
# - Contain workflow orchestration logic.
# - Contain scheduler logic.
# - Contain runtime logic.
# - Contain domain-specific business logic.
#
# Design Philosophy:
# Design For V5.
# Implement For V1.
#
# Notes:
# V1 agents inherit from this base class and
# override minimal domain-specific behavior.
#
# In V5 this becomes the extension point for:
# - Tracing
# - Memory
# - Governance
# - Guardrails
# - Evaluation
# - Cost Controls
# - Observability

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from alhf.multi_agent_orchestrator.contracts.agent_response import (
    AgentResponse,
)
from alhf.multi_agent_orchestrator.contracts.task_context import (
    TaskContext,
)
from alhf.multi_agent_orchestrator.interfaces.i_agent import (
    IAgent,
)


class BaseOutcomeAgent(
    IAgent,
    ABC,
):
    """
    Reusable base implementation for outcome agents.
    """

    @property
    @abstractmethod
    def agent_id(
        self,
    ) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def capability(
        self,
    ) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def success_message(
        self,
    ) -> str:
        raise NotImplementedError

    async def execute(
        self,
        task_context: TaskContext,
    ) -> AgentResponse:
        return AgentResponse(
            status="SUCCESS",
            confidence=1.0,
            result={
                "message": self.success_message,
                "task_id": task_context.task_id,
                "workflow_id": task_context.workflow_id,
                "capability": task_context.capability,
            },
            evidence=[
                {
                    "agent": self.agent_id,
                    "capability": self.capability,
                    "task_id": task_context.task_id,
                }
            ],
            metadata={
                "agent_id": self.agent_id,
                "capability": self.capability,
                "attempt_number": (
                    task_context.attempt_number
                ),
            },
        )
