# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Validate PlanningResult contract behavior.
#
# Responsibilities:
# - Validate required fields.
# - Validate confidence handling.
# - Validate assumptions handling.
# - Validate workflow definition storage.
#
# Must Not:
# - Test planner logic.
# - Test workflow execution.
# - Test orchestration logic.

from unittest import TestCase

from alhf.multi_agent_orchestrator.contracts.planning_result import (
    PlanningResult,
)
from alhf.multi_agent_orchestrator.contracts.workflow_definition import (
    WorkflowDefinition,
)


class TestPlanningResult(TestCase):

    def _create_workflow(self) -> WorkflowDefinition:
        return WorkflowDefinition(
            workflow_id="wf-001",
            workflow_type="repository_analysis",
        )

    def test_required_fields(self) -> None:
        workflow = self._create_workflow()

        result = PlanningResult(
            intent="repository_analysis",
            domain="software_engineering",
            strategy="root_cause_analysis",
            workflow_definition=workflow,
        )

        self.assertEqual(
            "repository_analysis",
            result.intent,
        )

        self.assertEqual(
            "software_engineering",
            result.domain,
        )

        self.assertEqual(
            "root_cause_analysis",
            result.strategy,
        )

    def test_default_confidence(self) -> None:
        workflow = self._create_workflow()

        result = PlanningResult(
            intent="repository_analysis",
            domain="software_engineering",
            strategy="root_cause_analysis",
            workflow_definition=workflow,
        )

        self.assertEqual(
            1.0,
            result.confidence,
        )

    def test_custom_confidence(self) -> None:
        workflow = self._create_workflow()

        result = PlanningResult(
            intent="repository_analysis",
            domain="software_engineering",
            strategy="root_cause_analysis",
            workflow_definition=workflow,
            confidence=0.85,
        )

        self.assertEqual(
            0.85,
            result.confidence,
        )

    def test_default_assumptions(self) -> None:
        workflow = self._create_workflow()

        result = PlanningResult(
            intent="repository_analysis",
            domain="software_engineering",
            strategy="root_cause_analysis",
            workflow_definition=workflow,
        )

        self.assertEqual(
            [],
            result.assumptions,
        )

    def test_custom_assumptions(self) -> None:
        workflow = self._create_workflow()

        assumptions = [
            "Repository access available",
            "Build logs available",
        ]

        result = PlanningResult(
            intent="repository_analysis",
            domain="software_engineering",
            strategy="root_cause_analysis",
            workflow_definition=workflow,
            assumptions=assumptions,
        )

        self.assertEqual(
            assumptions,
            result.assumptions,
        )

    def test_workflow_definition_reference(self) -> None:
        workflow = self._create_workflow()

        result = PlanningResult(
            intent="repository_analysis",
            domain="software_engineering",
            strategy="root_cause_analysis",
            workflow_definition=workflow,
        )

        self.assertEqual(
            workflow,
            result.workflow_definition,
        )
