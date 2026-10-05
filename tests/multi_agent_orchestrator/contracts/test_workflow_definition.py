# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Validate WorkflowDefinition contract behavior.
#
# Responsibilities:
# - Validate required fields.
# - Validate default task handling.
# - Validate default constraints handling.
# - Validate default metadata handling.
# - Validate custom task storage.
# - Validate custom constraints storage.
# - Validate custom metadata storage.
#
# Must Not:
# - Test planner logic.
# - Test workflow execution.
# - Test orchestration logic.
# - Test dependency scheduling behavior.

from unittest import TestCase

from alhf.multi_agent_orchestrator.contracts.task_definition import (
    TaskDefinition,
)
from alhf.multi_agent_orchestrator.contracts.workflow_definition import (
    WorkflowDefinition,
)


class TestWorkflowDefinition(TestCase):

    def test_required_fields(self) -> None:
        workflow = WorkflowDefinition(
            workflow_id="wf-001",
            workflow_type="repository_analysis",
        )

        self.assertEqual(
            "wf-001",
            workflow.workflow_id,
        )

        self.assertEqual(
            "repository_analysis",
            workflow.workflow_type,
        )

    def test_default_tasks(self) -> None:
        workflow = WorkflowDefinition(
            workflow_id="wf-001",
            workflow_type="repository_analysis",
        )

        self.assertEqual(
            [],
            workflow.tasks,
        )

    def test_default_constraints(self) -> None:
        workflow = WorkflowDefinition(
            workflow_id="wf-001",
            workflow_type="repository_analysis",
        )

        self.assertEqual(
            {},
            workflow.constraints,
        )

    def test_default_metadata(self) -> None:
        workflow = WorkflowDefinition(
            workflow_id="wf-001",
            workflow_type="repository_analysis",
        )

        self.assertEqual(
            {},
            workflow.metadata,
        )

    def test_custom_tasks(self) -> None:
        task = TaskDefinition(
            task_id="task-001",
            workflow_id="wf-001",
            capability="repository_analyzer",
        )

        workflow = WorkflowDefinition(
            workflow_id="wf-001",
            workflow_type="repository_analysis",
            tasks=[task],
        )

        self.assertEqual(
            [task],
            workflow.tasks,
        )

    def test_custom_constraints(self) -> None:
        constraints = {
            "max_agents": 5,
            "human_approval_required": True,
        }

        workflow = WorkflowDefinition(
            workflow_id="wf-001",
            workflow_type="repository_analysis",
            constraints=constraints,
        )

        self.assertEqual(
            constraints,
            workflow.constraints,
        )

    def test_custom_metadata(self) -> None:
        metadata = {
            "planner_version": "v1",
            "domain": "software_engineering",
        }

        workflow = WorkflowDefinition(
            workflow_id="wf-001",
            workflow_type="repository_analysis",
            metadata=metadata,
        )

        self.assertEqual(
            metadata,
            workflow.metadata,
        )

    def test_task_reference_storage(self) -> None:
        task = TaskDefinition(
            task_id="task-001",
            workflow_id="wf-001",
            capability="repository_analyzer",
        )

        workflow = WorkflowDefinition(
            workflow_id="wf-001",
            workflow_type="repository_analysis",
            tasks=[task],
        )

        self.assertEqual(
            task,
            workflow.tasks[0],
        )
