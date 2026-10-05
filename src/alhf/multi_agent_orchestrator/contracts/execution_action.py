# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines execution actions produced by the
# Execution Governor for the Multi-Agent
# Orchestrator Runtime.
#
# Responsibilities:
# - Represent governance decisions.
# - Provide a standardized runtime action vocabulary.
# - Act as the boundary between governance decisions
#   and runtime execution.
# - Remain stable across V1–V5 evolution.
#
# Must Not:
# - Contain execution logic.
# - Contain governance logic.
# - Contain workflow logic.
# - Contain retry implementation.
# - Contain escalation implementation.
# - Contain termination implementation.
#
# Design Philosophy:
# Design For V5.
# Implement For V1.
#
# V1 Supported Actions:
# - ALLOW
# - BLOCK
# - RETRY
# - ESCALATE
# - TERMINATE
#
# Future Reserved Actions:
# - WAIT_FOR_APPROVAL
# - PAUSE_FOR_INTENT_REVIEW
# - PAUSE_FOR_OUTCOME_REVIEW

from enum import Enum


class ExecutionAction(str, Enum):
    """
    Execution Governor action vocabulary.

    The governor decides.

    Runtime components execute.
    """

    # --------------------------------------------------
    # V1 Actions
    # --------------------------------------------------

    ALLOW = "ALLOW"

    BLOCK = "BLOCK"

    RETRY = "RETRY"

    ESCALATE = "ESCALATE"

    TERMINATE = "TERMINATE"

    # --------------------------------------------------
    # Reserved Future Actions
    # --------------------------------------------------

    WAIT_FOR_APPROVAL = (
        "WAIT_FOR_APPROVAL"
    )

    PAUSE_FOR_INTENT_REVIEW = (
        "PAUSE_FOR_INTENT_REVIEW"
    )

    PAUSE_FOR_OUTCOME_REVIEW = (
        "PAUSE_FOR_OUTCOME_REVIEW"
    )
