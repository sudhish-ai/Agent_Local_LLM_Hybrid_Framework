# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines configuration for the Execution Governor.
#
# Responsibilities:
# - Define retry limits.
# - Define timeout limits.
# - Define escalation behavior.
# - Centralize governor configuration.
#
# Must Not:
# - Contain execution logic.
# - Contain workflow logic.
# - Contain policy evaluation logic.
# - Contain runtime behavior.
#
# Design Philosophy:
# Design For V5.
# Implement For V1.
#
# Notes:
# V1 contains only real, implemented settings.
#
# Future governance capabilities should be
# added through new evaluators and governance
# layers rather than speculative configuration
# flags.

from dataclasses import dataclass


@dataclass(frozen=True)
class GovernorPolicy:
    """
    Configuration contract for
    WorkflowExecutionGovernor.
    """

    max_task_retries: int = 3

    max_workflow_retries: int = 1

    task_timeout_seconds: int = 300

    workflow_timeout_seconds: int = 3600

    escalation_enabled: bool = True
