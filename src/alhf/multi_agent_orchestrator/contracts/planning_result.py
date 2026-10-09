# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the planning result contract produced by
# the Workflow Planner and future Outcome Optimization Engine.
#
# Responsibilities:
# - Capture detected intent.
# - Capture detected domain.
# - Capture selected strategy.
# - Capture selected capabilities.
# - Capture planning confidence.
# - Capture planning assumptions.
# - Carry generated workflow definition.
#
# Must Not:
# - Contain execution logic.
# - Contain scheduling logic.
# - Contain dependency resolution logic.
# - Contain workflow execution state.
# - Contain planner intelligence.

from dataclasses import dataclass
from dataclasses import field

from alhf.multi_agent_orchestrator.contracts.workflow_definition import (
    WorkflowDefinition,
)


@dataclass(slots=True)
class PlanningResult:
    """
    Planning result produced by the Workflow Planner.

    Why:
        Planning should preserve reasoning artifacts,
        not only the generated workflow.

    V1:
        Supports template-driven planning.

    V2:
        Preserves selected capabilities alongside
        workflow generation.

    V5:
        Supports Outcome Optimization Engine,
        Pattern Intelligence,
        Domain Intelligence,
        Strategy Formation,
        Capability Planning,
        and Planning Confidence.
    """

    intent: str

    domain: str

    strategy: str

    workflow_definition: WorkflowDefinition

    selected_capabilities: tuple[
        str,
        ...
    ] = field(
        default_factory=tuple,
    )

    confidence: float = 1.0

    assumptions: list[str] = field(
        default_factory=list,
    )
