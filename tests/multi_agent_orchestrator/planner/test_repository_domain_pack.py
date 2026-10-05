# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Validate RepositoryDomainPack behavior.
#
# Responsibilities:
# - Validate supported intents.
# - Validate supported strategies.
# - Validate workflow templates.
#
# Must Not:
# - Test planner logic.
# - Test detector logic.
# - Test orchestration behavior.

from unittest import TestCase

from alhf.multi_agent_orchestrator.planner.domain_packs.repository_domain_pack import (
    RepositoryDomainPack,
)


class TestRepositoryDomainPack(TestCase):

    def test_supported_intents(self) -> None:
        pack = RepositoryDomainPack()

        self.assertIn(
            "repository_analysis",
            pack.supported_intents,
        )

        self.assertIn(
            "build_failure_analysis",
            pack.supported_intents,
        )

    def test_supported_strategies(self) -> None:
        pack = RepositoryDomainPack()

        self.assertIn(
            "root_cause_analysis",
            pack.supported_strategies,
        )

        self.assertIn(
            "repository_inspection",
            pack.supported_strategies,
        )

    def test_repository_analysis_template(self) -> None:
        pack = RepositoryDomainPack()

        self.assertEqual(
            "root_cause_analysis",
            pack.workflow_templates[
                "repository_analysis"
            ],
        )

    def test_build_failure_template(self) -> None:
        pack = RepositoryDomainPack()

        self.assertEqual(
            "root_cause_analysis",
            pack.workflow_templates[
                "build_failure_analysis"
            ],
        )

    def test_release_note_template(self) -> None:
        pack = RepositoryDomainPack()

        self.assertEqual(
            "release_note_generation",
            pack.workflow_templates[
                "release_note_generation"
            ],
        )
