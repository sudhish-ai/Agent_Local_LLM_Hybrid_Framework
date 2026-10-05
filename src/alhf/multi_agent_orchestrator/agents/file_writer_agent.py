# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides a simple file-writing agent used for
# Runtime V1 validation.
#
# Responsibilities:
# - Expose a capability.
# - Execute a task.
# - Create a visible artifact.
# - Return AgentResponse.
#
# Must Not:
# - Perform orchestration.
# - Perform scheduling.
# - Access workflow state.
# - Contain workflow logic.

from __future__ import annotations

from pathlib import Path

from alhf.multi_agent_orchestrator.contracts.agent_response import (
    AgentResponse,
)
from alhf.multi_agent_orchestrator.contracts.task_context import (
    TaskContext,
)
from alhf.multi_agent_orchestrator.interfaces.i_agent import (
    IAgent,
)


class FileWriterAgent(IAgent):
    """Runtime V1 file writer agent."""

    @property
    def agent_id(self) -> str:
        return "file-writer-agent"

    @property
    def capability(self) -> str:
        return "file_writer"

    async def execute(
        self,
        task_context: TaskContext,
    ) -> AgentResponse:
        output_directory = Path("output")

        output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_file = (
            output_directory
            / f"{task_context.task_id}.txt"
        )

        content = (
            "ALHF Runtime Validation\n"
            "=======================\n\n"
            f"Task Id: {task_context.task_id}\n"
            f"Workflow Id: {task_context.workflow_id}\n"
            f"Capability: {task_context.capability}\n\n"
            "FileWriterAgent executed successfully.\n"
        )

        output_file.write_text(
            content,
            encoding="utf-8",
        )

        return AgentResponse(
            status="SUCCESS",
            confidence=1.0,
            result={
                "output_file": str(output_file),
                "message": "File created successfully",
            },
            metadata={
                "agent_id": self.agent_id,
                "capability": self.capability,
            },
        )
