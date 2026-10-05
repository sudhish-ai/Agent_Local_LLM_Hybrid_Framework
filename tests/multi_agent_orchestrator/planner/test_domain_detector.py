# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Validate DomainDetector behavior.
#
# Responsibilities:
# - Validate repository analysis domain detection.
# - Validate build failure domain detection.
# - Validate release note domain detection.
# - Validate test strategy domain detection.
# - Validate returned domain type.
#
# Must Not:
# - Test workflow generation.
# - Test orchestration behavior.
# - Test execution behavior.

from unittest import TestCase

from alhf.multi_agent_orchestrator.contracts.intent_definition import (
    IntentDefinition,
)
from alhf.multi_agent_orchestrator.planner.domain_detector import (
    DomainDetector,
)


class TestDomainDetector(TestCase):

    def setUp(
        self,
    ) -> None:
        self.detector = DomainDetector()

    def test_repository_analysis_domain(
        self,
    ) -> None:
        intent = IntentDefinition(
            intent="repository_analysis",
        )

        domain = self.detector.detect(
            intent,
        )

        self.assertEqual(
            "software_engineering",
            domain,
        )

    def test_build_failure_domain(
        self,
    ) -> None:
        intent = IntentDefinition(
            intent="build_failure_analysis",
        )

        domain = self.detector.detect(
            intent,
        )

        self.assertEqual(
            "software_engineering",
            domain,
        )

    def test_release_note_domain(
        self,
    ) -> None:
        intent = IntentDefinition(
            intent="release_note_generation",
        )

        domain = self.detector.detect(
            intent,
        )

        self.assertEqual(
            "software_engineering",
            domain,
        )

    def test_test_strategy_domain(
        self,
    ) -> None:
        intent = IntentDefinition(
            intent="test_strategy_generation",
        )

        domain = self.detector.detect(
            intent,
        )

        self.assertEqual(
            "software_engineering",
            domain,
        )

    def test_returns_string_domain(
        self,
    ) -> None:
        intent = IntentDefinition(
            intent="repository_analysis",
        )

        domain = self.detector.detect(
            intent,
        )

        self.assertIsInstance(
            domain,
            str,
        )
