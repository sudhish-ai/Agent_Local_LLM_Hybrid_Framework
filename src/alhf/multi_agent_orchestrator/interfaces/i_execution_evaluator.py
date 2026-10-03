# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the execution evaluator contract for the
# Multi-Agent Orchestrator Runtime.
#
# Responsibilities:
# - Evaluate execution state.
# - Produce governance decisions.
# - Encapsulate a single governance concern.
# - Support pluggable governance extensions.
#
# Must Not:
# - Execute workflows.
# - Execute tasks.
# - Persist state.
# - Coordinate execution.
# - Apply runtime actions directly.
#
# Design Philosophy:
# Design For V5.
# Implement For V1.
#
# Notes:
# Each evaluator should own a single governance
# concern.
#
# Examples:
# - RetryEvaluator
# - TimeoutEvaluator
# - WorkflowStateEvaluator
# - PolicyEvaluator (V2)
# - ResourceEvaluator (V3)
# - IntentEvaluator (V4)
# - OutcomeEvaluator (V5)

from abc import ABC
from abc import abstractmethod

from alhf.multi_agent_orchestrator.contracts.execution_decision import (
    ExecutionDecision,
)


class IExecutionEvaluator(ABC):
    """
    Execution governance extension point.

    Implementations evaluate execution state
    and return an ExecutionDecision.
    """

    @abstractmethod
    def evaluate(
        self,
        context: object,
    ) -> ExecutionDecision:
        """
        Evaluate execution state and return
        a governance decision.
        """
        raise NotImplementedError
